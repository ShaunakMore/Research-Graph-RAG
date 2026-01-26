from fastapi import Body, HTTPException, FastAPI, UploadFile, File, Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from generation.hybrid_answer import ask_hybrid
from ingestion.ingest import ingest
from typing import Annotated
from pathlib import Path
import re
import requests
from jose import jwt
from jose.utils import base64url_decode
import os
from dotenv import load_dotenv
from huggingface_hub import HfApi
import io

load_dotenv()

app = FastAPI(title="Graph-RAG", version="1.0")

FRONTEND_URL = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api = HfApi()

# Clerk Configuration
CLERK_FRONTEND_API = os.getenv("CLERK_DOMAIN")  # Your Clerk domain
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")

# Hf dataset config
TOKEN = os.getenv("HF_TOKEN_WT")
REPO_ID = os.getenv("HF_DATASET_ID")

# Cache JWKS keys
_jwks_cache = None

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        response = requests.get(CLERK_JWKS_URL) #type:ignore
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache

def verify_clerk_token(authorization: str = Header(None)) -> str:
    """
    Verify Clerk JWT token and return user_id
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    
    try:
        # Get JWKS
        jwks = get_jwks()
        
        # Decode header to get kid (key id)
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the right key
        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=f"https://{CLERK_FRONTEND_API}",
            options={"verify_aud": False}  # Clerk tokens don't always have aud
        )
        
        # Get user_id from sub claim
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def upload_to_hf(content: bytes, user_id: str, paper_id: str):
    """
    Uploads bytes directly to the HF Dataset bucket.
    Automatically creates user folders via the path_in_repo.
    """
    # Define the path 
    path_in_repo = f"{user_id}/{paper_id}.pdf"
    
    # Upload directly from memory (no local disk needed)
    api.upload_file( 
        path_or_fileobj=io.BytesIO(content),
        path_in_repo=path_in_repo,
        repo_id=REPO_ID,
        repo_type="dataset",
        token=TOKEN
    )
    return path_in_repo

def get_user_pdf_names(user_id: str):
    """
    Returns a clean list of paper_ids for a specific user.
    Example: ['paper_123', 'intro_to_ai'] instead of ['user_id/paper_123.pdf']
    """
    # 1. Get the list of all files in the repo
    all_files = api.list_repo_files(repo_id=REPO_ID, repo_type="dataset", token=TOKEN)
    
    # 2. Filter for files in the user's folder and strip extensions
    user_papers = [
        f.split("/")[-1].replace(".pdf", "") 
        for f in all_files 
        if f.startswith(f"{user_id}/") and f.lower().endswith(".pdf")
    ]
    
    return user_papers

@app.get("/")
async def health_check():
    return {
        "message": "BACKEND SETUP SUCCESSFULL"
    }


@app.post("/query")
async def handle_query(
    prompt: Annotated[str | None, Body(..., embed=True)] = None,
    user_id: str = Depends(verify_clerk_token)
):
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Get papers for this specific user
    paper_list = get_user_pdf_names(user_id)
    if not paper_list:
        return {
            "message": "Please upload some documents first before asking questions."
        }
    
    llm_response = ask_hybrid(prompt, paper_list,user_id=user_id)
    if llm_response == "Gemini request failed":
        return {
            "message": "Error connecting with Gemini"
        }
    return {
        "message": f"{llm_response}"
    }


UPLOAD_DIR = Path("uploaded_papers")
UPLOAD_DIR.mkdir(exist_ok=True)



def normalize_paper_name(name: str) -> str:
    name = name.strip().lower()
    if not re.match(r"^[a-z0-9_]+$", name):
        raise ValueError(
            "Paper name must contain only lowercase letters, numbers, and underscores"
        )
    return name


@app.post("/upload")
async def upload_paper(
    file: UploadFile = File(...),
    paper_name: str = Form(...),
    user_id: str = Depends(verify_clerk_token)
):
    # 1️⃣ Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2️⃣ Validate and normalize paper name
    try:
        paper_id = normalize_paper_name(paper_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    content = await file.read()
    pdf_stream = io.BytesIO(content)
    pdf_upload_path = await upload_to_hf(content,user_id,paper_id)

    # 7️⃣ Process the document
    result_ingest = await ingest(pdf_stream, paper_id,user_id=user_id)

    return {
        "status": "success",
        "paper_id": paper_id,
        "filename": file.filename,
        "message": (
            f"Paper uploaded successfully. "
            f"Use '{paper_id}' to reference this paper in queries."
        )
    }


@app.get("/papers")
async def get_papers(user_id: str = Depends(verify_clerk_token)):
    # Return only papers for the authenticated user
    user_papers = get_user_pdf_names(user_id)
    
    return {
        "papers": [
            {
                "paper_id": paper_id,
                "filename": paper_id
            }
            for paper_id in user_papers
        ]
    }