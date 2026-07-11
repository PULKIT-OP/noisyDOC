# noisyDOC - PDF Chat App with RAG

noisyDOC is a full-stack document chat application where users can upload PDFs/documents and ask questions about them.

The project uses:

- Node.js + Express + EJS for web UI, auth, and upload APIs
- Python FastAPI for RAG ingestion/query
- FAISS + Sentence Transformers for vector search
- Groq LLM for final answer generation
- MongoDB for users and uploaded PDF metadata

## Key points to keep in mind before testing the project

- Each uploaded PDF now gets its own persisted FAISS store under `rag/faiss_store/documents/<pdf_id>`.
- You can reopen a saved PDF from the "My PDFs" page and continue chatting without reuploading it.
- The chat flow still uses the selected document id so questions are answered from the correct document.
- Just keep one thing in mind while chatting with your doc, it cannot remember what you asked it before so please try to complete one question in one text do not break it in multiple texts like we do in whatsapp.
- for example: query 1 : what is democracy in India? 
               response 1 : 85% blended ethanol still fuel prices are not down.

               query 2 : what are its advantages?
               response 2 will not get generated for this query because it doesnot know what did you ask before.
- Instead you should do this --->
               query 1 : what is democracy in India? what are its advantages if it exist?

## Features

- User signup/login with JWT cookie auth
- Upload PDF/TXT/DOC files from chat screen
- Automatic ingestion into a per-document vector store after upload
- Re-open previously uploaded documents from the library page
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

### Run separately (Not Recommended)

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
3. Express stores file metadata in MongoDB, creates a PDF record, and forwards the file plus `pdfId` to FastAPI `/ingest`.
4. FastAPI loads text, chunks content, creates embeddings, and saves the FAISS index for that specific PDF id.
5. User can later open the same PDF from "My PDFs" without uploading again.
6. User asks a question.
7. Express forwards question and `pdfId` to FastAPI `/query`.
8. FastAPI loads the matching FAISS index, retrieves relevant chunks, and sends context to Groq LLM.
9. Final answer is returned to chat UI.

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
- `POST /ingest` ingest uploaded file for a specific document id
- `POST /query` ask question over a specific document vector store

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

- FAISS indexes are still stored locally on the machine running the app.
- If the server is lost, the FAISS folders need to be backed up or restored separately.

## Future Improvements

- Move FAISS persistence to cloud storage or a managed vector DB if the project grows
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

- Cloud-backed FAISS persistence or managed vector DB migration
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
