# rag/app.py  — NEW FILE (your FastAPI server)
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os

# import YOUR existing logic
from pipeline import run_ingest, run_query  # we'll add these 2 functions

app = FastAPI()

# allow Node.js to call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body shapes (like req.body in Express)
class QueryRequest(BaseModel):
    question: str
    pdf_id: str
    top_k: int = 3

# ROUTES

@app.get("/")
def health_check():
    return {"status": "RAG service running"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...), pdf_id: str = Form(...)):
    # save uploaded file to data/pdf/
    _, ext = os.path.splitext(file.filename)
    os.makedirs("../data/pdf", exist_ok=True)
    save_path = f"../data/pdf/{pdf_id}{ext or ''}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # run existing pipeline on it
    result = run_ingest(save_path, pdf_id)
    if not result:
        return {"message": "Document ingestion failed", "file": file.filename}
    return {"message": "Document ingested", "file": file.filename}

@app.post("/query")
def query(body: QueryRequest):
    answer = run_query(body.question, body.pdf_id, body.top_k)
    return {"answer": answer}