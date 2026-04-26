from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import List
from backend.config import UPLOAD_DIR
from backend.utils.loaders import load_documents
from backend.utils.chunking import chunk_documents
from backend.services.rag_pipeline import create_vectorstore, save_topics
from backend.services.topic_service import extract_topics
from backend.config import VECTORSTORE_PATH

router = APIRouter(prefix="/api", tags=["topics"])

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@router.post("/extract-topics")
async def extract_topics_endpoint(files: List[UploadFile] = File(...)):
    """Upload documents and extract topics from them."""
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded")

    file_paths = []

    try:
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")

            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in [".pdf", ".docx", ".txt"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file_extension}. Supported: PDF, DOCX, TXT",
                )

            file_path = Path(UPLOAD_DIR) / file.filename
            content = await file.read()

            if not content:
                raise HTTPException(status_code=400, detail=f"Empty file: {file.filename}")

            with open(file_path, "wb") as f:
                f.write(content)

            file_paths.append(str(file_path))

        documents = load_documents(file_paths)
        chunks = chunk_documents(documents)
        create_vectorstore(chunks)
        topics = extract_topics(documents)
        
        # Save topics for validation during script generation
        save_topics(topics, VECTORSTORE_PATH)
        
        # Check for thin document detection (< 3 topics extracted)
        if len(topics) < 3:
            return {
                "topics": topics,
                "warning": f"Only {len(topics)} topic(s) extracted. Document may be too thin for comprehensive podcast discussion. Consider uploading more content.",
                "status": "insufficient_content"
            }

        return {
            "topics": topics,
            "status": "success",
            "count": len(topics)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
