import os
from dotenv import load_dotenv
from vectorstore import FaissVectorStore
from langchain_groq import ChatGroq
from embeddings import get_embedding_model

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "llama-3.3-70b-versatile"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if os.path.exists(faiss_path) and os.path.exists(meta_path):
            self.vectorstore.load()
        else:
            from data_loaders import load_all_documents
            docs = load_all_documents("data")
            if docs:  # Only build if we have documents
                self.vectorstore.build_from_documents(docs)
            else:
                print("[INFO] No initial documents found. Vector store will be empty until documents are ingested.")
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 10, min_score: float = 0.1) -> str:
        results = self.vectorstore.query(query, top_k=top_k)
        if not results:
            return "\nNo documents in the vector store. Please upload a document first."
        # Filter results: convert distance to similarity (lower distance = higher similarity)
        # similarity = 1 / (1 + distance)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"] and (1 / (1 + r["distance"])) >= min_score]
        context = "\n\n".join(texts)
        if not context:
            return "\nNo relevant documents found."
        prompt = f"""You are a helpful assistant. Answer the question using the provided context.
                    If the context contains the answer, provide a detailed response based on the context.
                    If the context does not contain the answer, say: "The provided context does not contain enough information to answer this question."

                    Context:
                    {context}

                    Question: {query}

                    Answer:"""
        response = self.llm.invoke([prompt])
        return response.content

# Example usage
if __name__ == "__main__":
    rag_search = RAGSearch()
    query = "What is attention mechanism?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)
