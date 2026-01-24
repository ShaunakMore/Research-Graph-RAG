from fastapi import Body, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from generation.hybrid_answer import ask_hybrid
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

@app.get("/query")
async def handle_query(prompt: str = Body(...,embed=True)):
  if not prompt or not prompt.strip():
    raise HTTPException(status_code=400,detail="Prompt cannot be empty")

  llm_response = ask_hybrid(query=prompt)
  if(llm_response == "Gemini request failed"):
    return {
      "message":"Error connecting with Gemini"
    }
  return {
    "message": f"{llm_response}"
  }