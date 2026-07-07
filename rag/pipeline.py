from data_loaders import load_all_documents, load_document
from vectorstore import FaissVectorStore
from search import RAGSearch
import os

# Initialize global vector store
store = FaissVectorStore("faiss_store")  # global, loaded once on startup

# Load existing store or build from initial data on first startup
faiss_path = os.path.join("faiss_store", "faiss.index")
meta_path = os.path.join("faiss_store", "metadata.pkl")
if os.path.exists(faiss_path) and os.path.exists(meta_path):
    store.load()
else:
    docs = load_all_documents("data")
    if docs:
        store.build_from_documents(docs)
    else:
        print("[INFO] No initial documents found in data folder. Vector store ready for ingestion.")

rag_search = RAGSearch()

def run_ingest(file_path: str):
    docs = load_document(file_path)
    if not docs:
        return False
    # Add each document to existing vector store instead of rebuilding
    for doc in docs:
        store.add_document(doc)
    return True

def run_query(question: str, top_k: int = 3):
    summary = rag_search.search_and_summarize(question, top_k=top_k, min_score=0.5)
    return summary