# Quick Start Guide - noisyDOC

Get noisyDOC up and running in just a few minutes!

## Prerequisites

Before you begin, make sure you have:

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.10+** - [Download here](https://www.python.org/)
- **MongoDB** - Running locally on `mongodb://127.0.0.1:27017/pdf-chat-app`
- **Groq API Key** - Get one free from [Groq Console](https://console.groq.com)

## Step 1: Clone the Repository

```bash
git clone https://github.com/PULKIT-OP/noisyDOC
cd noisyDOC
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the project root (`RAG_PROJECT/.env`):

```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET=your_super_secret_jwt_key_here
RAG_SERVICE_URL=http://localhost:8000 (optioanl)
```

**How to get Groq API Key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Create an API key
4. Copy and paste it into your `.env` file

## Step 3: Install Dependencies

### Backend (Node.js)

```bash
cd backend
npm install
```

### RAG Service (Python)

```bash
cd ../rag
python -m venv .venv (optional or dont do it)

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1 (optional or dont do it)

# On macOS/Linux:
source .venv/bin/activate (optional or dont do it)

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Start the Application

From the `backend` directory, run:

```bash
npm run dev:all
```

This will start both services:
- **Express Server**: http://localhost:3000
- **FastAPI RAG Server**: http://127.0.0.1:8000

You should see output like:
```
[nodemon] restarting due to changes...
[nodemon] starting `node index.js`
Express server running on port 3000
FastAPI server running on port 8000
```

## Step 5: Open the App

1. Open your browser
2. Go to **http://localhost:3000**
3. Click **Sign Up** and create an account
4. You're ready to go! 🎉

## Step 6: Upload & Chat

1. **Upload a PDF:**
   - Click the upload button on the chat page
   - Select a PDF file from your computer
   - Wait for the ingestion to complete

2. **Ask Questions:**
   - Type your question in the chat box
   - **Important:** Always mention the document name in your query
   - Example: `"From my_document.pdf, Does GOD exist?"`
   - Press Enter to get your answer

## Troubleshooting

### "Cannot connect to MongoDB"
- Make sure MongoDB is running locally
- Check that it's on `mongodb://127.0.0.1:27017`
- On Windows, you can start MongoDB with: `mongod`

### "RAG service not reachable"
- Verify FastAPI is running on port 8000
- Check your `.env` file has `RAG_SERVICE_URL=http://localhost:8000`
- Restart both services

### "No relevant documents found"
- Make sure you mentioned the document name in your query
- Try re-uploading the document
- Use specific keywords from the document

### "GROQ_API_KEY not found"
- Verify your `.env` file is in the project root
- Make sure the key is correctly set
- Restart the services after updating `.env`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [Project Structure](README.md#project-structure)
- Explore the [API Endpoints](README.md#key-endpoints)
- See [Future Improvements](README.md#future-improvements) for planned features

## Need Help?

If you run into issues:
1. Check the [Troubleshooting](README.md#troubleshooting) section in README.md
2. Make sure all prerequisites are installed
3. Verify all environment variables are set correctly
4. Check that both MongoDB and services are running

Happy chatting! 🚀