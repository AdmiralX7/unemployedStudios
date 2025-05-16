from typing import Type, Any, Optional
import base64
import os
import json
import pathlib
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import dotenv

# ---------------------------------------------------------------------------
#  GenerateAndDownloadImageTool – generates + downloads image to ./assets/images/
# ---------------------------------------------------------------------------
class GenerateAndDownloadImageSchema(BaseModel):
    prompt: str = Field(..., description="Prompt for DALL·E")
    file_name: str = Field(..., description="Where to save the image (PNG)")
    size: str = Field("1024x1024", description="Image resolution")
    response_format: str = Field("url", description="url or b64_json")
    model: str = Field("dall-e-3", description="DALL·E model name")
    n: int = Field(1, description="Number of images (1)")

class GenerateAndDownloadImageTool(BaseTool):
    """
    A single tool that generates an image via OpenAI's DALL·E API
    and downloads it locally (**url** or **b64_json** variant).
    """
    name: str = "generate_and_download_image"
    description: str = (
        "Generate an image from a prompt via DALL·E, "
        "then download the resulting image to file."
    )
    args_schema: Type[BaseModel] = GenerateAndDownloadImageSchema

    def _run(self, **kwargs) -> Any:
        prompt = kwargs["prompt"]
        file_name = kwargs["file_name"]
        size = kwargs.get("size", "1024x1024")
        response_format = kwargs.get("response_format", "url")
        model = kwargs.get("model", "dall-e-3")
        n = kwargs.get("n", 1)

        # -- Make sure OPENAI_API_KEY is set
        dotenv.load_dotenv(override=True)
        if not os.getenv("OPENAI_API_KEY"):
            return "OPENAI_API_KEY is not set in the environment."

        # -- Configure client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # -- Call DALL·E
        response = client.images.generate(
            prompt=prompt,
            n=n,
            size=size,
            response_format=response_format,
            model=model,
        )
        response_dict = response.model_dump(mode="python")

        if not response_dict or "data" not in response_dict or len(response_dict["data"]) == 0:
            return "No image data returned from DALL·E."

        # ---------------------------------------------------------
        # Depending on the response format, extract the image data
        # ---------------------------------------------------------
        if response_format == "url":
            image_url = response_dict["data"][0]["url"]

            # Download the image from the URL
            r = requests.get(image_url, timeout=30)
            r.raise_for_status()

            # Ensure folder exists
            pathlib.Path(file_name).expanduser().parent.mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(r.content)

            return json.dumps(
                {
                    "message": f"Image generated and saved as {file_name}.",
                    "url": image_url,
                },
                indent=2,
            )

        else:  # b64_json
            b64_data = response_dict["data"][0]["b64_json"]
            image_bytes = b64_data.encode("utf-8")
            decoded = base64.decodebytes(image_bytes)

            pathlib.Path(file_name).expanduser().parent.mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(decoded)

            return json.dumps(
                {
                    "message": f"Image generated (base64) and saved as {file_name}",
                },
                indent=2,
            )

    async def _arun(self, **kwargs) -> Any:
        return self._run(**kwargs)

# ---------------------------------------------------------------------------
#  SearchAndSaveSoundTool – searches Freesound + downloads to ./assets/audio/
# ---------------------------------------------------------------------------
class SearchAndSaveSoundToolArgs(BaseModel):
    """Arguments accepted by SearchAndSaveSoundTool."""
    query: str = Field(..., description="Search text for the Freesound query")
    output_path: str = Field(
        ...,
        description="Absolute or relative path (including filename) where the preview will be written"
    )
    max_results: Optional[int] = Field(
        5,
        description="Maximum number of results to consider (the first hit will be downloaded)"
    )

class SearchAndSaveSoundTool(BaseTool):
    """
    Searches Freesound for the query, scrapes the first result using BeautifulSoup,
    and downloads the preview audio file.
    """
    name: str = "search_and_save_sound"
    description: str = (
        "Search Freesound for an audio clip and save the first preview to disk. "
        "Returns a JSON blob describing the saved file."
    )
    args_schema = SearchAndSaveSoundToolArgs

    def _run(
        self,
        *,
        query: str,
        output_path: str,
        max_results: int = 5,
        **_
    ) -> Any:
        import os
        import json
        import requests
        
        # Always use the fallback method since we're having issues with the client library
        try:
            # Fallback to direct API requests
            print("Using direct API requests for Freesound")
            try:
                api_key = os.getenv("FREESOUND_API_KEY")
                if not api_key:
                    return json.dumps({"error": "FREESOUND_API_KEY not set in environment."})
                
                # Direct API request to search
                search_url = f"https://freesound.org/apiv2/search/text/"
                headers = {
                    "Authorization": f"Token {api_key}"
                }
                params = {
                    "query": query,
                    "page_size": max_results,
                    "fields": "id,name,previews,url"
                }
                
                response = requests.get(search_url, headers=headers, params=params, timeout=15)
                response.raise_for_status()
                results = response.json()
                
                if "results" not in results or len(results["results"]) == 0:
                    return json.dumps({"error": "No results found."})
                
                sound = results["results"][0]
                
                # Extract the preview URL from the sound object
                preview_url = None
                if "previews" in sound:
                    previews = sound["previews"]
                    if isinstance(previews, dict):
                        preview_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
                    elif isinstance(previews, list):
                        # If it's a list of preview objects
                        for preview in previews:
                            if isinstance(preview, dict) and "url" in preview:
                                preview_url = preview["url"]
                                break
                
                # If we still don't have a URL, try a different approach
                if not preview_url and "id" in sound:
                    sound_id = sound["id"]
                    # Try to get the sound directly by ID
                    sound_url = f"https://freesound.org/apiv2/sounds/{sound_id}/"
                    sound_response = requests.get(sound_url, headers=headers, timeout=15)
                    if sound_response.status_code == 200:
                        sound_data = sound_response.json()
                        if "previews" in sound_data:
                            previews = sound_data["previews"]
                            if isinstance(previews, dict):
                                preview_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
                
                if not preview_url:
                    return json.dumps({"error": "No preview audio found for this sound."})
                
                audio_data = requests.get(preview_url, timeout=15)
                audio_data.raise_for_status()
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(audio_data.content)
                
                return json.dumps({
                    "file": output_path,
                    "original_url": sound.get("url", ""),
                    "preview_url": preview_url,
                    "message": f"Audio saved as {output_path}"
                }, indent=2)
                
            except Exception as e:
                return json.dumps({"error": f"Failed to fetch or save audio: {e}"})
                
        except Exception as outer_e:
            return json.dumps({"error": f"Outer exception: {outer_e}"})
