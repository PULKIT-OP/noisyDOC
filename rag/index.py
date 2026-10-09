# rag/app.py  — NEW FILE (your FastAPI server)
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os
from threading import Lock

# import YOUR existing logic
from pipeline import run_ingest, run_query  # we'll add these 2 functions

app = FastAPI()
ingest_statuses = {}
status_lock = Lock()


def update_ingest_status(token, progress, message, status="processing"):
    if token:
        with status_lock:
            ingest_statuses[token] = {
                "status": status,
                "progress": progress,
                "message": message,
            }

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
async def ingest(
    file: UploadFile = File(...),
    pdf_id: str = Form(...),
    progress_token: str = Form(""),
):
    # save uploaded file to data/pdf/
    _, ext = os.path.splitext(file.filename)
    os.makedirs("../data/pdf", exist_ok=True)
    save_path = f"../data/pdf/{pdf_id}{ext or ''}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # run existing pipeline on it
    update_ingest_status(progress_token, 28, "Reading document...")
    result = run_ingest(
        save_path,
        pdf_id,
        progress_callback=lambda progress, message: update_ingest_status(
            progress_token, progress, message
        ),
    )
    if not result:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Document ingestion failed",
                "file": file.filename,
            },
        )
    update_ingest_status(progress_token, 100, "Document is ready to chat with.", "complete")
    return {"message": "Document ingested", "file": file.filename}


@app.get("/status/{progress_token}")
def ingest_status(progress_token: str):
    return ingest_statuses.get(
        progress_token,
        {"status": "processing", "progress": 25, "message": "Preparing document..."},
    )

@app.post("/query")
def query(body: QueryRequest):
    answer = run_query(body.question, body.pdf_id, body.top_k)
    return {"answer": answer}