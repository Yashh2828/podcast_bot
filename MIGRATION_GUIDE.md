# Migration Guide: Gemini → Hugging Face

## Summary of Changes

Your Podcast Bot has been successfully converted from **Google Generative AI (Gemini)** to **Hugging Face LLM API**. This guide explains the changes and how to set up your new environment.

---

## What Changed

### 1. **Dependencies**
- ❌ Removed: `langchain-google-genai`
- ✅ Added: `langchain-huggingface`, `huggingface-hub`

### 2. **LLM Provider**
- ❌ Old: Google Generative AI (Gemini 2.5 Flash)
- ✅ New: Hugging Face Inference API (Mistral 7B Instruct by default)

### 3. **Configuration Changes**

#### Before (Google):
```python
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "models/gemini-2.5-flash"
```

#### After (Hugging Face):
```python
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
```

### 4. **Code Updates**

#### Before (Google):
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0.8
)
response = llm.invoke(prompt)
return response.content
```

#### After (Hugging Face):
```python
from langchain_huggingface import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id=LLM_MODEL,
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    temperature=0.8,
    max_new_tokens=2048
)
response = llm.invoke(prompt)
return response.strip()
```

---

## Setup Instructions

### Step 1: Get Hugging Face API Token

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "Podcast Bot")
4. Select **Read** permission (minimum required)
5. Click "Generate"
6. Copy the token

### Step 2: Update Environment Variables

Create or update your `.env` file:

```bash
# Copy from .env.example
cp .env.example .env

# Edit .env and add your token
HUGGINGFACE_API_TOKEN=hf_your_token_here
```

Or manually create `.env`:
```env
HUGGINGFACE_API_TOKEN=hf_your_token_here
HUGGINGFACE_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Backend

```bash
uvicorn backend.app:app --reload
```

---

## Available Models

You can change the LLM model by editing `backend/config.py`:

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `mistralai/Mistral-7B-Instruct-v0.1` | ⚡ Fast | ⭐⭐⭐⭐ | **Recommended** - Balanced |
| `meta-llama/Llama-2-7b-chat-hf` | ⚡ Fast | ⭐⭐⭐ | Conversations |
| `HuggingFaceH4/zephyr-7b-beta` | ⚡ Medium | ⭐⭐⭐⭐ | Better quality |
| `meta-llama/Llama-2-13b-chat-hf` | 🐌 Slower | ⭐⭐⭐⭐⭐ | Higher quality (slower) |

To change the model:

```python
# In backend/config.py
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
```

---

## Key Differences

### Response Format
- **Google**: Returns `ChatMessage` object with `.content` attribute
- **Hugging Face**: Returns string directly (use `.strip()` to clean)

### Token Limits
- **Google**: Handles long responses automatically
- **Hugging Face**: Use `max_new_tokens` parameter (set to 2048 in config)

### Rate Limiting
- **Google**: Generous free tier
- **Hugging Face**: API tier dependent, check [pricing](https://huggingface.co/pricing)

### Cost
- **Google**: Gemini 2 Flash - $0.075 per 1M input tokens
- **Hugging Face**: Free tier available with rate limits

---

## Troubleshooting

### Error: "HUGGINGFACE_API_TOKEN not found"
- Check `.env` file exists in project root
- Verify token is correctly set: `HUGGINGFACE_API_TOKEN=hf_xxxxx`
- Restart the server after updating `.env`

### Error: "Failed to authenticate"
- Token might be expired or invalid
- Generate a new token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Ensure token has **Read** permission

### Slow responses
- Model might be loading for first time (creates cache)
- Consider switching to faster model (Mistral 7B)
- Check Hugging Face API status

### Generation quality issues
- Adjust `temperature` in config (0-1, higher = more creative)
- Increase `max_new_tokens` for longer responses
- Try different model from available options

---

## Files Modified

- ✏️ `backend/config.py` - Updated to use Hugging Face token
- ✏️ `backend/services/script_service.py` - Uses `HuggingFaceEndpoint`
- ✏️ `backend/services/topic_service.py` - Uses `HuggingFaceEndpoint`
- ✏️ `requirements.txt` - Updated dependencies
- ✏️ `.env.example` - Updated configuration template
- ✏️ `BACKEND_SETUP.md` - Updated setup instructions

---

## No Changes Needed

These components remain unchanged:
- ✅ Vector store (FAISS)
- ✅ Embeddings (SentenceTransformer)
- ✅ RAG pipeline
- ✅ FastAPI routes
- ✅ Frontend

---

## Next Steps

1. ✅ Update `.env` file with Hugging Face token
2. ✅ Run `pip install -r requirements.txt`
3. ✅ Start backend: `uvicorn backend.app:app --reload`
4. ✅ Test API: Visit http://localhost:8000/docs
5. ✅ Upload documents and generate scripts

---

## Questions?

- Hugging Face Docs: https://huggingface.co/docs
- LangChain Hugging Face: https://python.langchain.com/docs/integrations/llms/huggingface
- API Status: https://huggingface.co/status
