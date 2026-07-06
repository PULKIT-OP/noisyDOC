# noisyDOC — UI Specification
 
## Pages Overview
 
| Page | Route | Auth Required |
|------|-------|---------------|
| Home | `/` | No |
| Signup | `/signup` | No |
| Login | `/login` | No |
| My PDFs | `/my-pdfs` | Yes |
| New PDF + Chat | `/chat` | Yes |
 
---
 
## 1. Home Page (`/`)
 
**Navbar:**
- Top left: App name — `noisyDOC`
- Top right: `Signup` | `Login` links
**Body:**
- Center of screen: Heading — *"Talk with your Doc"*
- Clicking it redirects to `/login`
---
 
## 2. Signup Page (`/signup`)
 
**Form fields:**
- Name
- Email
- Password
**Behaviour:**
- On success → redirect to `/login`
---
 
## 3. Login Page (`/login`)
 
**Form fields:**
- Email
- Password
**Behaviour:**
- On success → JWT cookie is set
- Redirect to home page `/`
---
 
## 4. Logged-in State (all pages)
 
**Navbar (when user is logged in):**
- Top left: `noisyDOC`
- Center: `My PDFs` | `New PDF`
- Top right: `[User's Name] ▾` (dropdown)
  - Dropdown item: `Logout`
---
 
## 5. My PDFs Page (`/my-pdfs`)
 
**Behaviour:**
- Fetches all PDFs uploaded by the logged-in user from MongoDB
- Displays a list/grid of uploaded documents with:
  - File name
  - Upload date
---
 
## 6. New PDF + Chat Page (`/chat`)
 
**Step 1 — Upload Form:**
- File input: accepts `.pdf`, `.txt`, `.doc`
- Submit button: `Upload & Start Chat`
- On submit:
  - `POST /chat/upload` with `form-data`
  - File saved to `uploads/` folder
  - Metadata saved to MongoDB
  - Vectors ingested into FAISS via Python RAG service
  - On success → chat window opens
**Step 2 — Chat Window (WebSocket):**
- Connects to Node.js via `socket.io`
- UI layout:
```
  ┌─────────────────────────────────┐
  │  📄 filename.pdf                │
  ├─────────────────────────────────┤
  │                                 │
  │  🤖 Document uploaded! Ask me   │
  │     anything about it.          │
  │                                 │
  │  👤 What is this about?         │
  │                                 │
  │  🤖 This document is about...   │
  │                                 │
  ├─────────────────────────────────┤
  │  Type your question...  [Send]  │
  └─────────────────────────────────┘
```
 
**Socket events:**
| Event | Direction | Payload |
|-------|-----------|---------|
| `chat_message` | Client → Server | `{ question: "..." }` |
| `chat_response` | Server → Client | `{ answer: "..." }` |
 
---
 
## Full User Flow
 
```
Home Page
   │
   ▼ click "Talk with your Doc"
Login Page  ←──── Signup Page
   │
   ▼ login success (JWT cookie set)
Home Page (logged in)
   │
   ├── My PDFs → list of uploaded docs
   │
   └── New PDF
          │
          ▼ upload PDF
       Chat Window (WebSocket)
          │
          ▼ ask question
       RAG Answer (via Python FastAPI)
```
 
---
 
## Tech Stack Per Layer
 
| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, Vanilla JS, Socket.io client |
| Backend API | Node.js, Express.js, JWT, Multer, Socket.io |
| RAG Service | Python, FastAPI, LangChain, FAISS |
| Database | MongoDB (metadata), FAISS local store (vectors) |
| Auth | JWT via HTTP-only cookie |