# Podcast Script Generation System - Backend

Production-ready FastAPI backend for generating podcast scripts using RAG with Hugging Face LLM API.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Create a `.env` file in the project root
   - Add your Hugging Face API token:
     ```
     HUGGINGFACE_API_TOKEN=your_huggingface_api_token_here
     ```
   - Get your token from: https://huggingface.co/settings/tokens

3. **Run the server:**
   ```bash
   uvicorn backend.app:app --reload
   ```

4. **Access API:**
   - Swagger UI: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

---

## Configuration

The LLM model can be changed in `backend/config.py`:
- `mistralai/Mistral-7B-Instruct-v0.1` (recommended - fast & good quality)
- `meta-llama/Llama-2-7b-chat-hf` (good for conversations)
- `HuggingFaceH4/zephyr-7b-beta` (balanced performance)

---

## API Endpoints

### 1. Extract Topics
**POST** `/api/extract-topics`

Upload documents and extract topics for podcast discussion.

**Request:**
- Form: `files` (multipart) - PDF, DOCX, or TXT files

**Response:**
```json
{
  "topics": [
    "Topic 1",
    "Topic 2",
    "..."
  ]
}
```

**Error Cases:**
- No files uploaded → 400 Bad Request
- Unsupported format → 400 Bad Request
- Empty file content → 400 Bad Request

---

### 2. Generate Script
**POST** `/api/generate`

Generate a podcast script based on parameters.

**Request:**
```json
{
  "host_name": "John",
  "guest_name": "Jane",
  "host_gender": "male",
  "guest_gender": "female",
  "host_speed": "normal",
  "guest_speed": "fast",
  "topics": ["Topic 1", "Topic 2"],
  "duration": 30
}
```

**Field Requirements:**
- `host_name`, `guest_name`: Non-empty strings
- `host_gender`, `guest_gender`: "male", "female", or "other"
- `host_speed`, `guest_speed`: "slow", "normal", or "fast"
- `topics`: List with at least 1 topic
- `duration`: Integer between 1-180 (minutes)

**Response:**
```json
{
  "script": "[HOST]: Opening dialogue\n[GUEST]: Response\n...",
  "metadata": {
    "word_count": 4500,
    "duration_minutes": 30,
    "topics_used": ["Topic 1", "Topic 2"]
  }
}
```

---

## System Flow

1. **Upload Documents** → `/api/extract-topics`
   - Upload PDFs, DOCX, or TXT files
   - Documents are chunked and stored in FAISS vectorstore
   - Topics are extracted from documents

2. **Select Topics** → Choose from extracted topics

3. **Generate Script** → `/api/generate`
   - Provide podcast parameters
   - LLM retrieves relevant context from vectorstore
   - Generates realistic conversational script

4. **Regenerate** → Call `/api/generate` again with different parameters

---

## Architecture

- **LLM**: ChatGoogleGenerativeAI (Gemini 1.5 Flash)
- **Embeddings**: GoogleGenerativeAIEmbeddings
- **Vector DB**: FAISS (local storage)
- **Document Loaders**: PyPDFLoader, docx2txt, TextLoader
- **Chunking**: RecursiveCharacterTextSplitter (chunk_size=500, overlap=100)

---

## Key Features

✅ **Multi-format document support** - PDF, DOCX, TXT
✅ **RAG-based context retrieval** - Relevant background information
✅ **Natural script generation** - Realistic conversational dialogue
✅ **Topic validation** - Ensures topic consistency
✅ **Error handling** - Clear JSON error responses
✅ **CORS enabled** - Ready for frontend integration
✅ **Production-ready** - Clean, modular, scalable code

---

## Project Structure

```
backend/
├── app.py                    # FastAPI app entry point
├── config.py                 # Configuration & environment
├── models/
│   └── request_models.py    # Pydantic request schemas
├── routes/
│   ├── topics.py            # Topic extraction endpoint
│   └── generate.py          # Script generation endpoint
├── services/
│   ├── rag_pipeline.py      # FAISS vectorstore management
│   ├── topic_service.py     # Topic extraction logic
│   └── script_service.py    # Script generation logic
└── utils/
    ├── loaders.py           # Document loading utilities
    └── chunking.py          # Document chunking utilities
```

---

## Notes

- FAISS vectorstore is stored locally at `backend/vectorstore/db`
- Uploaded files are saved to `data/uploads/`
- Scripts target ~150 words per minute (word_count = duration × 150)
- Natural filler words (um, hmm, you know, like) are included for realism
