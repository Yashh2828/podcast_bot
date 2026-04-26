# 🎙️ Podcast Gen - AI-Powered Podcast Script Generator

Generate realistic podcast scripts using RAG (Retrieval-Augmented Generation) and Hugging Face LLMs. Upload documents, extract topics, configure speakers, and get natural conversation scripts.

---

## ✨ Features

- 🤖 **AI-Powered Generation** - Uses Hugging Face LLMs for natural dialogue
- 📚 **RAG-Based Extraction** - Extracts topics from PDF, DOCX, and TXT files
- 🎯 **Topic Selection** - Choose which topics to include in your podcast
- ⚡ **Adjustable Speaking Speeds** - Control pacing for host and guest
- 🔄 **Regeneration** - Modify and regenerate scripts on the fly
- 🎨 **Modern Streamlit UI** - Beautiful, intuitive web interface

---

## 🚀 Setup Steps

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd "Podcast bot HF"
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the project root:
```bash
# Required - Get from https://huggingface.co/settings/tokens
HUGGINGFACE_API_TOKEN=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
```

Or set it in your terminal:
```bash
# Windows PowerShell
$env:HUGGINGFACE_API_TOKEN="your_token_here"

# Windows CMD
set HUGGINGFACE_API_TOKEN=your_token_here

# macOS/Linux
export HUGGINGFACE_API_TOKEN=your_token_here
```

---

## 🖥️ How to Run UI (Streamlit)

The recommended way to use the application:

### Step 1: Start the Backend
```bash
# From project root
uvicorn backend.app:app --reload --port 8000
```

### Step 2: Start the Frontend (New Terminal)
```bash
# From project root
streamlit run frontend/app.py
```

The UI will open automatically at `http://localhost:8501`

---

## 💻 How to Run via Terminal (Fallback)

If you prefer not using the UI, you can interact with the API directly:

### Start the Backend Server
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check if API is running |
| `/api/extract-topics` | POST | Upload files and extract topics |
| `/api/generate` | POST | Generate podcast script |
| `/api/regenerate` | POST | Regenerate with modifications |
| `/api/restart` | POST | Clear all data and restart |

### Example cURL Commands

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Extract Topics:**
```bash
curl -X POST "http://localhost:8000/api/extract-topics" \
  -F "files=@sample.pdf" \
  -F "files=@document.docx"
```

**Generate Script:**
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "host_name": "Sarah",
    "guest_name": "Dr. Johnson",
    "host_gender": "female",
    "guest_gender": "male",
    "host_speed": 100,
    "guest_speed": 110,
    "topics": ["AI Technology", "Machine Learning"],
    "duration": 15
  }'
```

---

## 🤖 LLM Used

| Component | Model | Provider |
|-----------|-------|----------|
| **LLM** | `mistralai/Mistral-7B-Instruct-v0.1` | Hugging Face |
| **Embeddings** | `all-MiniLM-L6-v2` | Hugging Face |

**Model Characteristics:**
- Fast inference with good quality output
- 7B parameters - efficient for most use cases
- Optimized for instruction-following
- Works well for conversational/dialogue generation

**Alternative models** (edit `backend/config.py`):
- `meta-llama/Llama-2-7b-chat-hf` - Good for conversations
- `microsoft/DialoGPT-medium` - Conversational focused

---

## 🔐 Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HUGGINGFACE_API_TOKEN` | ✅ Yes | Hugging Face API token for LLM access |
| `API_BASE_URL` | ❌ No | Backend URL (default: `http://localhost:8000`) |

**Getting your Hugging Face Token:**
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token (read access is sufficient)
3. Copy and paste into your `.env` file

---

## 📁 Project Structure

```
Podcast bot HF/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── config.py           # Configuration & env vars
│   ├── routes/
│   │   ├── topics.py       # Topic extraction endpoints
│   │   └── generate.py     # Script generation endpoints
│   ├── services/
│   │   ├── rag_pipeline.py # RAG & vectorstore logic
│   │   ├── script_service.py # LLM script generation
│   │   └── topic_service.py # Topic extraction
│   └── utils/
│       ├── chunking.py     # Document chunking
│       └── loaders.py      # File loaders (PDF, DOCX, TXT)
├── frontend/
│   └── app.py              # Streamlit UI
├── data/uploads/           # Uploaded documents storage
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

---

## 🌐 Deployment

### Backend on Render
1. Push code to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `HUGGINGFACE_API_TOKEN`

### Frontend on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Deploy `frontend/app.py`
3. Add secret: `API_BASE_URL = "https://your-render-url.onrender.com"`

---

## 📄 Sample Output

See [`sample_output.md`](sample_output.md) for a generated podcast script example.

---

## 🛠️ Troubleshooting

**Backend won't start:**
- Check `HUGGINGFACE_API_TOKEN` is set correctly
- Verify port 8000 is not in use

**Frontend can't connect:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app.py`

**Out of memory:**
- The LLM model requires ~4GB RAM minimum
- Consider using a smaller model in `backend/config.py`

---

## 📜 License

MIT License - Feel free to use and modify!

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.
