from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai import LLM
from typing import List, Dict, Any, Optional
import os
import json
import re

# Import our models
from unemployedstudios.crews.asset_generation_crew.models import AssetSpecCollection, ImageAssetSpec, AudioAssetSpec

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AssetGenerationCrew:
    """Asset Generation Crew for game development
    
    This crew is responsible for:
    - Analyzing asset requirements based on the game concept and style guide
    - Creating specifications for visual assets (characters, environments, UI)
    - Creating specifications for audio assets (sound effects, music)
    - Compiling all specifications into a structured collection
    
    The specifications are then used by the main program to generate or source the actual assets.
    """
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    # Configuration paths
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    # Define the LLM to use for this crew
    llm = LLM(model="openai/gpt-4o")
    
    def __init__(self):
        # Create output directory if it doesn't exist
        os.makedirs("GameGenerationOutput/assets/images", exist_ok=True)
        os.makedirs("GameGenerationOutput/assets/audio", exist_ok=True)
    
    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    
    @agent
    def asset_specification_agent(self) -> Agent:
        """Asset Specification Agent responsible for analyzing and compiling asset requirements"""
        return Agent(
            config=self.agents_config["asset_specification_agent"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def visual_asset_agent(self) -> Agent:
        """Visual Asset Agent responsible for creating detailed specifications for character and environment assets"""
        return Agent(
            config=self.agents_config["visual_asset_agent"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def ui_asset_agent(self) -> Agent:
        """UI Asset Agent responsible for creating detailed specifications for UI elements"""
        return Agent(
            config=self.agents_config["ui_asset_agent"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def audio_asset_agent(self) -> Agent:
        """Audio Asset Agent responsible for creating detailed specifications for sound effects and music"""
        return Agent(
            config=self.agents_config["audio_asset_agent"],
            llm=self.llm,
            verbose=True
        )
    
    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def analyze_asset_requirements(self) -> Task:
        """Analyze game concept and style guide to create list of required assets"""
        return Task(
            config=self.tasks_config["analyze_asset_requirements"]
        )
    
    @task
    def specify_visual_assets(self) -> Task:
        """Create detailed specifications for visual assets using ImageAssetSpec model"""
        return Task(
            config=self.tasks_config["specify_visual_assets"],
            context=[self.analyze_asset_requirements()]
        )
    
    @task
    def specify_ui_assets(self) -> Task:
        """Create detailed specifications for UI assets using ImageAssetSpec model"""
        return Task(
            config=self.tasks_config["specify_ui_assets"],
            context=[self.analyze_asset_requirements()]
        )
    
    @task
    def specify_audio_assets(self) -> Task:
        """Create detailed specifications for audio assets using AudioAssetSpec model"""
        return Task(
            config=self.tasks_config["specify_audio_assets"],
            context=[self.analyze_asset_requirements()]
        )
    
    @task
    def compile_asset_specifications(self) -> Task:
        """Compile all asset specifications into a structured collection"""
        return Task(
            config=self.tasks_config["compile_asset_specifications"],
            context=[
                self.specify_visual_assets(),
                self.specify_ui_assets(),
                self.specify_audio_assets()
            ],
            output_pydantic=AssetSpecCollection
        )
    
    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Create the asset generation crew"""
        return Crew(
            agents=[
                self.asset_specification_agent(),
                self.visual_asset_agent(),
                self.ui_asset_agent(),
                self.audio_asset_agent()
            ],
            tasks=[
                self.analyze_asset_requirements(),
                self.specify_visual_assets(),
                self.specify_ui_assets(),
                self.specify_audio_assets(),
                self.compile_asset_specifications()
            ],
            process=Process.sequential,
            verbose=True
        )
        
    # --------------------------------------------------
    # VALIDATION METHODS
    # --------------------------------------------------
    
    def validate_asset_specifications(self, specs: AssetSpecCollection) -> Dict[str, Any]:
        """
        Validates the asset specifications before processing
        Returns a dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "image_assets": {
                "valid_count": 0,
                "invalid_count": 0
            },
            "audio_assets": {
                "valid_count": 0,
                "invalid_count": 0
            }
        }
        
        # Validate image assets
        if specs.image_assets:
            for idx, asset in enumerate(specs.image_assets):
                try:
                    # Validate image size (must be one of the allowed sizes)
                    allowed_sizes = ["1024x1024", "1792x1024", "1024x1792"]
                    if asset.size not in allowed_sizes:
                        err_msg = f"Image asset '{asset.asset_id}' has invalid size: {asset.size}. Must be one of: {', '.join(allowed_sizes)}"
                        validation_results["errors"].append(err_msg)
                        validation_results["image_assets"]["invalid_count"] += 1
                        
                        # Auto-fix the size by setting it to 1024x1024
                        print(f"Auto-fixing invalid size for {asset.asset_id} to 1024x1024")
                        asset.size = "1024x1024"
                        continue
                    
                    # Validate model name
                    allowed_models = ["gpt-image-1", "dall-e-2", "dall-e-3"]
                    if asset.model not in allowed_models:
                        err_msg = f"Image asset '{asset.asset_id}' has invalid model: {asset.model}. Must be one of: {', '.join(allowed_models)}"
                        validation_results["errors"].append(err_msg)
                        validation_results["image_assets"]["invalid_count"] += 1
                        
                        # Auto-fix the model by setting it to dall-e-3
                        print(f"Auto-fixing invalid model for {asset.asset_id} to dall-e-3")
                        asset.model = "dall-e-3"
                        continue
                    
                    # Validate filename
                    if not asset.filename.endswith((".png", ".jpg", ".jpeg")):
                        validation_results["warnings"].append(
                            f"Image asset '{asset.asset_id}' has filename without standard image extension: {asset.filename}"
                        )
                    
                    # Validate prompt length
                    if len(asset.prompt) < 20:
                        validation_results["warnings"].append(
                            f"Image asset '{asset.asset_id}' has short prompt ({len(asset.prompt)} chars) which may not generate good results"
                        )
                    
                    # Mark as valid
                    validation_results["image_assets"]["valid_count"] += 1
                
                except Exception as e:
                    validation_results["errors"].append(f"Error validating image asset #{idx}: {str(e)}")
                    validation_results["image_assets"]["invalid_count"] += 1
        
        # Validate audio assets
        if specs.audio_assets:
            for idx, asset in enumerate(specs.audio_assets):
                try:
                    # Set query from search_terms if not provided
                    if not asset.query and asset.search_terms:
                        asset.query = asset.search_terms
                    
                    # Validate search terms
                    if not asset.search_terms and not asset.query:
                        err_msg = f"Audio asset '{asset.asset_id}' missing both search_terms and query"
                        validation_results["errors"].append(err_msg)
                        validation_results["audio_assets"]["invalid_count"] += 1
                        
                        # Add fallback search terms
                        fallback_terms = f"game sound {asset.asset_id} {asset.asset_type}"
                        print(f"Auto-adding fallback search terms for {asset.asset_id}: {fallback_terms}")
                        asset.search_terms = fallback_terms
                        continue
                    
                    # Validate filename
                    if not asset.filename.endswith((".mp3", ".wav", ".ogg")):
                        validation_results["warnings"].append(
                            f"Audio asset '{asset.asset_id}' has filename without standard audio extension: {asset.filename}"
                        )
                    
                    # Validate query/search_terms length
                    search_string = asset.query or asset.search_terms
                    if len(search_string) < 5:
                        validation_results["warnings"].append(
                            f"Audio asset '{asset.asset_id}' has short search string ({len(search_string)} chars) which may not return good results"
                        )
                        
                        # Add more descriptive search terms
                        enhanced_terms = f"game sound {asset.asset_id} {asset.asset_type}"
                        print(f"Auto-enhancing short search terms for {asset.asset_id}: {enhanced_terms}")
                        asset.search_terms = enhanced_terms
                    
                    # Make search terms more effective based on our testing
                    if search_string and "search term enhanced" not in search_string:
                        # Enhance search terms based on asset type
                        asset_type = asset.asset_type.lower()
                        if asset_type == "effect" and "sound effect" not in search_string.lower():
                            validation_results["warnings"].append(
                                f"Audio asset '{asset.asset_id}' may benefit from adding 'sound effect' to search terms"
                            )
                            # Auto-enhance the search terms
                            enhanced_terms = f"{asset.search_terms}, sound effect (search term enhanced)"
                            print(f"Auto-enhancing search terms for {asset.asset_id}: {enhanced_terms}")
                            asset.search_terms = enhanced_terms
                            
                        elif asset_type == "music" and "8-bit" not in search_string.lower():
                            validation_results["warnings"].append(
                                f"Audio asset '{asset.asset_id}' may benefit from adding '8-bit' to search terms for better game music results"
                            )
                            # Auto-enhance the search terms
                            enhanced_terms = f"{asset.search_terms}, 8-bit (search term enhanced)"
                            print(f"Auto-enhancing search terms for {asset.asset_id}: {enhanced_terms}")
                            asset.search_terms = enhanced_terms
                            
                        elif "game sound" not in search_string.lower():
                            validation_results["warnings"].append(
                                f"Audio asset '{asset.asset_id}' may benefit from adding 'game sound' to search terms"
                            )
                            # Auto-enhance the search terms
                            enhanced_terms = f"{asset.search_terms}, game sound (search term enhanced)"
                            print(f"Auto-enhancing search terms for {asset.asset_id}: {enhanced_terms}")
                            asset.search_terms = enhanced_terms
                    
                    # Mark as valid
                    validation_results["audio_assets"]["valid_count"] += 1
                
                except Exception as e:
                    validation_results["errors"].append(f"Error validating audio asset #{idx}: {str(e)}")
                    validation_results["audio_assets"]["invalid_count"] += 1
        
        # Update overall validation status - still return errors but many are now fixed
        if validation_results["errors"]:
            validation_results["valid"] = False
            validation_results["warnings"].append("Auto-fixed some validation issues, but manual review recommended")
        
        return validation_results
    
    def extract_asset_specs_from_output(self, output):
        """Extract asset specifications from crew output, with robust error handling"""
        try:
            # If the output is already a proper AssetSpecCollection, return it
            if isinstance(output, AssetSpecCollection):
                return output
            
            # If output has a specific attribute for the specs
            if hasattr(output, 'compile_asset_specifications'):
                return output.compile_asset_specifications
            
            # Try to parse from raw output
            if hasattr(output, 'raw'):
                # Try direct JSON parsing first
                try:
                    specs_data = json.loads(output.raw)
                    
                    # Fix search_terms arrays by converting them to strings
                    if isinstance(specs_data, dict) and 'audio_assets' in specs_data:
                        for audio in specs_data.get('audio_assets', []):
                            if isinstance(audio, dict) and 'search_terms' in audio and isinstance(audio['search_terms'], list):
                                audio['search_terms'] = ' '.join(audio['search_terms'])
                    
                    return AssetSpecCollection(**specs_data)
                except Exception as json_err:
                    print(f"Error parsing raw output as JSON: {str(json_err)}")
                    
                    # Try to extract JSON from markdown code blocks
                    try:
                        json_match = re.search(r'```json\n(.*?)\n```', output.raw, re.DOTALL)
                        if json_match:
                            json_content = json_match.group(1)
                            specs_data = json.loads(json_content)
                            
                            # Fix search_terms arrays by converting them to strings
                            if isinstance(specs_data, dict) and 'audio_assets' in specs_data:
                                for audio in specs_data.get('audio_assets', []):
                                    if isinstance(audio, dict) and 'search_terms' in audio and isinstance(audio['search_terms'], list):
                                        audio['search_terms'] = ' '.join(audio['search_terms'])
                            
                            return AssetSpecCollection(**specs_data)
                    except Exception as md_err:
                        print(f"Error extracting JSON from markdown: {str(md_err)}")
            
            # If all else fails, try to convert to a string and parse
            try:
                # Try to fix the string representation if it might contain lists for search_terms
                str_output = str(output)
                
                # This is a crude approach but might help in some cases - try to detect and fix list patterns
                # Example: search_terms=['a', 'b', 'c'] -> search_terms='a b c'
                list_pattern = r"search_terms=\[(.*?)\]"
                
                def replace_list_with_string(match):
                    list_content = match.group(1)
                    # Split by commas and clean up quotes
                    items = [item.strip().strip("'\"") for item in list_content.split(',')]
                    return f"search_terms='{' '.join(items)}'"
                
                fixed_output = re.sub(list_pattern, replace_list_with_string, str_output)
                
                return AssetSpecCollection.parse_raw(fixed_output)
            except Exception as parse_err:
                print(f"Error parsing output as string: {str(parse_err)}")
                
            # If we still can't parse it, create a minimal fallback
            print("Creating fallback asset specifications")
            return self._create_fallback_asset_specs()
            
        except Exception as e:
            print(f"Error extracting asset specs: {str(e)}")
            return self._create_fallback_asset_specs()

    def _create_fallback_asset_specs(self):
        """Create fallback asset specifications if the crew output can't be parsed."""
        # Create minimal set of image specifications
        image_assets = [
            ImageAssetSpec(
                asset_id="main_character",
                asset_type="character",
                filename="assets/images/main_character.png",
                prompt="A computer science student character for a pixel art platformer game, wearing casual clothes with a laptop backpack",
                style="minimalist pixel art",
                importance=1,
                description="The main player character for Code Quest"
            ),
            ImageAssetSpec(
                asset_id="syntax_error_enemy",
                asset_type="character",
                filename="assets/images/syntax_error_enemy.png",
                prompt="A glitchy, error-like monster character in pixel art style with red highlights",
                style="minimalist pixel art",
                importance=1,
                description="A standard enemy character representing syntax errors"
            ),
            ImageAssetSpec(
                asset_id="university_background",
                asset_type="environment",
                filename="assets/images/university_background.png",
                prompt="A pixel art university campus background with computer labs and classrooms",
                style="minimalist pixel art",
                importance=1,
                description="The background for the University level"
            )
        ]
        
        # Create minimal set of audio specifications
        audio_assets = [
            AudioAssetSpec(
                asset_id="jump_sound",
                asset_type="effect",
                filename="assets/audio/jump_sound.mp3",
                search_terms="game jump sound effect 8-bit",
                description="Sound effect when the player jumps",
                importance=1
            ),
            AudioAssetSpec(
                asset_id="collect_code",
                asset_type="effect",
                filename="assets/audio/collect_code.mp3",
                search_terms="game collect item sound positive 8-bit",
                description="Sound effect when the player collects a code snippet",
                importance=1
            )
        ]
        
        return AssetSpecCollection(image_assets=image_assets, audio_assets=audio_assets)
