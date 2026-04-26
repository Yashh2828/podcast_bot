from pydantic import BaseModel, Field, validator
from typing import List


class GenerateRequest(BaseModel):
    host_name: str = Field(..., min_length=1, description="Host name (non-empty string)")
    guest_name: str = Field(..., min_length=1, description="Guest name (non-empty string)")
    host_gender: str = Field(..., pattern="^(male|female|other)$", description="Host gender: male, female, or other")
    guest_gender: str = Field(..., pattern="^(male|female|other)$", description="Guest gender: male, female, or other")
    host_speed: int = Field(..., ge=50, le=150, description="Host speaking speed (50-150, where 50=slow, 100=normal, 150=fast)")
    guest_speed: int = Field(..., ge=50, le=150, description="Guest speaking speed (50-150, where 50=slow, 100=normal, 150=fast)")
    topics: List[str] = Field(..., min_items=1, description="List of podcast topics to discuss")
    duration: int = Field(..., description="Podcast duration in minutes (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, or 60)")
    
    @validator('duration')
    def validate_duration(cls, v):
        """Ensure duration is one of the allowed values: 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60."""
        allowed_durations = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        if v not in allowed_durations:
            raise ValueError(f"Duration must be one of: {allowed_durations}. Got {v}")
        return v


class RegenerateRequest(BaseModel):
    """Request model for regenerating podcast scripts with modifications."""
    host_name: str = Field(..., min_length=1, description="Host name (non-empty string)")
    guest_name: str = Field(..., min_length=1, description="Guest name (non-empty string)")
    host_gender: str = Field(..., pattern="^(male|female|other)$", description="Host gender: male, female, or other")
    guest_gender: str = Field(..., pattern="^(male|female|other)$", description="Guest gender: male, female, or other")
    host_speed: int = Field(..., ge=50, le=150, description="Host speaking speed (50-150)")
    guest_speed: int = Field(..., ge=50, le=150, description="Guest speaking speed (50-150)")
    topics: List[str] = Field(..., min_items=1, description="List of podcast topics to discuss")
    duration: int = Field(..., description="Podcast duration in minutes (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, or 60)")
    modification_request: str = Field(..., min_length=1, description="Specific modification or regeneration instructions (e.g., 'make it more technical', 'focus on topic 1')")
    
    @validator('duration')
    def validate_duration(cls, v):
        """Ensure duration is one of the allowed values."""
        allowed_durations = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        if v not in allowed_durations:
            raise ValueError(f"Duration must be one of: {allowed_durations}. Got {v}")
        return v
