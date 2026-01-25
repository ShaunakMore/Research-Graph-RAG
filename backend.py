from fastapi import Body, HTTPException, FastAPI, UploadFile, File, Form, Header, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from generation.hybrid_answer import ask_hybrid
from ingestion.ingest import ingest
from typing import Annotated
from pathlib import Path
import shutil
import re
import requests
from jose import jwt, jwk
from jose.utils import base64url_decode
import json,os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Graph-RAG", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clerk Configuration
CLERK_FRONTEND_API = os.getenv("VITE_CLERK_DOMAIN")  # Your Clerk domain
CLERK_JWKS_URL = os.getenv("VITE_CLERK_JWKS_URL")

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
    paper_store = UPLOAD_DIR / user_id
    if not paper_store.exists():
        return {
            "message": "Please upload some documents first before asking questions."
        }
    
    papers = list(paper_store.iterdir())
    paper_list = [i.name for i in papers]
    
    if not paper_list:
        return {
            "message": "You haven't uploaded any papers yet. Upload some documents to get started!"
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

# Store papers per user: {user_id: {paper_id: {...}}}
PAPER_REGISTRY = {}


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

    # 3️⃣ Initialize user's registry if needed
    if user_id not in PAPER_REGISTRY:
        PAPER_REGISTRY[user_id] = {}

    # 4️⃣ Ensure uniqueness for this user
    if paper_id in PAPER_REGISTRY[user_id]:
        raise HTTPException(
            status_code=400,
            detail=f"Paper name '{paper_id}' already exists"
        )

    # 5️⃣ Create user-specific directory
    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    
    paper_dir = user_dir / paper_id
    paper_dir.mkdir(exist_ok=False)

    pdf_path = paper_dir / file.filename

    # 6️⃣ Save PDF
    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 7️⃣ Process the document
    result_ingest = await ingest(pdf_path, paper_id,user_id=user_id)

    # 8️⃣ Register paper for this user
    PAPER_REGISTRY[user_id][paper_id] = {
        "paper_id": paper_id,
        "filename": file.filename,
        "path": str(pdf_path),
    }

    print(result_ingest)

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
    user_papers = PAPER_REGISTRY.get(user_id, {})
    
    return {
        "papers": [
            {
                "paper_id": paper_id,
                "filename": info["filename"]
            }
            for paper_id, info in user_papers.items()
        ]
    }