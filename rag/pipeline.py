from data_loaders import load_all_documents
from vectorstore import FaissVectorStore
from search import RAGSearch

store = FaissVectorStore("faiss_store")  # global, loaded once on startup
rag_search = RAGSearch()

def run_ingest(file_path: str):
    docs = load_all_documents("../data")   # or just the single file
    store.build_from_documents(docs)
    store.load()
    return True

def run_query(question: str, top_k: int = 3):
    summary = rag_search.search_and_summarize(question, top_k=top_k, min_score=0.5)
    return summary