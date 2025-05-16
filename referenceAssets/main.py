#!/usr/bin/env python
import os
import dotenv
dotenv.load_dotenv(override=True)
from typing import Dict
from random import randint
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start

# Import Crews
from unemploymentstudios.crews.concept_expansion_crew.concept_expansion_crew import ConceptExpansionCrew
from unemploymentstudios.crews.file_structure_planning_crew.file_structure_planning_crew import FileStructurePlanningCrew
from unemploymentstudios.crews.general_code_crew.general_code_crew import GeneralCodeCrew
from unemploymentstudios.crews.asset_generation_crew.asset_generation_crew import AssetGenerationCrew
from unemploymentstudios.crews.testing_qa_crew.testing_qa_crew import TestingQACrew

# Import Pydantic Types
from unemploymentstudios.types import GameConcept, AssetSpecCollection, ImageAssetSpec, AudioAssetSpec

# Additional Imports
import asyncio
import time
import json
import shutil
import pathlib
from pathlib import Path

# Load concept from file or create default if it doesn't exist
concept_path = os.path.join(os.path.dirname(__file__), "knowledge", "concept.json")
try:
    with open(concept_path) as f:
        concept = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Create a default concept if file doesn't exist or is invalid
    concept = {
        "Storyline": "A heroic adventure through a magical world",
        "Game mechanics": "Platformer with puzzle-solving elements",
        "Characters and Interactive entities": "A brave hero with magical abilities, various enemies and allies",
        "Levels and difficulty": "Multiple levels with increasing difficulty",
        "Visual and audio style": "Vibrant fantasy world with orchestral music"
    }
    # Ensure the directory exists
    os.makedirs(os.path.dirname(concept_path), exist_ok=True)
    with open(concept_path, "w") as f:
        json.dump(concept, f, indent=2)

def is_directory(path: str) -> bool:
    # For example, treat anything that ends in a slash as a directory
    return path.endswith("/")

class GameState(BaseModel):
    # Concept fields ---------------------------------------------------------
    Storyline: str = concept["Storyline"]
    Game_Mechanics: str = concept["Game mechanics"]
    Entities: str = concept["Characters and Interactive entities"]
    Levels: str = concept["Levels and difficulty"]
    visualAudioStyle: str = concept["Visual and audio style"]

    # Phase outputs ----------------------------------------------------------
    conceptExpansionOutput: str = ""
    fileStructurePlanningOutput: str = ""
    assetGenerationOutput: str = ""
    testingQAOutput: str = ""

    # Generated artefacts ----------------------------------------------------
    generatedCodeFiles: Dict[str, str] = Field(default_factory=dict)
    generatedAssetSpecs: Dict[str, str] = Field(default_factory=dict)
    generatedImages: Dict[str, str] = Field(default_factory=dict)
    generatedSounds: Dict[str, str] = Field(default_factory=dict)
    qaReports: Dict[str, str] = Field(default_factory=dict)

