import os
import json
from unemploymentstudios.tools.custom_tool import GenerateAndDownloadImageTool, SearchAndSaveSoundTool

# Create output directories
os.makedirs("./tool_tests/images", exist_ok=True)
os.makedirs("./tool_tests/audio", exist_ok=True)

def test_tools():
    print("Starting tool tests...")
    
    # Initialize the tools
    image_tool = GenerateAndDownloadImageTool()
    audio_tool = SearchAndSaveSoundTool()
    
    # Test image generation - Image 1
    print("\n=== Testing Image Generation - Image 1 ===")
    image1_result = image_tool._run(
        prompt="A heroic knight with a glowing sword standing on a cliff, pixel art style",
        file_name="./tool_tests/images/hero_knight.png"
    )
    print(f"Image 1 result: {image1_result}")
    
    # Test image generation - Image 2
    print("\n=== Testing Image Generation - Image 2 ===")
    image2_result = image_tool._run(
        prompt="A magical forest with glowing plants and a waterfall, pixel art style",
        file_name="./tool_tests/images/magical_forest.png"
    )
    print(f"Image 2 result: {image2_result}")
    
    # Test audio generation - Sound 1
    print("\n=== Testing Audio Generation - Sound 1 ===")
    audio1_result = audio_tool._run(
        query="adventure game background music fantasy",
        output_path="./tool_tests/audio/adventure_music.mp3"
    )
    print(f"Audio 1 result: {audio1_result}")
    
    # Test audio generation - Sound 2
    print("\n=== Testing Audio Generation - Sound 2 ===")
    audio2_result = audio_tool._run(
        query="game sword swing sound effect",
        output_path="./tool_tests/audio/sword_swing.mp3"
    )
    print(f"Audio 2 result: {audio2_result}")
    
    # Verify results
    verify_results()

def verify_results():
    """Verify that the files were created and log the results."""
    print("\n=== Verification Results ===")
    
    image_files = [
        "./tool_tests/images/hero_knight.png",
        "./tool_tests/images/magical_forest.png"
    ]
    
    audio_files = [
        "./tool_tests/audio/adventure_music.mp3",
        "./tool_tests/audio/sword_swing.mp3"
    ]
    
    # Check image files
    print("\nImage files:")
    for img_file in image_files:
        if os.path.exists(img_file):
            size = os.path.getsize(img_file) / 1024  # KB
            print(f"✅ {img_file} - {size:.2f} KB")
        else:
            print(f"❌ {img_file} - Not found")
    
    # Check audio files
    print("\nAudio files:")
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            size = os.path.getsize(audio_file) / 1024  # KB
            print(f"✅ {audio_file} - {size:.2f} KB")
        else:
            print(f"❌ {audio_file} - Not found")

if __name__ == "__main__":
    test_tools()

