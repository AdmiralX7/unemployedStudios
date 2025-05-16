from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic import validator

class ImageAssetSpec(BaseModel):
    """Specification for a visual asset to be generated"""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    asset_type: str = Field(..., description="Type of asset (character, environment, ui, etc.)")
    filename: str = Field(..., description="Filename with path for the asset")
    prompt: str = Field(..., description="Detailed DALL-E prompt to generate the image")
    style: str = Field(..., description="Visual style description")
    importance: int = Field(..., description="Priority level (1-5, where 1 is highest)")
    description: str = Field(..., description="Purpose and usage of the asset in the game")
    size: str = Field("1024x1024", description="Image resolution - must be one of: 1024x1024, 1792x1024, or 1024x1792")
    model: str = Field("dall-e-3", description="DALL-E model to use")
    
    class Config:
        validate_assignment = True
        # Add validation for size to be one of the allowed values
        @validator('size')
        def validate_size(cls, v):
            allowed_sizes = ["1024x1024", "1792x1024", "1024x1792"]
            if v not in allowed_sizes:
                raise ValueError(f"Size must be one of: {', '.join(allowed_sizes)}")
            return v

class AudioAssetSpec(BaseModel):
    """Specification for an audio asset to be sourced"""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    asset_type: str = Field(..., description="Type of audio (effect, music, ambient, ui)")
    filename: str = Field(..., description="Filename with path for the asset")
    search_terms: str = Field(..., description="Search terms to find the audio on Freesound")
    description: str = Field(..., description="Description of the sound and its purpose")
    importance: int = Field(..., description="Priority level (1-5, where 1 is highest)")
    duration: Optional[float] = Field(None, description="Desired duration in seconds (if applicable)")
    # Add a query field as an alias for search_terms to match the tool interface
    query: Optional[str] = Field(None, description="Alternative to search_terms, will be used if provided")

class AssetSpecCollection(BaseModel):
    """Collection of all asset specifications for the game"""
    image_assets: List[ImageAssetSpec] = Field(default_factory=list, description="List of image asset specifications")
    audio_assets: List[AudioAssetSpec] = Field(default_factory=list, description="List of audio asset specifications") 