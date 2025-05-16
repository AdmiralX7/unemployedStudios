from pydantic import BaseModel, Field, validator
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
    size: str = Field("1024x1024", description="Image resolution - must be one of: 1024x1024, 1792x1024, or 1024x1792")
    model: str = Field("dall-e-3", description="Model to use - must be one of: 'gpt-image-1', 'dall-e-2', or 'dall-e-3'")
    
    @validator('size')
    def validate_size(cls, v):
        allowed_sizes = ["1024x1024", "1792x1024", "1024x1792"]
        if v not in allowed_sizes:
            raise ValueError(f"Size must be one of: {', '.join(allowed_sizes)}")
        return v
        
    @validator('model')
    def validate_model(cls, v):
        allowed_models = ["gpt-image-1", "dall-e-2", "dall-e-3"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {', '.join(allowed_models)}")
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
    # This field allows for string representation of duration for better human readability
    duration_description: Optional[str] = Field(None, description="Human-readable description of duration (e.g., '30 seconds')")
    
    @validator('duration', pre=True)
    def parse_duration(cls, v):
        """Parse duration from various formats to float seconds"""
        if v is None:
            return None
            
        # If already a number, return as is
        if isinstance(v, (int, float)):
            return float(v)
            
        # If a string, try to extract a number
        if isinstance(v, str):
            # Try to extract a simple number first
            import re
            
            # If it contains a range like "0.5-1 seconds", use the average
            range_match = re.search(r'(\d+\.?\d*)[^\d]+(\d+\.?\d*)', v)
            if range_match:
                try:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                    return (min_val + max_val) / 2  # Use the average
                except (ValueError, IndexError):
                    pass
            
            # Try to find a single number
            number_match = re.search(r'(\d+\.?\d*)', v)
            if number_match:
                try:
                    num_val = float(number_match.group(1))
                    
                    # Adjust for minutes to seconds if "minute" is in the string
                    if "minute" in v.lower():
                        num_val *= 60
                        
                    return num_val
                except (ValueError, IndexError):
                    pass
        
        # If all parsing attempts fail, return None
        return None
    
    @validator('search_terms')
    def enhance_search_terms(cls, v, values):
        """Enhance search terms based on asset type for better results"""
        asset_type = values.get('asset_type', '').lower()
        search_terms = v.lower()
        
        # Already enhanced, don't double-enhance
        if "search term enhanced" in search_terms:
            return v
            
        enhanced = False
        
        # Add sound effect for effect asset types if not present
        if asset_type == 'effect' and 'sound effect' not in search_terms:
            v = f"{v}, sound effect"
            enhanced = True
            
        # Add 8-bit for music asset types if not present
        if asset_type == 'music' and '8-bit' not in search_terms:
            v = f"{v}, 8-bit"
            enhanced = True
            
        # Add game sound for other asset types
        if asset_type not in ['effect', 'music'] and 'game sound' not in search_terms:
            v = f"{v}, game sound"
            enhanced = True
            
        # Mark as enhanced to prevent double processing
        if enhanced:
            v = f"{v} (search term enhanced)"
            
        return v

class AssetSpecCollection(BaseModel):
    """Collection of all asset specifications for the game"""
    image_assets: List[ImageAssetSpec] = Field(default_factory=list, description="List of image asset specifications")
    audio_assets: List[AudioAssetSpec] = Field(default_factory=list, description="List of audio asset specifications") 