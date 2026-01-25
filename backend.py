from fastapi import Body, HTTPException, FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from generation.hybrid_answer import ask_hybrid
from ingestion.ingest import ingest
from typing import Annotated
from pathlib import Path
import shutil
import re

app = FastAPI(title="Graph-RAG",version="1.0")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Configure this properly in production
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

  

@app.get("/")
async def health_check():
  return {
    "message": "BACKEND SETUP SUCCESSFULL"
  }

@app.post("/query")
async def handle_query(prompt: Annotated[str | None ,Body(...,embed=True)] = None):
  if not prompt or not prompt.strip():
    raise HTTPException(status_code=400,detail="Prompt cannot be empty")

  # llm_response = ask_hybrid(query=prompt)
  paper_store = UPLOAD_DIR
  papers = list(paper_store.iterdir())
  paper_list = [i.name for i in papers]
  
  llm_response = ask_hybrid(prompt)
  if(llm_response == "Gemini request failed"):
    return {
      "message":"Error connecting with Gemini"
    }
  return {
    "message": f"{llm_response}"
  }
  

UPLOAD_DIR = Path("uploaded_papers")
UPLOAD_DIR.mkdir(exist_ok=True)

# simple in-memory registry for now
# later you can persist this (DB / JSON / Neo4j)
PAPER_REGISTRY = {}

def normalize_paper_name(name: str) -> str:
    name = name.strip().lower()
    if not re.match(r"^[a-z0-9_]+$", name):
        raise ValueError(
            "Paper name must contain only lowercase letters, numbers, and underscores"
        )
    return name


@app.post("/upload")
async def upload_paper(file: UploadFile = File(...), paper_name: str = Form(...)):
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

    # 3️⃣ Ensure uniqueness
    if paper_id in PAPER_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Paper name '{paper_id}' already exists"
        )

    # 4️⃣ Save PDF to disk
    paper_dir = UPLOAD_DIR / paper_id
    paper_dir.mkdir(exist_ok=False)

    pdf_path = paper_dir / file.filename
        
    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result_ingest = await ingest(pdf_path,paper_id)
    
    # 5️⃣ Register paper
    PAPER_REGISTRY[paper_id] = {
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
async def get_papers():
    return {
        "papers": [
            {
                "paper_id": paper_id,
                "filename": info["filename"]
            }
            for paper_id, info in PAPER_REGISTRY.items()
        ]
    }
  