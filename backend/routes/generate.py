from fastapi import APIRouter, HTTPException
from backend.models.request_models import GenerateRequest, RegenerateRequest
from backend.services.script_service import generate_script, regenerate_script
from backend.services.rag_pipeline import load_vectorstore, load_topics
from backend.config import VECTORSTORE_PATH

router = APIRouter(prefix="/api", tags=["generate"])


def validate_topics(selected_topics: list) -> dict:
    """Validate selected topics against extracted topics from vectorstore."""
    # Load extracted topics from disk
    extracted_topics = load_topics(VECTORSTORE_PATH)
    
    if not extracted_topics:
        # Fallback: check if vectorstore exists at all
        vectorstore_data = load_vectorstore()
        if not vectorstore_data:
            return {
                "included_topics": selected_topics,
                "ignored_topics": [],
                "validation_status": "no_extraction",
                "warning": "No document extraction found. Please upload documents and extract topics first."
            }
        # Vectorstore exists but no topics saved - allow all selected topics
        return {
            "included_topics": selected_topics,
            "ignored_topics": [],
            "validation_status": "no_topic_validation",
            "note": "Topics validation skipped - no extracted topics found"
        }
    
    # Compare selected topics against extracted topics
    selected_set = set(t.lower().strip() for t in selected_topics)
    extracted_lower = set(t.lower().strip() for t in extracted_topics)
    
    included = [t for t in selected_topics if t.lower().strip() in extracted_lower]
    ignored = [t for t in selected_topics if t.lower().strip() not in extracted_lower]
    
    return {
        "included_topics": included,
        "ignored_topics": ignored,
        "validation_status": "validated",
        "extracted_topics_count": len(extracted_topics),
        "note": f"Compared {len(selected_topics)} selected topic(s) against {len(extracted_topics)} extracted topic(s)"
    }


@router.post("/generate")
async def generate_podcast_script(request: GenerateRequest):
    """Generate a podcast script based on provided parameters."""
    try:
        topic_validation = validate_topics(request.topics)

        script = generate_script(
            host_name=request.host_name,
            guest_name=request.guest_name,
            host_gender=request.host_gender,
            guest_gender=request.guest_gender,
            host_speed=request.host_speed,
            guest_speed=request.guest_speed,
            topics=request.topics,
            duration=request.duration,
        )

        return {
            "script": script,
            "metadata": {
                "word_count": request.duration * 150,
                "duration_minutes": request.duration,
                "topics_included": topic_validation.get("included_topics", []),
                "topics_ignored": topic_validation.get("ignored_topics", []),
                "validation_status": topic_validation.get("validation_status", ""),
                "validation_note": topic_validation.get("note", topic_validation.get("warning", "")),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")


@router.post("/regenerate")
async def regenerate_podcast_script(request: RegenerateRequest):
    """Regenerate a podcast script with specific modifications or improvements.
    
    Use this endpoint to modify aspects of a previously generated script:
    - Change tone or style (e.g., 'make it more technical', 'add humor')
    - Focus on specific topics
    - Adjust pacing or depth
    - Improve transitions or flow
    """
    try:
        topic_validation = validate_topics(request.topics)

        script = regenerate_script(
            host_name=request.host_name,
            guest_name=request.guest_name,
            host_gender=request.host_gender,
            guest_gender=request.guest_gender,
            host_speed=request.host_speed,
            guest_speed=request.guest_speed,
            topics=request.topics,
            duration=request.duration,
            modification_request=request.modification_request,
        )

        return {
            "script": script,
            "metadata": {
                "word_count": request.duration * 150,
                "duration_minutes": request.duration,
                "topics_included": topic_validation.get("included_topics", []),
                "topics_ignored": topic_validation.get("ignored_topics", []),
                "validation_status": topic_validation.get("validation_status", ""),
                "validation_note": topic_validation.get("note", topic_validation.get("warning", "")),
                "modification": request.modification_request,
            },
            "status": "regenerated"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating script: {str(e)}")
