from pydantic import BaseModel, Field
from typing import List, Optional

class ImageAssetSpec(BaseModel):
    """Specification for a visual asset to be generated"""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    asset_type: str = Field(..., description="Type of asset (character, environment, ui, etc.)")
    filename: str = Field(..., description="Filename with path for the asset")
    prompt: str = Field(..., description="Detailed DALL-E prompt to generate the image")
    style: str = Field(..., description="Visual style description")
    importance: int = Field(..., description="Priority level (1-5, where 1 is highest)")
    description: str = Field(..., description="Purpose and usage of the asset in the game")
    size: str = Field("1024x1024", description="Image resolution")

class AudioAssetSpec(BaseModel):
    """Specification for an audio asset to be sourced"""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    asset_type: str = Field(..., description="Type of audio (effect, music, ambient, ui)")
    filename: str = Field(..., description="Filename with path for the asset")
    search_terms: str = Field(..., description="Search terms to find the audio on Freesound")
    description: str = Field(..., description="Description of the sound and its purpose")
    importance: int = Field(..., description="Priority level (1-5, where 1 is highest)")
    duration: Optional[float] = Field(None, description="Desired duration in seconds (if applicable)")

class AssetSpecCollection(BaseModel):
    """Collection of all asset specifications for the game"""
    image_assets: List[ImageAssetSpec] = Field(default_factory=list, description="List of image asset specifications")
    audio_assets: List[AudioAssetSpec] = Field(default_factory=list, description="List of audio asset specifications") 