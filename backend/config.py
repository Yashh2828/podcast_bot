import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ImportError("HUGGINGFACE_API_TOKEN not found in environment variables")

VECTORSTORE_PATH = "backend/vectorstore/db"
UPLOAD_DIR = "data/uploads"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
# Hugging Face model options:
# - "mistralai/Mistral-7B-Instruct-v0.1" (fast, good quality)
# - "meta-llama/Llama-2-7b-chat-hf" (good for conversations)
# - "microsoft/DialoGPT-medium" (conversational)
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
