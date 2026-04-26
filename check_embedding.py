from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_TOKEN")
print("HuggingFace API Token:", api_key[:20] + "..." if api_key else "NOT FOUND")

# Use the same embedding model as the backend config
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

try:
    print(f"\nLoading SentenceTransformer model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Test embedding generation
    test_text = "This is a test sentence for embedding generation."
    embedding = model.encode(test_text, convert_to_numpy=True)
    
    print("SUCCESS! Embedding model loaded successfully.")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"Model name: {EMBEDDING_MODEL}")
    
except Exception as e:
    print(f"Error loading embedding model: {str(e)}")
