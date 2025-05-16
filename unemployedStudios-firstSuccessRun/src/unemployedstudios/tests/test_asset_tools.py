#!/usr/bin/env python
import os
import json
import sys
import dotenv
from pathlib import Path

# Add src directory to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Make sure environment variables are loaded
dotenv.load_dotenv(override=True)

# Import the tools using try/except to handle different import contexts
try:
    from unemployedstudios.tools.custom_tool import GenerateAndDownloadImageTool, SearchAndSaveSoundTool
except ModuleNotFoundError:
    # Fallback to direct import when run as a script
    from src.unemployedstudios.tools.custom_tool import GenerateAndDownloadImageTool, SearchAndSaveSoundTool

# Create output directories
def setup_test_directories():
    """Create directories for test outputs"""
    test_dir = Path("./test_output")
    image_dir = test_dir / "images"
    audio_dir = test_dir / "audio"
    
    image_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    return test_dir, image_dir, audio_dir

def test_tools():
    """Run tests for both image and audio generation tools"""
    print("Starting asset generation tool tests...")
    print(f"OPENAI_API_KEY available: {bool(os.getenv('OPENAI_API_KEY'))}")
    print(f"FREESOUND_API_KEY available: {bool(os.getenv('FREESOUND_API_KEY'))}")
    print(f"FREESOUND_CLIENT_ID available: {bool(os.getenv('FREESOUND_CLIENT_ID'))}")
    
    # Setup directories
    test_dir, image_dir, audio_dir = setup_test_directories()
    
    # Initialize the tools
    image_tool = GenerateAndDownloadImageTool()
    audio_tool = SearchAndSaveSoundTool()
    
    # Track results
    results = {
        "images": {},
        "audio": {}
    }
    
    # Test image generation
    test_images(image_tool, image_dir, results)
    
    # Test audio generation
    test_audio(audio_tool, audio_dir, results)
    
    # Verify results
    verify_results(results)
    
    # Save results to JSON file
    with open(test_dir / "test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to {test_dir / 'test_results.json'}")
    
    return results

