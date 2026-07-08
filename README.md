# noisyDOC - PDF Chat App with RAG

noisyDOC is a full-stack document chat application where users can upload PDFs/documents and ask questions about them.

The project uses:

- Node.js + Express + EJS for web UI, auth, and upload APIs
- Python FastAPI for RAG ingestion/query
- FAISS + Sentence Transformers for vector search
- Groq LLM for final answer generation
- MongoDB for users and uploaded PDF metadata

## Key points to keep in mind before testing the project

- It uses a shared FAISS vector store, which simply means all the documents that you will upload will be indexed in same file 
- So while you are chatting with you doc PLEASE specify the doc name for each query.
- For example: from the document testing.pdf tell me in short who the fuck is Narendra Modi?
- If you donot specify the document then it might give wrong answer or tell you it doesnot have any context about your query.

## Features

- User signup/login with JWT cookie auth
- Upload PDF/TXT/DOC files from chat screen
- Automatic ingestion into vector store after upload
- Chat-style Q&A over uploaded content
- My PDFs page for uploaded document history
- Retrieval fallback improvements for better recall on specific terms


## Project Structure

```text
noisyDOC/
	backend/       # Express app, auth, uploads, Mongo models, API routes
	rag/           # FastAPI app, loaders, embeddings, vectorstore, search pipeline
	frontend/      # EJS views + CSS + client-side script
	data/          # Shared document storage used by RAG service
```

## Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB running locally (default: mongodb://127.0.0.1:27017/pdf-chat-app)
- pip (or virtualenv + pip)

## Environment Variables

Create a `.env` file in project root (`noisyDOC/.env`) with:

```env
GROQ_API_KEY=your_groq_key_here
JWT_SECRET=your_jwt_secret_here
RAG_SERVICE_URL=http://localhost:8000 (optional)
```

Notes:

- `RAG_SERVICE_URL` is optional but recommended.
- Groq key is used by the Python RAG service for answer generation.

## Installation

### 1) Clone the repository

```bash
git clone https://github.com/PULKIT-OP/noisyDOC
cd RAG_PROJECT
```

### 2) Install backend dependencies

```bash
cd backend
npm install
```

### 3) Install Python dependencies

```bash
cd ../rag
(next two commands are optional)
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the App

### Recommended: run both services together

```bash
cd backend
npm run dev:all
```

This starts:

- Express server on `http://localhost:3000`
- FastAPI RAG server on `http://127.0.0.1:8000`

### Run separately (optional) (dont use it, its shit)

Backend:

```bash
cd backend
npm run dev
```

RAG service:

```bash
cd rag
uvicorn index:app --reload --port 8000
```

## Main App Flow

1. User logs in.
2. User uploads a file from chat page.
3. Express stores file metadata in MongoDB and forwards file to FastAPI `/ingest`.
4. FastAPI loads text, chunks content, creates embeddings, and updates FAISS store.
5. User asks a question.
6. Express forwards question to FastAPI `/query`.
7. FastAPI retrieves relevant chunks and sends context to Groq LLM.
8. Final answer is returned to chat UI.

## Key Endpoints

### Express (Node)

- `POST /user/signup`
- `POST /user/login`
- `GET /my-pdfs`
- `GET /my-pdfs-data`
- `POST /chat/upload`
- `POST /chat`

### FastAPI (Python)

- `GET /` health check
- `POST /ingest` ingest uploaded file
- `POST /query` ask question over vector store

## Scripts

From `backend/package.json`:

- `npm run start` - run Express in normal mode
- `npm run dev` - run Express with nodemon
- `npm run dev:rag` - run FastAPI with reload
- `npm run dev:all` - run Express + FastAPI concurrently

## Troubleshooting

### "No relevant documents found"

Possible reasons:

- Query terms are not in top retrieved chunks.
- Text extraction/chunking split important terms.
- Very strict score filtering.

What helps:

- Re-upload and re-query once ingestion is complete.
- Ask with explicit keywords from the document.
- Ensure both backend and RAG services are running.

### MongoDB connection error

- Verify local MongoDB is running.
- Check URI in backend connection config.

### RAG service not reachable

- Confirm FastAPI is running on port `8000`.
- Verify `RAG_SERVICE_URL` in `.env`.

### Missing Groq key

- Set `GROQ_API_KEY` in root `.env`.
- Restart services after updating env values.

## Current Limitations

- Retrieval currently uses a shared FAISS store for all uploaded documents.
- Per-document isolated chat can be added by storing separate indexes or filtering by document metadata.

## Future Improvements

- Per-document vector stores (or metadata-filtered retrieval)
- Better citation/source snippet display in responses
- Hybrid retrieval (semantic + keyword/BM25)
- File delete and index cleanup flow

## Open for Contributions

We welcome contributions from the community! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test thoroughly
4. **Commit with clear messages**:
   ```bash
   git commit -m "Add: description of your changes"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** with a clear description of your changes

### Areas We'd Love Help With

- Per-document vector stores (isolated chat per document)
- Better citation and source snippet display
- Hybrid retrieval (semantic + keyword/BM25)
- File delete and index cleanup functionality
- UI/UX improvements
- Documentation and tutorials
- Bug fixes and performance improvements

### Code Guidelines

- Follow existing code style and conventions
- Write clear, descriptive commit messages
- Test your changes before submitting a PR
- Update documentation if needed
- Keep PRs focused on a single feature or fix
- Do not make multiple features in one PR PLEASE

### Questions or Ideas?

Feel free to open an issue to discuss ideas, report bugs, or ask questions. We're here to help!
