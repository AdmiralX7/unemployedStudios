#!/usr/bin/env python
import argparse
import sys
import os

# Add src directory to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Use relative import when imported as a module
try:
    from unemployedstudios.tests.test_asset_tools import test_tools, test_images, test_audio, setup_test_directories
except ModuleNotFoundError:
    # Fallback to direct import when run as a script
    from src.unemployedstudios.tests.test_asset_tools import test_tools, test_images, test_audio, setup_test_directories

def parse_args():
    parser = argparse.ArgumentParser(description='Test asset generation tools')
    parser.add_argument('--images-only', action='store_true', help='Run only image tests')
    parser.add_argument('--audio-only', action='store_true', help='Run only audio tests')
    parser.add_argument('--output-dir', type=str, default='./test_output', help='Directory for test outputs')
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.images_only and args.audio_only:
        print("Error: Can't specify both --images-only and --audio-only")
        sys.exit(1)
    
    if args.images_only:
        print("Running image generation tests only...")
        from unemployedstudios.tools.custom_tool import GenerateAndDownloadImageTool
        test_dir, image_dir, _ = setup_test_directories()
        image_tool = GenerateAndDownloadImageTool()
        results = {"images": {}, "audio": {}}
        test_images(image_tool, image_dir, results)
        
    elif args.audio_only:
        print("Running audio generation tests only...")
        from unemployedstudios.tools.custom_tool import SearchAndSaveSoundTool
        test_dir, _, audio_dir = setup_test_directories()
        audio_tool = SearchAndSaveSoundTool()
        results = {"images": {}, "audio": {}}
        test_audio(audio_tool, audio_dir, results)
        
    else:
        print("Running all asset generation tests...")
        results = test_tools()
    
    # Summarize test results
    image_success = sum(1 for data in results["images"].values() if data["success"])
    audio_success = sum(1 for data in results["audio"].values() if data["success"])
    
    print("\n=== Test Summary ===")
    print(f"Images: {image_success}/{len(results['images'])} successful")
    print(f"Audio: {audio_success}/{len(results['audio'])} successful")
    
    # Return non-zero exit code if any tests failed
    if image_success < len(results["images"]) or audio_success < len(results["audio"]):
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main() 