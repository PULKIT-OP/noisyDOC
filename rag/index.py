# rag/app.py  — NEW FILE (your FastAPI server)
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os

# import YOUR existing logic
from pipeline import run_ingest, run_query  # we'll add these 2 functions

app = FastAPI()

# allow Node.js to call this server (like CORS in Express)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request body shapes (like req.body in Express) ───
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

# ─── ROUTES ───────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "RAG service running"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    # save uploaded file to data/pdf/
    save_path = f"../data/pdf/{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # run your existing pipeline on it
    result = run_ingest(save_path)
    return {"message": "Document ingested", "file": file.filename}

@app.post("/query")
def query(body: QueryRequest):
    answer = run_query(body.question, body.top_k)
    return {"answer": answer}