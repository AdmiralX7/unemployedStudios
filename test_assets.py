#!/usr/bin/env python
"""
Asset Generation Test Script

This script tests the asset generation tools to ensure they're working correctly.
It will generate test images and audio files to verify functionality.

Usage:
  python test_assets.py [--images-only] [--audio-only]

Options:
  --images-only    Test only image generation
  --audio-only     Test only audio generation
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    # Try direct import first
    from src.unemployedstudios.tests.run_asset_tests import main
except ImportError:
    # Fallback to module import
    from unemployedstudios.tests.run_asset_tests import main

if __name__ == "__main__":
    # Add description
    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        if "-h" not in sys.argv and "--help" not in sys.argv:
            print("\nRunning all tests...\n")
    
    # Run the tests
    main() 