class GameFlow(Flow[GameState]):
    @start()
    def start_game(self):
        print("")
        print("=== Starting Game Generation Process ===")
        print("This process will use multiple AI agents working in crews to generate a complete game")
        print("1. Concept Expansion - Develop detailed game concept")
        print("2. File Structure Planning - Design the codebase architecture")
        print("3. Code Generation - Create the actual game code files")
        print("4. Asset Generation - Create specifications for graphics and audio")
        print("5. Testing & QA - Ensure all components work together")
        print("")

    @listen(start_game)
    def concept_expansion(self):
        print("=== Starting Concept Expansion Phase ===")
        
        concept_expansion_raw = (
            ConceptExpansionCrew()
            .crew()
            .kickoff(inputs={
                "Storyline": self.state.Storyline, 
                "Game_Mechanics":self.state.Game_Mechanics, 
                "Entities":self.state.Entities, 
                "Levels":self.state.Levels, 
                "visualAudioStyle":self.state.visualAudioStyle
            })
        )

        self.state.conceptExpansionOutput = concept_expansion_raw.raw
        print("=== Concept Expansion Phase Complete ===")

    @listen(concept_expansion)
    def save_concept(self):
        print("=== Saving Expanded Game Concept ===")
        
        # Define the desired directory and file name
        output_dir = "./Game"
        file_name = "game_concept.txt"
        file_path = os.path.join(output_dir, file_name)

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Write the file (creates file if it doesn't exist)
        with open("./Game/game_concept.txt", "w") as f:
            f.write(self.state.conceptExpansionOutput)
            
        print(f"Saved expanded game concept to {file_path}")

    @listen(save_concept)
    def file_structure_planning(self):
        print("=== Starting File Structure Planning Phase ===")
        
        # 1. Parse JSON string into a Pydantic model.
        expanded_concept = GameConcept(**json.loads(self.state.conceptExpansionOutput))

        # For supporting_characters, turn each Character object into a dict
        supporting_characters_as_dicts = [char.dict() for char in expanded_concept.supporting_characters]
        # Same for levels (turn each Level object into a dict)
        levels_as_dicts = [lvl.dict() for lvl in expanded_concept.levels]

        # Build a dictionary for the base fields (non-list)
        inputs_dict = {
            "title": expanded_concept.title,
            "tagline": expanded_concept.tagline,
            "overview": expanded_concept.overview,
            "main_character": expanded_concept.main_character.name,
            "main_character_name": expanded_concept.main_character.name,
            "main_character_role": expanded_concept.main_character.role,
            "main_character_abilities": expanded_concept.main_character.abilities,
            "main_character_description": expanded_concept.main_character.description,
            "main_character_emotional_arc": expanded_concept.main_character.emotional_arc,
            "supporting_characters": supporting_characters_as_dicts,
            "supporting_characters|length": len(expanded_concept.supporting_characters),
            "world_building": expanded_concept.world_building,
            "levels": levels_as_dicts,
            "levels|length": len(expanded_concept.levels),
            "gameplay_mechanics": expanded_concept.gameplay_mechanics,
            "visual_style": expanded_concept.visual_style,
            "audio_style": expanded_concept.audio_style,
            "emotional_arc": expanded_concept.emotional_arc,
            "conclusion": expanded_concept.conclusion,
        }

        #
        # 2. Precompute placeholders for each supporting character
        #
        character_inputs = {}
        for idx, char in enumerate(expanded_concept.supporting_characters):
            prefix = f"supporting_characters_{idx}_"
            character_inputs[f"{prefix}name"] = char.name
            character_inputs[f"{prefix}role"] = char.role
            character_inputs[f"{prefix}description"] = char.description
            character_inputs[f"{prefix}abilities"] = char.abilities
            character_inputs[f"{prefix}emotional_arc"] = char.emotional_arc

        #
        # 3. Precompute placeholders for each level
        #
        level_inputs = {}
        for idx, lvl in enumerate(expanded_concept.levels):
            prefix = f"levels_{idx}_"
            level_inputs[f"{prefix}name"] = lvl.name
            level_inputs[f"{prefix}description"] = lvl.description
            level_inputs[f"{prefix}difficulty"] = lvl.difficulty
            level_inputs[f"{prefix}key_objectives"] = lvl.key_objectives
            level_inputs[f"{prefix}enemies_obstacles"] = lvl.enemies_obstacles
            level_inputs[f"{prefix}boss_battle"] = lvl.boss_battle

        #
        # 3a. Also define the first/last-level placeholders that match tasks.yaml
        #
        # Only do this if at least one level exists.
        if expanded_concept.levels:
            first_level = expanded_concept.levels[0]
            inputs_dict["first_level_name"] = first_level.name
            inputs_dict["first_level_difficulty"] = first_level.difficulty
            inputs_dict["first_level_enemies_obstacles"] = first_level.enemies_obstacles

            # If there's a "last" level distinct from the first, define placeholders from that too:
            last_level = expanded_concept.levels[-1]
            inputs_dict["last_level_name"] = last_level.name
            inputs_dict["last_level_difficulty"] = last_level.difficulty
            inputs_dict["last_level_boss_battle"] = last_level.boss_battle

            # For tasks referencing all level names in a single string (e.g., {levels_names}):
            level_names = [lvl.name for lvl in expanded_concept.levels]
            inputs_dict["levels_names"] = ", ".join(level_names)

        # Merge our custom loops into the main inputs_dict
        inputs_dict.update(character_inputs)
        inputs_dict.update(level_inputs)

        # 4. Kick off your crew with the full dictionary of placeholders
        file_structure_planning_raw = (
            FileStructurePlanningCrew()
            .crew()
            .kickoff(inputs=inputs_dict)
        )

        self.state.fileStructurePlanningOutput = file_structure_planning_raw.raw
        print("=== File Structure Planning Phase Complete ===")

    @listen(file_structure_planning)
    def save_file_structure(self):
        print("=== Saving File Structure Plan ===")

        # Define the desired directory and file name
        output_dir = "./Game"
        file_name = "file_structure.txt"
        file_path = os.path.join(output_dir, file_name)

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Write the file (creates file if it doesn't exist)
        with open("./Game/file_structure.txt", "w") as f:
            f.write(self.state.fileStructurePlanningOutput)
        
        # Extract just the JSON part for proper parsing 
        # and save it as a separate JSON file for reliable access
        try:
            # First, try to parse it directly in case it's clean JSON
            file_structure = json.loads(self.state.fileStructurePlanningOutput)
            
            # If successful, write the clean JSON to a file
            with open("./Game/file_structure.json", "w") as f:
                json.dump(file_structure, f, indent=2)
                
            print(f"Saved structured file plan to {output_dir}/file_structure.json")
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON using regex
            import re
            json_match = re.search(r'(\{[\s\S]*\})', self.state.fileStructurePlanningOutput)
            
            if json_match:
                try:
                    # Try to parse the extracted JSON
                    json_text = json_match.group(1)
                    file_structure = json.loads(json_text)
                    
                    # If successful, write the clean JSON to a file
                    with open("./Game/file_structure.json", "w") as f:
                        json.dump(file_structure, f, indent=2)
                    
                    print(f"Extracted and saved structured file plan to {output_dir}/file_structure.json")
                except json.JSONDecodeError:
                    print("Warning: Could not extract valid JSON from the output.")
                    # Create a fallback structure
                    self._create_fallback_file_structure()
            else:
                print("Warning: Could not find JSON data in the output.")
                # Create a fallback structure
                self._create_fallback_file_structure()
            
        print(f"Saved file structure plan to {file_path}")
    
    def _create_fallback_file_structure(self):
        """Create a minimal fallback file structure if JSON parsing fails."""
        fallback_structure = {
            "files": [
                {
                    "filename": "index.html",
                    "purpose": "Main entry point for the game",
                    "content_guidelines": "Create a simple HTML file that loads game assets and scripts",
                    "dependencies": ["style.css", "game.js"]
                },
                {
                    "filename": "style.css",
                    "purpose": "Main stylesheet for the game",
                    "content_guidelines": "Basic styling for the game elements",
                    "dependencies": []
                },
                {
                    "filename": "game.js",
                    "purpose": "Main game logic",
                    "content_guidelines": "Implement core game mechanics",
                    "dependencies": []
                }
            ]
        }
        
        with open("./Game/file_structure.json", "w") as f:
            json.dump(fallback_structure, f, indent=2)
        
        print("Created fallback file structure JSON")
        
        # Also update the state with the fallback structure
        self.state.fileStructurePlanningOutput = json.dumps(fallback_structure)

    @listen(save_file_structure)
    async def write_code_files(self):
        """
        Parse the file structure planning output, 
        spawn an async writing job for each file, and await them concurrently.
        """
        print("=== Starting Code Generation Phase ===")
        print("TEMPORARY TEST MODE: Only generating the first file...")

        # Parse the file structure planning output from the JSON file
        try:
            with open("./Game/file_structure.json", "r") as f:
                file_structure = json.load(f)
            
            files = file_structure["files"]  # This is the array of file specs
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error reading file structure: {str(e)}")
            print("No files to generate. Check file structure output.")
            return

        # If no files, exit early
        if not files:
            print("No files to generate. Check file structure output.")
            return

        # TEMPORARY: Only process the first file for testing
        if files:
            first_file = files[0]
            print(f"Generating only the first file: {first_file['filename']}")
            result = await self._generate_file_code(first_file)
            
            if result:
                filename, content = result
                self.state.generatedCodeFiles[filename] = content
                self._write_file_to_disk(filename, content)
                print(f"=== Generated 1 code file for testing: {filename} ===")
            else:
                print("Failed to generate the test file.")
        else:
            print("No files found in the structure plan.")
        
        # Skip the original concurrent code generation
        print("=== Skipped remaining files for testing purposes ===")

    async def _generate_file_code(self, file_spec):
        """
        Generate code for a single file using the GeneralCodeCrew
        """
        filename = file_spec["filename"]
        purpose = file_spec["purpose"]
        content_guidelines = file_spec["content_guidelines"]
        dependencies = file_spec.get("dependencies", [])
        
        print(f"Generating code for: {filename}")
        
        try:
            # Use GeneralCodeCrew to generate the file content
            file_result = (
                GeneralCodeCrew()
                .crew()
                .kickoff(inputs={
                    "filename": filename,
                    "purpose": purpose,
                    "content_guidelines": content_guidelines,
                    "dependencies": dependencies
                })
            )
            
            # Return the filename and content
            return filename, file_result.raw
        except Exception as e:
            print(f"Error generating code for {filename}: {str(e)}")
            return None
        
    def _write_file_to_disk(self, filename: str, content: str):
        """
        Write a generated file to disk, skipping folder‑only entries.
        """
        output_dir = "./Game"

        # Skip any paths that try to write outside the Game directory
        if filename.startswith('/'):
            print(f"Warning: Skipping file with absolute path: {filename}")
            # Store a sanitized version in the state
            safe_filename = filename.lstrip('/')
            self.state.generatedCodeFiles[safe_filename] = content
            return

        # ── 1️⃣ Ignore or create directory‑only specs ───────────────────────────────
        if filename.endswith("/") or os.path.basename(filename) == "":
            try:
                dir_path = os.path.join(output_dir, filename)
                os.makedirs(dir_path, exist_ok=True)
                print(f"Created directory (no file to write): {dir_path}")
            except OSError as e:
                print(f"Warning: Could not create directory {dir_path}: {e}")
            return

        # ── 2️⃣ Ensure parent folders exist (unchanged) ────────────────────────────
        if "/" in filename:
            sub_path = os.path.dirname(filename)
            full_dir_path = os.path.join(output_dir, sub_path)
            try:
                os.makedirs(full_dir_path, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create directory {full_dir_path}: {e}")
                # Skip file creation if we can't create the directory
                return

        # ── 3️⃣ Write the file (unchanged) ─────────────────────────────────────────
        file_path = os.path.join(output_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Wrote file: {file_path}")
        except OSError as e:
            print(f"Warning: Could not write file {file_path}: {e}")
            # Store the content in state even if we couldn't write to disk
            self.state.generatedCodeFiles[filename] = content

    @listen(save_file_structure)
    async def write_code_files(self):
        """
        Parse the file structure planning output, 
        spawn an async writing job for each file, and await them concurrently.
        """
        print("=== Starting Code Generation Phase ===")
        print("Generating code files concurrently...")

        # Parse the file structure planning output from the JSON file
        try:
            with open("./Game/file_structure.json", "r") as f:
                file_structure = json.load(f)
            
            files = file_structure["files"]  # This is the array of file specs
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error reading file structure: {str(e)}")
            print("No files to generate. Check file structure output.")
            return

        # If no files, exit early
        if not files:
            print("No files to generate. Check file structure output.")
            return

        # Create a list to store all tasks that we'll await concurrently
        tasks = []
        
        # For each file specification, create and launch an async task
        for file_spec in files:
            task = asyncio.create_task(
                self._generate_file_code(file_spec)
            )
            tasks.append(task)
        
        # Wait for all file generation tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Process results (store in state, etc.)
        for result in results:
            if result:  # Skip any None results
                filename, content = result
                # Store in state dictionary
                self.state.generatedCodeFiles[filename] = content
                
                # Write the file to disk
                self._write_file_to_disk(filename, content)
        
        print(f"=== Generated {len(self.state.generatedCodeFiles)} code files ===")

    @listen(write_code_files)
    def generate_assets(self):
        """
        Generate game assets based on specifications created by the AssetGenerationCrew.
        The crew will return a structured AssetSpecCollection, which we'll use to generate
        the actual assets using the tools in custom_tool.py.
        """
        print("=== Starting Asset Generation Phase ===")

        # Create asset directories
        try:
            os.makedirs("./Game/assets/images", exist_ok=True)
            os.makedirs("./Game/assets/audio", exist_ok=True)
            os.makedirs("./assets/images", exist_ok=True)
            os.makedirs("./assets/audio", exist_ok=True)
            os.makedirs("./public/assets/images", exist_ok=True)
            os.makedirs("./public/assets/audio", exist_ok=True)
            print("Created asset directories")
        except OSError as e:
            print(f"Warning: Could not create asset directories: {e}")

        # Import the tools we'll need for generation
        from unemploymentstudios.tools.custom_tool import GenerateAndDownloadImageTool, SearchAndSaveSoundTool
        
        # Test if API keys are available
        print(f"OPENAI_API_KEY available: {bool(os.getenv('OPENAI_API_KEY'))}")
        print(f"FREESOUND_API_KEY available: {bool(os.getenv('FREESOUND_API_KEY'))}")
        
        # Initialize the tools
        image_tool = GenerateAndDownloadImageTool()
        audio_tool = SearchAndSaveSoundTool()

        # 1. Run the AssetGenerationCrew to get specifications
        try:
            expanded_concept = GameConcept(**json.loads(self.state.conceptExpansionOutput))
            asset_inputs = {
                "main_character": expanded_concept.main_character.model_dump(),
                "supporting_characters": [c.model_dump() for c in expanded_concept.supporting_characters],
                "world_building": expanded_concept.world_building,
                "levels": [l.model_dump() for l in expanded_concept.levels],
                "visual_style": expanded_concept.visual_style,
                "audio_style": expanded_concept.audio_style,
                "title": expanded_concept.title
            }

            print(f"Prepared asset inputs: {asset_inputs.keys()}")

            # 2. Kick off the AssetGenerationCrew to get specifications
            print("Starting AssetGenerationCrew for specification generation...")
            asset_result = (
                AssetGenerationCrew()
                .crew()
                .kickoff(inputs=asset_inputs)
            )
            
            # Store the raw output for reference
            self.state.assetGenerationOutput = asset_result.raw
            
            # Parse the output as an AssetSpecCollection
            try:
                # Try to parse directly with model_validate_json (Pydantic v2 method)
                from pydantic import TypeAdapter
                asset_specs = TypeAdapter(AssetSpecCollection).validate_json(self.state.assetGenerationOutput)
                print(f"Successfully parsed asset specifications: {len(asset_specs.image_assets)} images, {len(asset_specs.audio_assets)} audio")
            except Exception as e:
                print(f"Error parsing asset specifications: {e}")
                # Attempt to extract JSON from the output if it's not pure JSON
                import re
                json_match = re.search(r'```json\n(.*?)\n```', self.state.assetGenerationOutput, re.DOTALL)
                if json_match:
                    try:
                        # Extract the JSON from markdown code blocks
                        json_content = json_match.group(1)
                        # Remove any non-JSON content
                        asset_specs = TypeAdapter(AssetSpecCollection).validate_json(json_content)
                        print(f"Successfully parsed asset specifications from markdown: {len(asset_specs.image_assets)} images, {len(asset_specs.audio_assets)} audio")
                    except Exception as e2:
                        print(f"Error parsing asset specifications from markdown: {e2}")
                        # Try to fix the common issues in the JSON
                        try:
                            # Parse as regular JSON first to fix structure
                            import json
                            json_data = json.loads(json_content)
                            
                            # Fix common field issues
                            if "image_assets" in json_data:
                                for img in json_data["image_assets"]:
                                    if "prompt" not in img:
                                        img["prompt"] = f"Game asset: {img.get('asset_id', 'unknown')}"
                                    if "style" not in img:
                                        img["style"] = "pixel art"
                            
                            if "audio_assets" in json_data:
                                for audio in json_data["audio_assets"]:
                                    if "query" not in audio:
                                        audio["query"] = f"game sound {audio.get('asset_id', 'effect')}"
                                    # Convert numeric duration to string
                                    if "desired_duration" in audio and not isinstance(audio["desired_duration"], str):
                                        audio["desired_duration"] = str(audio["desired_duration"])
                            
                            # Create the asset specs with the fixed data
                            asset_specs = AssetSpecCollection(**json_data)
                            print(f"Fixed and parsed asset specifications: {len(asset_specs.image_assets)} images, {len(asset_specs.audio_assets)} audio")
                        except Exception as e3:
                            print(f"Error fixing asset specifications: {e3}")
                            # Create fallback specifications
                            asset_specs = self._create_fallback_asset_specs()
                else:
                    # Create fallback specifications
                    asset_specs = self._create_fallback_asset_specs()
            
            # 3. Generate the actual assets from the specifications
            self._generate_assets_from_specs(asset_specs, image_tool, audio_tool)
            
            # 4. Copy everything into ./Game/assets/
            print("Running _organise_generated_assets...")
            self._organise_generated_assets()
            
            # 5. Save specifications for reference
            try:
                with open("./Game/asset_specifications.json", "w") as f:
                    # Use model_dump_json instead of json (Pydantic v2 method)
                    f.write(asset_specs.model_dump_json(indent=2))
                print("Saved asset specifications to ./Game/asset_specifications.json")
            except Exception as e:
                print(f"Error saving asset specifications: {e}")

            print("Asset generation & copying complete.")

        except Exception as e:
            print(f"[Asset Generation] Error: {e}")
            # Create and generate fallback assets
            fallback_specs = self._create_fallback_asset_specs()
            self._generate_assets_from_specs(fallback_specs, image_tool, audio_tool)
            self._organise_generated_assets()
            
        print("=== Asset Generation Phase Complete ===")

    def _create_fallback_asset_specs(self) -> 'AssetSpecCollection':
        """Create fallback asset specifications if the crew output can't be parsed."""
        from unemploymentstudios.types import AssetSpecCollection, ImageAssetSpec, AudioAssetSpec
        
        # Create minimal set of image specifications
        image_assets = [
            ImageAssetSpec(
                asset_id="main_character",
                asset_type="character",
                filename="./assets/images/main_character.png",
                prompt="A hero character for a video game with determined expression, detailed pixel art style",
                style="pixel art",
                importance=1,
                description="The main player character for the game"
            ),
            ImageAssetSpec(
                asset_id="enemy",
                asset_type="character",
                filename="./assets/images/enemy.png",
                prompt="A menacing enemy character for a video game, detailed pixel art style",
                style="pixel art",
                importance=1,
                description="A standard enemy character"
            ),
            ImageAssetSpec(
                asset_id="background",
                asset_type="environment",
                filename="./assets/images/background.png",
                prompt="A beautiful game background landscape, pixel art style",
                style="pixel art",
                importance=1,
                description="The main background for the game levels"
            ),
            ImageAssetSpec(
                asset_id="ui_button",
                asset_type="ui",
                filename="./assets/images/ui_button.png",
                prompt="A stylish game UI button in pixel art style",
                style="pixel art",
                importance=2,
                description="Button for the game's user interface"
            ),
            ImageAssetSpec(
                asset_id="logo",
                asset_type="ui",
                filename="./assets/images/logo.png",
                prompt="A game logo with stylized text, pixel art style",
                style="pixel art",
                importance=1,
                description="The game's main logo"
            )
        ]
        
        # Create minimal set of audio specifications
        audio_assets = [
            AudioAssetSpec(
                asset_id="background_music",
                asset_type="music",
                filename="./assets/audio/background_music.mp3",
                query="game background music",
                description="Background music for the main game",
                importance=1
            ),
            AudioAssetSpec(
                asset_id="jump_sound",
                asset_type="effect",
                filename="./assets/audio/jump_sound.mp3",
                query="game jump sound effect",
                description="Sound effect when the player jumps",
                importance=1
            ),
            AudioAssetSpec(
                asset_id="collect_item",
                asset_type="effect",
                filename="./assets/audio/collect_item.mp3",
                query="game collect item sound",
                description="Sound effect when the player collects an item",
                importance=2
            )
        ]
        
        return AssetSpecCollection(image_assets=image_assets, audio_assets=audio_assets)

    def _generate_assets_from_specs(self, asset_specs: 'AssetSpecCollection', image_tool, audio_tool):
        """Generate assets based on the provided specifications."""
        # Track successful generations
        successful_images = []
        successful_audio = []
        
        # Generate images with rate limiting protection
        print(f"Generating {len(asset_specs.image_assets)} images...")
        
        # Limit to a smaller number of images to avoid rate limiting
        max_images_to_generate = min(3, len(asset_specs.image_assets))
        
        for i, img_spec in enumerate(asset_specs.image_assets[:max_images_to_generate]):
            try:
                print(f"Generating image: {img_spec.filename} ({img_spec.asset_id})")
                
                # Add delay between requests to avoid rate limiting
                if i > 0:
                    import time
                    print("Waiting to avoid rate limiting...")
                    time.sleep(2)  # 2 second delay between requests
                
                # Add retry logic
                retry_count = 0
                max_retries = 3
                while retry_count < max_retries:
                    try:
                        result_str = image_tool._run(
                            prompt=img_spec.prompt,
                            file_name=img_spec.filename
                        )
                        self.state.generatedImages[img_spec.asset_id] = img_spec.filename
                        successful_images.append(img_spec.asset_id)
                        print(f"Generated image: {img_spec.filename}")
                        break  # Success, exit retry loop
                    except Exception as retry_error:
                        retry_count += 1
                        if "429" in str(retry_error) and retry_count < max_retries:
                            # Rate limit error, wait longer and retry
                            wait_time = 5 * retry_count  # Progressive backoff
                            print(f"Rate limit encountered. Waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                            time.sleep(wait_time)
                        else:
                            # Other error or max retries reached
                            raise
            except Exception as e:
                print(f"Error generating image {img_spec.asset_id}: {e}")
        
        # Generate audio with similar protection
        print(f"Generating {len(asset_specs.audio_assets)} audio files...")
        
        # Limit to a smaller number of audio files
        max_audio_to_generate = min(3, len(asset_specs.audio_assets))
        
        for i, audio_spec in enumerate(asset_specs.audio_assets[:max_audio_to_generate]):
            try:
                print(f"Generating audio: {audio_spec.filename} ({audio_spec.asset_id})")
                
                # Add delay between requests
                if i > 0:
                    import time
                    time.sleep(1)  # 1 second delay between requests
                
                # Add retry logic
                retry_count = 0
                max_retries = 3
                while retry_count < max_retries:
                    try:
                        result_str = audio_tool._run(
                            query=audio_spec.query,
                            output_path=audio_spec.filename
                        )
                        self.state.generatedSounds[audio_spec.asset_id] = audio_spec.filename
                        successful_audio.append(audio_spec.asset_id)
                        print(f"Generated audio: {audio_spec.filename}")
                        break  # Success, exit retry loop
                    except Exception as retry_error:
                        retry_count += 1
                        if retry_count < max_retries:
                            # Any error, wait and retry
                            wait_time = 3 * retry_count  # Progressive backoff
                            print(f"Error encountered. Waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                            time.sleep(wait_time)
                        else:
                            # Max retries reached
                            raise
            except Exception as e:
                print(f"Error generating audio {audio_spec.asset_id}: {e}")
        
        # Save manifests
        if successful_images:
            image_manifest = {asset_id: {"file": self.state.generatedImages[asset_id]} 
                             for asset_id in successful_images}
            os.makedirs("./assets", exist_ok=True)
            with open("./assets/manifest_images.json", "w") as f:
                json.dump(image_manifest, f, indent=2)
                
        if successful_audio:
            audio_manifest = {asset_id: {"file": self.state.generatedSounds[asset_id]} 
                             for asset_id in successful_audio}
            os.makedirs("./assets", exist_ok=True)
            with open("./assets/manifest_audio.json", "w") as f:
                json.dump(audio_manifest, f, indent=2)
                
        print(f"Successfully generated {len(successful_images)} images and {len(successful_audio)} audio files")

    # -----------------------------------------------------------------------
    #                          NEW helper methods
    # -----------------------------------------------------------------------
    def _organise_generated_assets(self):
        """
        Copy manifests + actual files produced by AssetGenerationCrew into
        the canonical ./Game/assets folder.
        """
        game_assets_root = pathlib.Path("./Game/assets")
        images_dir = game_assets_root / "images"
        audio_dir = game_assets_root / "audio"
        game_assets_root.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        audio_dir.mkdir(exist_ok=True)

        # default locations produced by our crew
        crew_assets_root = pathlib.Path("./assets")
        public_root = pathlib.Path("./public/assets")  # in case Integrator used this

        # 1️⃣ Copy manifest files if they exist
        for src in [
            crew_assets_root / "manifest_images.json",
            crew_assets_root / "manifest_audio.json",
            public_root / "manifest_images.json",
            public_root / "manifest_audio.json",
        ]:
            if src.exists():
                shutil.copy2(src, game_assets_root / src.name)

        # 2️⃣ Walk through likely asset locations and copy files
        for candidate_root in [crew_assets_root, public_root]:
            if not candidate_root.exists():
                continue
            for path in candidate_root.rglob("*"):
                if path.is_file():
                    # Decide destination sub‑dir (images vs audio vs other)
                    lower = path.suffix.lower()
                    if lower in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                        dest = images_dir / path.name
                        shutil.copy2(path, dest)
                        self.state.generatedImages[path.name] = str(dest)
                    elif lower in {".wav", ".mp3", ".ogg"}:
                        dest = audio_dir / path.name
                        shutil.copy2(path, dest)
                        self.state.generatedSounds[path.name] = str(dest)
                    # else: ignore (could add fonts or fx later)

        # 3️⃣ Simple console summary
        print(f"  Copied {len(self.state.generatedImages)} images "
              f"and {len(self.state.generatedSounds)} audio files into Game/assets.")
    @listen(generate_assets)
    def test_game(self):
        """
        Run tests on the generated game code.
        """
        print("=== Starting Testing & QA Phase ===")
        
        try:
            # Create inputs for the testing and QA crew
            code_files = {filename: content for filename, content in self.state.generatedCodeFiles.items()}
            
            # Only include key files to avoid overwhelming the crew
            key_files = {
                k: v for k, v in code_files.items() 
                if k.endswith('.js') or k.endswith('.html') or k.endswith('.css')
            }
            
            # Simplify testing by only including essential files if there are too many
            if len(key_files) > 5:
                # Prioritize main files
                priority_files = {}
                for name in ['index.html', 'main.js', 'game.js', 'style.css']:
                    if name in key_files:
                        priority_files[name] = key_files[name]
                
                # If we don't have at least 3 files, add more until we do
                if len(priority_files) < 3:
                    for name, content in key_files.items():
                        if name not in priority_files:
                            priority_files[name] = content
                            if len(priority_files) >= 3:
                                break
                
                test_inputs = {"code_files": priority_files}
            else:
                test_inputs = {"code_files": key_files}
            
            # Add concept information
            if self.state.conceptExpansionOutput:
                test_inputs["game_concept"] = self.state.conceptExpansionOutput
            
            # Use TestingQACrew to test the game
            test_result = (
                TestingQACrew()
                .crew()
                .kickoff(inputs=test_inputs)
            )
            
            # Store the testing output
            self.state.testingQAOutput = test_result.raw
            
            # Save testing report to file
            with open("./Game/qa_report.txt", "w") as f:
                f.write(self.state.testingQAOutput)
                
            print("QA testing completed successfully")
            
        except Exception as e:
            print(f"Error in testing phase: {str(e)}")
            
            # Create a minimal test report as fallback
            test_report = """
            # Game Test Report
            
            A comprehensive test of the generated game code would be performed here.
            
            ## Testing Areas
            - Functionality testing
            - Performance testing
            - Usability testing
            - Compatibility testing
            
            ## Results
            Placeholder for test results
            """
            
            # Write test report to file
            with open("./Game/test_report.md", "w") as f:
                f.write(test_report)
                
            print("Created fallback test_report.md")
            
        print("=== Testing & QA Phase Complete ===")

    @listen(test_game)
    def finalize_game(self):
        """
        Final steps to prepare the game for deployment.
        """
        print("=== Game Finalization Phase ===")
        
        # Create a README.md for the game
        readme_content = f"""
        # {self.state.Storyline.split()[0] if self.state.Storyline else "Game"} - Generated by UnemploymentStudios
        
        This game was automatically generated using CrewAI and UnemploymentStudios.
        
        ## How to Run
        
        1. Open the `index.html` file in a modern web browser
        2. Alternatively, use a local server:
           ```
           python -m http.server
           ```
           Then visit http://localhost:8000
        
        ## Game Concept
        
        {self.state.Storyline}
        
        ## Game Mechanics
        
        {self.state.Game_Mechanics}
        
        ## Credits
        
        Generated by UnemploymentStudios using CrewAI
        """
        
        # Write README to file
        with open("./Game/README.md", "w") as f:
            f.write(readme_content)
            
        print("Created README.md for the game")
        
        # Create an index.html launcher if it doesn't exist
        # This ensures we have at least one working file to preview the game
        if not os.path.exists("./Game/index.html"):
            fallback_index = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Game by UnemploymentStudios</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f0f0f0; }
                    .game-container { width: 800px; height: 600px; margin: 20px auto; background-color: #fff; border: 2px solid #333; }
                    header { text-align: center; padding: 20px; }
                    footer { text-align: center; padding: 10px; font-size: 0.8em; color: #666; }
                </style>
            </head>
            <body>
                <header>
                    <h1>Game by UnemploymentStudios</h1>
                </header>
                
                <div class="game-container" id="game-container">
                    <h2 style="text-align: center; padding-top: 250px;">Game Loading...</h2>
                </div>
                
                <footer>
                    <p>Created with CrewAI and UnemploymentStudios</p>
                </footer>
                
                <script>
                    // Check if game.js exists, otherwise display a message
                    document.addEventListener('DOMContentLoaded', function() {
                        const gameScript = document.createElement('script');
                        gameScript.src = 'game.js';
                        gameScript.onerror = function() {
                            document.getElementById('game-container').innerHTML = 
                                '<div style="text-align: center; padding-top: 250px;"><h2>Game files are still being generated</h2>' +
                                '<p>Check the generated files in the Game directory</p></div>';
                        };
                        document.body.appendChild(gameScript);
                    });
                </script>
            </body>
            </html>
            """
            
            with open("./Game/index.html", "w") as f:
                f.write(fallback_index)
                
            print("Created fallback index.html")
        
        print("=== Game Generation Complete ===")
        print("")
        print("Your game has been generated in the ./Game directory!")
        print("Open ./Game/index.html in a web browser to play.")
        print("View ./Game/file_structure.txt for the codebase organization.")
        print("View ./Game/game_concept.txt for the detailed game concept.")
        print("")

def kickoff():
    game_flow = GameFlow()
    flow_result = game_flow.kickoff()

def plot():
    return "UnemploymentStudios Flow Diagram"

if __name__ == "__main__":
    start_time = time.perf_counter()
    
    # Display welcome message
    print("")
    print("=" * 80)
    print("               UnemploymentStudios Game Generator                ")
    print("=" * 80)
    print("This tool will generate a complete web-based game using CrewAI.")
    print("The process takes several minutes as multiple AI agents work together.")
    print("=" * 80)
    print("")
    
    # Start the flow
    kickoff()

    end_time = time.perf_counter()
    print(f"Execution time: {end_time - start_time:.4f} seconds")
