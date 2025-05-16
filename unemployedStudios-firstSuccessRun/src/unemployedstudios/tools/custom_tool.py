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
    api_key: Optional[str] = Field(
        None, 
        description="Freesound API key - will use environment FREESOUND_API_KEY if not provided"
    )
    client_id: Optional[str] = Field(
        None, 
        description="Freesound client ID - will use environment FREESOUND_CLIENT_ID if not provided"
    )

class SearchAndSaveSoundTool(BaseTool):
    """
    Searches Freesound for the query, scrapes the first result using BeautifulSoup,
    and downloads the preview audio file.
    
    Note: This tool can use both FREESOUND_API_KEY and FREESOUND_CLIENT_ID from 
    environment variables. Both credentials may be needed for successful API access.
    """
    name: str = "search_and_save_sound"
    description: str = (
        "Search Freesound for an audio clip and save the first preview to disk. "
        "Returns a JSON blob describing the saved file. "
        "Uses both FREESOUND_API_KEY and FREESOUND_CLIENT_ID if available."
    )
    args_schema = SearchAndSaveSoundToolArgs

    def _run(
        self,
        *,
        query: str,
        output_path: str,
        max_results: int = 5,
        api_key: str = None,
        client_id: str = None,
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
                # Check for API key in parameters first, then environment
                api_key = api_key or os.getenv("FREESOUND_API_KEY")
                client_id = client_id or os.getenv("FREESOUND_CLIENT_ID")
                
                if api_key:
                    print(f"Using Freesound API Key: Available")
                if client_id:
                    print(f"Using Freesound Client ID: Available")
                
                # Search for sounds
                search_url = f"https://freesound.org/apiv2/search/text/"
                params = {
                    "query": query,
                    "sort": "score",
                    "fields": "id,name,previews,download,duration,username,license",
                    "page_size": max_results
                }
                headers = {"Authorization": f"Token {api_key}"}
                
                print(f"Sending search request with query: '{query}'")
                response = requests.get(search_url, params=params, headers=headers)
                response.raise_for_status()
                results = response.json()
                
                if not results.get("results"):
                    print("No results found")
                    return {"success": False, "message": "No results found"}
                
                print(f"Found {len(results.get('results', []))} results")
                
                # Debug: Print first few results with key details
                for i, sound in enumerate(results.get("results", [])[:3]):
                    print(f"Result {i+1}:")
                    print(f"  Name: {sound.get('name')}")
                    print(f"  Duration: {sound.get('duration', 'unknown')} seconds")
                    print(f"  User: {sound.get('username')}")
                    print(f"  License: {sound.get('license')}")
                    if "previews" in sound:
                        print(f"  Preview types: {list(sound['previews'].keys())}")
                
                # Get the first result
                sound = results["results"][0]
                
                # Extract the preview URL (prefer MP3 preview if available)
                preview_url = None
                if "previews" in sound:
                    preview_types = list(sound["previews"].keys())
                    print(f"Available preview types: {preview_types}")
                    
                    # Try to get the best quality preview
                    if "preview-hq-mp3" in preview_types:
                        preview_url = sound["previews"]["preview-hq-mp3"]
                    elif "preview-lq-mp3" in preview_types:
                        preview_url = sound["previews"]["preview-lq-mp3"]
                    elif "preview-hq-ogg" in preview_types:
                        preview_url = sound["previews"]["preview-hq-ogg"]
                    elif "preview-lq-ogg" in preview_types:
                        preview_url = sound["previews"]["preview-lq-ogg"]
                    elif preview_types:
                        # Take the first available preview type if none of the preferred ones are available
                        preview_url = sound["previews"][preview_types[0]]
                
                if not preview_url:
                    print("No preview URL found in the response")
                    return {"success": False, "message": "No preview URL found in the response", "sound_id": sound.get("id", "unknown")}
                
                print(f"Downloading audio from: {preview_url}")
                
                # Download the preview
                audio_data = requests.get(preview_url)
                audio_data.raise_for_status()
                
                # Write to file
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(audio_data.content)
                
                file_size = os.path.getsize(output_path)
                print(f"Downloaded audio file. Size: {file_size / 1024:.2f} KB")
                
                if file_size == 0:
                    raise Exception("Downloaded file has zero size")
                
                # Create a metadata structure to return
                filename = os.path.basename(output_path)
                result = {
                    "success": True,
                    "sound_id": sound["id"],
                    "filename": filename,
                    "duration": sound.get("duration", "unknown"),
                    "path": output_path,
                    "preview_url": preview_url,
                    "license": sound.get("license", "unknown"),
                    "file_size_bytes": file_size
                }
                
                return result
            
            except Exception as e:
                print(f"Error during Freesound API request: {e}")
                raise e
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            return {"error": str(e)}
