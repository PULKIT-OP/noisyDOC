from data_loaders import load_all_documents, load_document
from vectorstore import FaissVectorStore
from search import RAGSearch
import os

def _document_store_dir(document_id: str) -> str:
    return FaissVectorStore.make_persist_dir("faiss_store", document_id)

def run_ingest(file_path: str, document_id: str):
    docs = load_document(file_path)
    if not docs:
        return False
    store = FaissVectorStore(_document_store_dir(document_id))
    store.build_from_documents(docs)
    return True

def run_query(question: str, document_id: str, top_k: int = 3):
    store_dir = _document_store_dir(document_id)
    faiss_path = os.path.join(store_dir, "faiss.index")
    meta_path = os.path.join(store_dir, "metadata.pkl")
    if not os.path.exists(faiss_path) or not os.path.exists(meta_path):
        return "No saved document index found for that document. Upload the PDF again to create it."

    rag_search = RAGSearch(persist_dir=store_dir, load_from_data=False)
    summary = rag_search.search_and_summarize(question, top_k=max(top_k, 8), min_score=0.2)
    return summary