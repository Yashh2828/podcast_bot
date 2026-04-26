from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import topics, generate
from backend.services.rag_pipeline import clear_vectorstore
from backend.config import VECTORSTORE_PATH

app = FastAPI(
    title="Podcast Script Generation API",
    description="Generate podcast scripts using RAG and LLM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router)
app.include_router(generate.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/restart")
async def restart_flow():
    """
    Restart the podcast generation flow.
    
    Clears all uploaded documents, extracted topics, and vectorstore data.
    User must re-enter all inputs and upload documents again.
    """
    try:
        cleared = clear_vectorstore(VECTORSTORE_PATH)
        if cleared:
            return {
                "status": "success",
                "message": "Flow restarted. All prior inputs and selections have been cleared. Please re-enter configuration and upload documents.",
                "actions_required": [
                    "Re-enter speaker information",
                    "Re-upload documents",
                    "Re-extract topics",
                    "Select topics again"
                ]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear vectorstore")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting flow: {str(e)}")