def test_images(image_tool, image_dir, results):
    """Test image generation tool with multiple prompts and various sizes"""
    test_cases = [
        {
            "name": "main_character",
            "prompt": "A computer science student character for a pixel art platformer game, wearing casual clothes with a laptop backpack",
            "filename": "main_character.png",
            "size": "1024x1024"
        },
        {
            "name": "game_background",
            "prompt": "A university campus background with computer labs for a pixel art game",
            "filename": "university_background.png",
            "size": "1024x1024"
        },
        {
            "name": "game_enemy",
            "prompt": "A small bug-like computer virus monster for a pixel art platformer game",
            "filename": "enemy_virus.png",
            "size": "1024x1024"
        },
        {
            "name": "game_collectible",
            "prompt": "A glowing USB drive powerup item for a pixel art game, wide format",
            "filename": "powerup_usb.png",
            "size": "1792x1024"
        },
        {
            "name": "game_ui_button",
            "prompt": "A start button with pixel art style for a computer science themed game interface, vertical format",
            "filename": "ui_button.png",
            "size": "1024x1792"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Testing Image Generation ({i+1}/{len(test_cases)}): {test_case['name']} ===")
        
        output_path = image_dir / test_case["filename"]
        
        try:
            result = image_tool._run(
                prompt=test_case["prompt"],
                file_name=str(output_path),
                size=test_case["size"]
            )
            
            print(f"✅ Generated image: {output_path} (Size: {test_case['size']})")
            
            # Parse the result if it's a JSON string
            try:
                if isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = result
            except:
                result_data = {"message": str(result)}
            
            # Store result
            results["images"][test_case["name"]] = {
                "prompt": test_case["prompt"],
                "file_path": str(output_path),
                "size": test_case["size"],
                "success": True,
                "result": result_data
            }
            
        except Exception as e:
            print(f"❌ Failed to generate image: {e}")
            results["images"][test_case["name"]] = {
                "prompt": test_case["prompt"],
                "file_path": str(output_path),
                "size": test_case["size"],
                "success": False,
                "error": str(e)
            }

def test_audio(audio_tool, audio_dir, results):
    """Test audio generation tool with multiple queries of varying types"""
    test_cases = [
        {
            "name": "jump_sound",
            "query": "game jump sound effect 8-bit",
            "filename": "jump_sound.mp3",
            "description": "Short jumping effect"
        },
        {
            "name": "background_music",
            "query": "8-bit music loop",
            "filename": "background_music.mp3",
            "description": "Longer background music"
        },
        {
            "name": "collect_item",
            "query": "coin collect 8-bit",
            "filename": "collect_item.mp3",
            "description": "Very short collection sound"
        },
        {
            "name": "game_over",
            "query": "8-bit game over sound effect",
            "filename": "game_over.mp3",
            "description": "Medium length game over jingle"
        },
        {
            "name": "menu_click",
            "query": "ui click",
            "filename": "menu_click.mp3",
            "description": "Extremely short UI interaction sound"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Testing Audio Generation ({i+1}/{len(test_cases)}): {test_case['name']} ===")
        print(f"Description: {test_case['description']}")
        
        output_path = audio_dir / test_case["filename"]
        
        try:
            # Get both credentials
            freesound_api_key = os.getenv('FREESOUND_API_KEY')
            freesound_client_id = os.getenv('FREESOUND_CLIENT_ID')
            
            extra_params = {}
            if freesound_api_key:
                extra_params['api_key'] = freesound_api_key
                print(f"Using Freesound API Key: Available")
            if freesound_client_id:
                extra_params['client_id'] = freesound_client_id
                print(f"Using Freesound Client ID: Available")
                
            result = audio_tool._run(
                query=test_case["query"],
                output_path=str(output_path),
                **extra_params
            )
            
            # Verify the file was actually created before marking as success
            if os.path.exists(output_path):
                print(f"✅ Generated audio: {output_path}")
                
                # Parse the result if it's a JSON string
                try:
                    if isinstance(result, str):
                        result_data = json.loads(result)
                    else:
                        result_data = result
                except:
                    result_data = {"message": str(result)}
                
                # Store result
                results["audio"][test_case["name"]] = {
                    "query": test_case["query"],
                    "file_path": str(output_path),
                    "description": test_case["description"],
                    "success": True,
                    "result": result_data
                }
            else:
                raise Exception(f"Audio file was not created despite successful API response")
            
        except Exception as e:
            print(f"❌ Failed to generate audio: {e}")
            results["audio"][test_case["name"]] = {
                "query": test_case["query"],
                "file_path": str(output_path),
                "description": test_case["description"],
                "success": False,
                "error": str(e)
            }

def verify_results(results):
    """Verify that files were created and show results"""
    print("\n=== Verification Results ===")
    
    # Verify images
    print("\nImage files:")
    for name, data in results["images"].items():
        file_path = data["file_path"]
        if data["success"] and os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024  # KB
            dimensions = data.get("size", "unknown dimensions")
            print(f"✅ {name}: {file_path} - {size_kb:.2f} KB ({dimensions})")
            print(f"   Prompt: \"{data['prompt'][:60]}...\"")
        else:
            print(f"❌ {name}: {file_path} - Not found or generation failed")
            if not data["success"] and "error" in data:
                print(f"   Error: {data['error']}")
    
    # Verify audio - make one more check to ensure files exist before reporting
    print("\nAudio files:")
    for name, data in results["audio"].items():
        file_path = data["file_path"]
        # Double-check file existence regardless of the reported success
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024  # KB
            description = data.get("description", "")
            print(f"✅ {name}: {file_path} - {size_kb:.2f} KB")
            print(f"   Description: {description}")
            print(f"   Query: \"{data['query'][:60]}...\"")
            # Update success flag if file exists
            if not data["success"]:
                data["success"] = True
                print(f"   Note: File exists despite reported failure")
        else:
            print(f"❌ {name}: {file_path} - Not found or generation failed")
            if not data["success"] and "error" in data:
                print(f"   Error: {data['error']}")
                
    # Summary statistics - recalculate with verified file existence
    print("\nSummary Statistics:")
    total_image_size = sum(os.path.getsize(data["file_path"]) / (1024 * 1024) 
                         for name, data in results["images"].items() 
                         if os.path.exists(data["file_path"]))
    total_audio_size = sum(os.path.getsize(data["file_path"]) / (1024 * 1024) 
                         for name, data in results["audio"].items() 
                         if os.path.exists(data["file_path"]))
    
    actual_image_count = sum(1 for name, data in results["images"].items() if os.path.exists(data["file_path"]))
    actual_audio_count = sum(1 for name, data in results["audio"].items() if os.path.exists(data["file_path"]))
    
    print(f"Total Images: {actual_image_count}/{len(results['images'])} files, {total_image_size:.2f} MB")
    print(f"Total Audio: {actual_audio_count}/{len(results['audio'])} files, {total_audio_size:.2f} MB")
    print(f"Total Assets: {actual_image_count + actual_audio_count} files, {total_image_size + total_audio_size:.2f} MB")

def main():
    """Main function to run tests"""
    test_tools()

if __name__ == "__main__":
    main() 