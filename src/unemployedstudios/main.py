#!/usr/bin/env python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from crewai.flow import Flow, listen, start, router, and_
from unemployedstudios.crews.concept_crew import ConceptCrew
from unemployedstudios.crews.concept_crew.models import ConceptExpansion, GameDesignDocument, TechnicalArchitecture, StyleGuide, GameplayMechanic, Character, Enemy, Level, MonetizationStrategy
from unemployedstudios.crews.technical_design_crew import TechnicalDesignCrew
from unemployedstudios.crews.engine_crew import EngineCrew
from unemployedstudios.crews.entity_crew import EntityCrew
from unemployedstudios.crews.level_crew import LevelCrew
from unemployedstudios.crews.ui_crew import UICrew
from unemployedstudios.crews.asset_generation_crew import AssetGenerationCrew, AssetSpecCollection
from unemployedstudios.tools.custom_tool import GenerateAndDownloadImageTool, SearchAndSaveSoundTool
import json
import os
import re

class GameDevelopmentState(BaseModel):
    # Initial inputs
    game_concept: str = ""
    game_template_path: str = "game_template.html"
    
    # Concept Phase outputs (structured with Pydantic models)
    concept_expansion: Optional[ConceptExpansion] = None
    game_design_document: Optional[GameDesignDocument] = None
    technical_architecture: Optional[TechnicalArchitecture] = None
    style_guide: Optional[StyleGuide] = None
    
    # Technical Design Phase outputs
    template_analysis: Optional[Dict[str, Any]] = None
    core_systems_design: Optional[Dict[str, Any]] = None
    component_interfaces: Optional[Dict[str, Any]] = None
    integration_mapping: Optional[Dict[str, Any]] = None
    design_validation: Optional[Dict[str, Any]] = None
    refined_technical_design: Optional[Dict[str, Any]] = None
    
    # Template integration points
    template_css_insertion_point: Optional[str] = None
    template_audio_insertion_point: Optional[str] = None
    template_game_ui_insertion_point: Optional[str] = None
    template_game_logic_insertion_point: Optional[str] = None
    template_game_class_insertion_point: Optional[str] = None
    
    # Code Generation Phase outputs (now segmented for template insertion)
    game_engine_segments: Optional[Dict[str, str]] = None
    game_entities_segments: Optional[Dict[str, str]] = None
    game_levels_segments: Optional[Dict[str, str]] = None
    game_ui_segments: Optional[Dict[str, str]] = None
    
    # Legacy code generation outputs (maintained for backward compatibility)
    game_engine_file: Optional[str] = None
    game_entities_file: Optional[str] = None
    game_levels_file: Optional[str] = None
    game_ui_file: Optional[str] = None
    
    # Status tracking
    concept_phase_complete: bool = False
    technical_design_phase_complete: bool = False
    engine_development_complete: bool = False
    entity_development_complete: bool = False
    level_development_complete: bool = False
    ui_development_complete: bool = False
    template_integration_complete: bool = False
    
    # Validation and refinement tracking
    validation_results: Optional[Dict[str, Any]] = None
    refinement_iterations: int = 0
    validation_phase_complete: bool = False
    refinement_phase_complete: bool = False
    max_refinement_iterations: int = 3
    convergence_threshold: float = 0.1  # Improvement threshold for convergence
    
    # Asset Generation Phase outputs
    asset_specifications: Optional[AssetSpecCollection] = None
    generated_image_assets: Optional[Dict[str, str]] = None
    generated_audio_assets: Optional[Dict[str, str]] = None
    asset_generation_complete: bool = False

class GameDevelopmentFlow(Flow[GameDevelopmentState]):
    """
    Game Development Flow that orchestrates the creation of a complete HTML5 game
    Following the architecture defined in the flow architecture document
    """
    
    def _get_output_path(self, filename: str) -> str:
        """Helper method to generate consistent output file paths"""
        # Ensure the output directory exists
        os.makedirs("GameGenerationOutput", exist_ok=True)
        
        # Return the full path to the output file
        return os.path.join("GameGenerationOutput", filename)
        
    @start()
    def initialize_flow(self):
        """Entry point for the game development flow"""
        print("Starting Game Development Flow")
        
        # Create GameGenerationOutput directory if it doesn't exist
        os.makedirs("GameGenerationOutput", exist_ok=True)
        
        # Set the template path to use the game_template.html from project root
        self.state.game_template_path = "game_template.html"
        print(f"Using game template from: {self.state.game_template_path}")
        
        # Game concept for "Code Quest: CS Student Journey"
        self.state.game_concept = """
        Create a 2D platformer called "Code Quest" where players control a computer science student navigating 
        through academic challenges to become a software developer. The game features:
        
        - Simple platformer mechanics (run, jump, solve puzzles)
        - Coding-themed collectibles and obstacles
        - Three distinct level environments (University, Internship, Job Hunt)
        - Mini coding puzzles that unlock new paths
        - A progression system where players gain programming skills
        - Boss battles in the form of "technical interviews"
        
        The visual style is minimalist pixel art with a color scheme reflecting programming themes.
        The game should be accessible to non-programmers while including CS concepts that students 
        and developers will appreciate.
        """
        
        return "Flow initialized with 'Code Quest' game concept"
    
    @listen(initialize_flow)
    def concept_phase(self):
        """
        Concept Phase of the Game Development Flow
        
        This phase includes:
        - Concept Expansion
        - Game Design Document Creation
        - Architecture Planning
        - Style Guide Definition
        """
        print("Starting Concept Phase")
        
        # Run the Concept Crew with the initial game concept
        concept_output = (
            ConceptCrew()
            .crew()
            .kickoff(inputs={
                "game_concept": self.state.game_concept
            })
        )
        
        # Create GameGenerationOutput directory
        os.makedirs("GameGenerationOutput", exist_ok=True)
        
        # Process and save output
        try:
            # Store raw output as structured JSON
            if hasattr(concept_output, 'raw'):
                # Save raw output for debugging if needed
                with open(self._get_output_path("debug_raw_output.json"), "w") as f:
                    f.write(concept_output.raw)
                
                # Parse the raw output to ensure it's valid JSON
                try:
                    concept_data = json.loads(concept_output.raw)
                except json.JSONDecodeError:
                    # If not valid JSON, wrap it in a content field
                    concept_data = {"content": concept_output.raw}
                    
                # Save the complete data to a single file
                with open(self._get_output_path("concept_phase_output.json"), "w") as f:
                    json.dump(concept_data, f, indent=2)
                    
                # Store in state for direct access if needed
                # We'll still try to parse into Pydantic models for type safety if possible
                try:
                    self.state.concept_expansion = ConceptExpansion.parse_obj(concept_data)
                    print("Successfully parsed concept expansion")
                except Exception as e:
                    print(f"Note: Could not parse concept expansion: {str(e)}")
                    self.state.concept_expansion = None
                    
                # Print some statistics if available
                if isinstance(concept_data, dict):
                    if "title" in concept_data:
                        print(f"Concept Expansion completed with title: {concept_data['title']}")
                    
                    # Log level information if available
                    if "levels" in concept_data and isinstance(concept_data["levels"], list):
                        print(f"Game has {len(concept_data['levels'])} levels defined:")
                        for i, level in enumerate(concept_data["levels"]):
                            if isinstance(level, dict) and "name" in level and "theme" in level:
                                print(f"  - Level {i+1}: {level['name']} ({level['theme']})")
                    
                    # Log enemy information if available
                    if "enemies" in concept_data and isinstance(concept_data["enemies"], list):
                        print(f"Game has {len(concept_data['enemies'])} enemy types defined:")
                        for i, enemy in enumerate(concept_data["enemies"]):
                            if isinstance(enemy, dict) and "name" in enemy and "difficulty" in enemy:
                                print(f"  - Enemy {i+1}: {enemy['name']} (Difficulty: {enemy['difficulty']})")
                    
                    # Log mechanics information if available
                    if "gameplay_mechanics" in concept_data and isinstance(concept_data["gameplay_mechanics"], list):
                        print(f"Game mechanics ({len(concept_data['gameplay_mechanics'])}):")
                        for i, mechanic in enumerate(concept_data["gameplay_mechanics"]):
                            if isinstance(mechanic, dict) and "name" in mechanic and "implementation_complexity" in mechanic:
                                print(f"  - {mechanic['name']}: {mechanic['implementation_complexity']} complexity")
            else:
                raw_output = str(concept_output)
                print("No structured raw output available, saving as string")
                with open(self._get_output_path("concept_phase_output.json"), "w") as f:
                    json.dump({"raw_content": raw_output}, f, indent=2)
                    
        except Exception as e:
            print(f"Error processing crew output: {str(e)}")
            raise ValueError(f"Failed to process crew output: {str(e)}")
        
        # Mark the concept phase as complete
        self.state.concept_phase_complete = True
        
        return "Concept Phase completed successfully with structured outputs"
    
    @listen(concept_phase)
    def technical_design_phase(self):
        """
        Technical Design Phase of the Game Development Flow
        
        This phase includes:
        - Template Analysis
        - Integration Planning
        - Component Interface Definition
        - Design Validation and Refinement
        """
        print("Starting Technical Design Phase")
        
        # Create GameGenerationOutput directory if it doesn't exist yet
        os.makedirs("GameGenerationOutput", exist_ok=True)
        
        # Load the concept phase output
        try:
            with open(self._get_output_path("concept_phase_output.json"), "r") as f:
                concept_data = json.load(f)
                
            # Extract sections needed for technical design
            concept_expansion_dict = concept_data
            game_design_document_dict = concept_data
            technical_architecture_dict = concept_data
            style_guide_dict = concept_data
            
            print("Successfully loaded concept phase output")
        except Exception as e:
            print(f"Error loading concept phase output: {str(e)}")
            
            # Try to load debug raw output as fallback
            try:
                with open(self._get_output_path("debug_raw_output.json"), "r") as f:
                    raw_output = f.read()
                    
                # Try to parse as JSON
                try:
                    concept_data = json.loads(raw_output)
                except:
                    concept_data = {"content": raw_output}
                    
                concept_expansion_dict = concept_data
                game_design_document_dict = concept_data
                technical_architecture_dict = concept_data
                style_guide_dict = concept_data
                
                print("Using debug raw output as fallback")
            except Exception as e2:
                print(f"Error loading fallback output: {str(e2)}")
                raise ValueError("Missing required concept phase output and could not load fallback files")
        
        # Extract mechanic names from the concept_data if available
        mechanic_names = []
        try:
            if isinstance(concept_data, dict) and 'gameplay_mechanics' in concept_data:
                mechanics = concept_data.get('gameplay_mechanics', [])
                if isinstance(mechanics, list):
                    for mechanic in mechanics:
                        if isinstance(mechanic, dict) and 'name' in mechanic:
                            mechanic_names.append(mechanic['name'])
                        
            # If no mechanics found, use a default list based on the game concept
            if not mechanic_names:
                mechanic_names = ["Platform Movement", "Coding Puzzles", "Collectibles System", "Level Progression"]
                
            print(f"Using mechanic names: {mechanic_names}")
        except Exception as e:
            print(f"Error extracting mechanic names: {str(e)}")
            mechanic_names = ["Platform Movement", "Coding Puzzles", "Collectibles System", "Level Progression"]
        
        # Extract level names from the concept_data if available
        level_names = []
        try:
            if isinstance(concept_data, dict) and 'levels' in concept_data:
                levels = concept_data.get('levels', [])
                if isinstance(levels, list):
                    for level in levels:
                        if isinstance(level, dict) and 'name' in level:
                            level_names.append(level['name'])
                        
            # If no levels found, use a default list based on the game concept
            if not level_names:
                level_names = ["University", "Internship", "Job Hunt"]
                
            print(f"Using level names: {level_names}")
        except Exception as e:
            print(f"Error extracting level names: {str(e)}")
            level_names = ["University", "Internship", "Job Hunt"]
        
        # Add system names
        system_names = ["Rendering", "Input", "Physics", "Entity", "Level", "UI", "Audio"]
        print(f"Using system names: {system_names}")
        
        # Extract enemy names from the concept_data if available
        enemy_names = []
        try:
            if isinstance(concept_data, dict) and 'enemies' in concept_data:
                enemies = concept_data.get('enemies', [])
                if isinstance(enemies, list):
                    for enemy in enemies:
                        if isinstance(enemy, dict) and 'name' in enemy:
                            enemy_names.append(enemy['name'])
                        
            # If no enemies found, use a default list based on the game concept
            if not enemy_names:
                enemy_names = ["Syntax Error", "Logic Bug", "Deadline Demon", "Memory Leak", "Infinite Loop"]
                
            print(f"Using enemy names: {enemy_names}")
        except Exception as e:
            print(f"Error extracting enemy names: {str(e)}")
            enemy_names = ["Syntax Error", "Logic Bug", "Deadline Demon", "Memory Leak", "Infinite Loop"]
            
        # Set up default game template path if not already specified
        if not self.state.game_template_path:
            self.state.game_template_path = self._get_output_path("template.html")
            print(f"Using default template path: {self.state.game_template_path}")
            
            # Copy the game_template.html file from the project root if it exists
            if os.path.exists("game_template.html"):
                import shutil
                shutil.copy("game_template.html", self.state.game_template_path)
                print(f"Copied game_template.html from project root to {self.state.game_template_path}")
            else:
                print("Warning: game_template.html not found in project root. Integration may fail.")
                
            # Set default template integration points if not specified
            if not self.state.template_css_insertion_point:
                self.state.template_css_insertion_point = "/*Your style goes here */"
                print(f"Set default CSS insertion point: {self.state.template_css_insertion_point}")
                
            if not self.state.template_audio_insertion_point:
                self.state.template_audio_insertion_point = "<!--Extra audio tags for sound effects-->"
                print(f"Set default audio insertion point: {self.state.template_audio_insertion_point}")
                
            if not self.state.template_game_ui_insertion_point:
                self.state.template_game_ui_insertion_point = "class GameUI {"
                print(f"Set default GameUI insertion point: {self.state.template_game_ui_insertion_point}")
                
            if not self.state.template_game_logic_insertion_point:
                self.state.template_game_logic_insertion_point = "class GameLogic {"
                print(f"Set default GameLogic insertion point: {self.state.template_game_logic_insertion_point}")
                
            if not self.state.template_game_class_insertion_point:
                self.state.template_game_class_insertion_point = "class Game {"
                print(f"Set default Game class insertion point: {self.state.template_game_class_insertion_point}")
        
        # Run the Technical Design Crew with outputs from the Concept Phase
        tech_design_output = (
            TechnicalDesignCrew()
            .crew()
            .kickoff(inputs={
                "game_concept": self.state.game_concept,
                "concept_expansion": concept_expansion_dict,
                "game_design_document": game_design_document_dict,
                "technical_architecture": technical_architecture_dict,
                "style_guide": style_guide_dict,
                "mechanic_names": mechanic_names,
                "level_names": level_names,
                "system_names": system_names,
                "enemy_names": enemy_names,
                "game_template_path": self.state.game_template_path
            })
        )
        
        # Store the raw output for debugging if needed
        with open(self._get_output_path("debug_tech_output.json"), "w") as f:
            if hasattr(tech_design_output, 'raw'):
                f.write(tech_design_output.raw)
            else:
                f.write(str(tech_design_output))
        
        # Process outputs
        try:
            # Save the entire technical design output as a single JSON file
            if hasattr(tech_design_output, 'raw'):
                try:
                    tech_design_data = json.loads(tech_design_output.raw)
                    with open(self._get_output_path("technical_design_output.json"), "w") as f:
                        json.dump(tech_design_data, f, indent=2)
                    
                    # Store in state for convenience
                    self.state.technical_design_data = tech_design_data
                    
                    # Also extract specific outputs if available - now including template analysis
                    if hasattr(tech_design_output, 'template_analysis_task'):
                        self.state.template_analysis = tech_design_output.template_analysis_task
                        print("Successfully extracted template analysis")
                    else:
                        self.state.template_analysis = tech_design_data
                    
                    if hasattr(tech_design_output, 'core_systems_design_task'):
                        self.state.core_systems_design = tech_design_output.core_systems_design_task
                        print("Successfully extracted core systems design")
                    else:
                        self.state.core_systems_design = tech_design_data
                    
                    if hasattr(tech_design_output, 'interface_definition_task'):
                        self.state.component_interfaces = tech_design_output.interface_definition_task
                        print("Successfully extracted component interfaces")
                    else:
                        self.state.component_interfaces = tech_design_data
                    
                    if hasattr(tech_design_output, 'integration_mapping_task'):
                        self.state.integration_mapping = tech_design_output.integration_mapping_task
                        print("Successfully extracted integration mapping")
                    else:
                        self.state.integration_mapping = tech_design_data
                    
                    if hasattr(tech_design_output, 'design_validation_task'):
                        self.state.design_validation = tech_design_output.design_validation_task
                        print("Successfully extracted design validation")
                    else:
                        self.state.design_validation = tech_design_data
                    
                    if hasattr(tech_design_output, 'design_refinement_task'):
                        self.state.refined_technical_design = tech_design_output.design_refinement_task
                        print("Successfully extracted refined technical design")
                    else:
                        self.state.refined_technical_design = tech_design_data
                    
                    # Extract template insertion points from integration mapping if available
                    if self.state.integration_mapping and isinstance(self.state.integration_mapping, dict):
                        if 'css_insertion_point' in self.state.integration_mapping:
                            self.state.template_css_insertion_point = self.state.integration_mapping['css_insertion_point']
                            print(f"Set CSS insertion point: {self.state.template_css_insertion_point}")
                            
                        if 'audio_insertion_point' in self.state.integration_mapping:
                            self.state.template_audio_insertion_point = self.state.integration_mapping['audio_insertion_point']
                            print(f"Set audio insertion point: {self.state.template_audio_insertion_point}")
                            
                        if 'game_ui_insertion_point' in self.state.integration_mapping:
                            self.state.template_game_ui_insertion_point = self.state.integration_mapping['game_ui_insertion_point']
                            print(f"Set GameUI insertion point: {self.state.template_game_ui_insertion_point}")
                            
                        if 'game_logic_insertion_point' in self.state.integration_mapping:
                            self.state.template_game_logic_insertion_point = self.state.integration_mapping['game_logic_insertion_point']
                            print(f"Set GameLogic insertion point: {self.state.template_game_logic_insertion_point}")
                            
                        if 'game_class_insertion_point' in self.state.integration_mapping:
                            self.state.template_game_class_insertion_point = self.state.integration_mapping['game_class_insertion_point']
                            print(f"Set Game class insertion point: {self.state.template_game_class_insertion_point}")
                    
                except json.JSONDecodeError:
                    # If not valid JSON, wrap it in a content field
                    with open(self._get_output_path("technical_design_output.json"), "w") as f:
                        json.dump({"content": tech_design_output.raw}, f, indent=2)
                        
                    self.state.template_analysis = {"content": tech_design_output.raw}
                    self.state.core_systems_design = {"content": tech_design_output.raw}
                    self.state.component_interfaces = {"content": tech_design_output.raw}
                    self.state.integration_mapping = {"content": tech_design_output.raw}
                    self.state.design_validation = {"content": tech_design_output.raw}
                    self.state.refined_technical_design = {"content": tech_design_output.raw}
            else:
                raw_output = str(tech_design_output)
                with open(self._get_output_path("technical_design_output.json"), "w") as f:
                    json.dump({"content": raw_output}, f, indent=2)
                    
                self.state.template_analysis = {"content": raw_output}
                self.state.core_systems_design = {"content": raw_output}
                self.state.component_interfaces = {"content": raw_output}
                self.state.integration_mapping = {"content": raw_output}
                self.state.design_validation = {"content": raw_output}
                self.state.refined_technical_design = {"content": raw_output}
        except Exception as e:
            print(f"Error processing technical design output: {str(e)}")
            # Continue anyway - we've saved the raw outputs
        
        # Mark the technical design phase as complete
        self.state.technical_design_phase_complete = True
        
        print("Technical Design Phase completed successfully with template integration planning")
        
        return "Technical Design Phase completed successfully with template integration planning"
    
    @router(condition=technical_design_phase)
    def route_to_next_phase(self):
        """Route to the next phase based on the current state"""
        if self.state.technical_design_phase_complete:
            print("Technical Design Phase completed. Moving to Code Generation Phase with Template Integration.")
            
            # Ensure we have required template information before proceeding
            if not self.state.template_analysis:
                print("Warning: Template analysis is missing. This may cause issues with integration.")
            
            if not self.state.integration_mapping:
                print("Warning: Integration mapping is missing. This may cause issues with code generation.")
            
            # Verify template insertion points are defined
            if not (self.state.template_game_class_insertion_point or 
                    self.state.template_game_logic_insertion_point or 
                    self.state.template_game_ui_insertion_point):
                print("Warning: No template insertion points defined. Using default integration approach.")
            
            # Initialize the parallel code generation phase by triggering the engine crew
            # Other crews will be triggered in parallel through the engine_crew_generation event
            return self.initiate_code_generation
        elif self.state.concept_phase_complete:
            print("Concept Phase completed. Moving to Technical Design Phase with Template Analysis.")
            return self.technical_design_phase
        else:
            # If concept phase isn't complete, this shouldn't happen
            print("Error: Concept Phase was not completed successfully.")
            return None
    
    @listen(route_to_next_phase)
    def initiate_code_generation(self):
        """
        Initiate the Code Generation Phase with parallel crew execution
        
        This method starts all code generation crews in parallel using the appropriate
        events based on the CrewAI Flow architecture
        """
        print("Initiating parallel Code Generation Phase")
        
        # Start all crews in parallel - each will proceed independently
        # The template integration will only happen after all crews have completed
        self.engine_crew_generation()
        self.entity_crew_generation()
        self.level_crew_generation()
        self.ui_crew_generation()
        
        return "Parallel Code Generation Phase initiated"

    @listen(initiate_code_generation)
    def engine_crew_generation(self):
        """
        Core Engine Development Phase of the Game Development Flow
        
        This phase is responsible for:
        - Game loop integration with template
        - Rendering pipeline extensions
        - Input handling system enhancements
        - Performance optimization for template
        """
        print("Starting Core Engine Development Phase with Template Integration")
        
        # Run the Engine Crew with the technical design outputs including template information
        engine_output = (
            EngineCrew()
            .crew()
            .kickoff(inputs={
                # Core technical design information
                "core_systems_design": self.state.core_systems_design,
                "component_interfaces": self.state.component_interfaces,
                "refined_technical_design": self.state.refined_technical_design,
                
                # Template integration information
                "template_analysis": self.state.template_analysis,
                "integration_mapping": self.state.integration_mapping,
                "game_template_path": self.state.game_template_path,
                
                # Template insertion points
                "template_game_class_insertion_point": self.state.template_game_class_insertion_point,
                "template_game_logic_insertion_point": self.state.template_game_logic_insertion_point
            })
        )
        
        # Process the output
        try:
            # Store the raw output for debugging
            with open(self._get_output_path("debug_engine_output.json"), "w") as f:
                if hasattr(engine_output, 'raw'):
                    f.write(engine_output.raw)
                else:
                    f.write(str(engine_output))
            
            # Initialize segments dictionary if not exists
            if self.state.game_engine_segments is None:
                self.state.game_engine_segments = {}
            
            # Process segmented code output for template integration
            if hasattr(engine_output, 'game_class_extensions'):
                # Store code segments for template integration
                self.state.game_engine_segments['game_class'] = engine_output.game_class_extensions
                print(f"Successfully generated Game class extensions ({len(engine_output.game_class_extensions)} bytes)")
                
            if hasattr(engine_output, 'game_logic_extensions'):
                self.state.game_engine_segments['game_logic'] = engine_output.game_logic_extensions
                print(f"Successfully generated GameLogic extensions ({len(engine_output.game_logic_extensions)} bytes)")
            
            # Try to parse raw output if attributes are missing
            if hasattr(engine_output, 'raw') and (
                'game_class' not in self.state.game_engine_segments or 
                not self.state.game_engine_segments.get('game_class') or
                'game_logic' not in self.state.game_engine_segments or 
                not self.state.game_engine_segments.get('game_logic')
            ):
                try:
                    # Try to parse as JSON
                    engine_data = json.loads(engine_output.raw)
                    
                    # Store segments by type
                    if 'game_class' in engine_data and ('game_class' not in self.state.game_engine_segments or not self.state.game_engine_segments['game_class']):
                        self.state.game_engine_segments['game_class'] = engine_data['game_class']
                        print(f"Parsed Game class extensions from raw output")
                    
                    if 'game_logic' in engine_data and ('game_logic' not in self.state.game_engine_segments or not self.state.game_engine_segments['game_logic']):
                        self.state.game_engine_segments['game_logic'] = engine_data['game_logic']
                        print(f"Parsed GameLogic extensions from raw output")
                    
                except json.JSONDecodeError:
                    print("Raw output is not valid JSON, trying regex extraction")
                    # Try to extract segments using regex
                    import re
                    
                    if 'game_class' not in self.state.game_engine_segments or not self.state.game_engine_segments['game_class']:
                        # Try different regex patterns to extract game class code
                        patterns = [
                            r'```javascript\s*// Game Class Extensions\s*(.*?)```',
                            r'```js\s*// Game Class Extensions\s*(.*?)```',
                            r'```javascript\s*(.*?class\s+Game.*?)```',
                            r'// GAME_CLASS EXTENSIONS\s*(.*?)(?://|$)',
                            r'class Game\s*{(.*?)}'
                        ]
                        
                        for pattern in patterns:
                            game_class_match = re.search(pattern, engine_output.raw, re.DOTALL)
                            if game_class_match:
                                self.state.game_engine_segments['game_class'] = game_class_match.group(1).strip()
                                print(f"Extracted Game class extensions using regex pattern: {pattern}")
                                break
                    
                    if 'game_logic' not in self.state.game_engine_segments or not self.state.game_engine_segments['game_logic']:
                        # Try different regex patterns to extract game logic code
                        patterns = [
                            r'```javascript\s*// Game Logic Extensions\s*(.*?)```',
                            r'```js\s*// Game Logic Extensions\s*(.*?)```',
                            r'```javascript\s*(.*?update\(.*?\).*?)```',
                            r'// GAME_LOGIC EXTENSIONS\s*(.*?)(?://|$)',
                            r'update\(.*?\)\s*{(.*?)}'
                        ]
                        
                        for pattern in patterns:
                            game_logic_match = re.search(pattern, engine_output.raw, re.DOTALL)
                            if game_logic_match:
                                self.state.game_engine_segments['game_logic'] = game_logic_match.group(1).strip()
                                print(f"Extracted GameLogic extensions using regex pattern: {pattern}")
                                break
            
            # For backward compatibility, still check for the standalone file
            engine_file_path = "GameGenerationOutput/game_engine.js"
            if os.path.exists(engine_file_path):
                with open(engine_file_path, "r") as f:
                    engine_code = f.read()
                self.state.game_engine_file = engine_code
                print(f"Also found legacy game_engine.js ({len(engine_code)} bytes)")
                
                # Extract segments from file if not already set
                if 'game_class' not in self.state.game_engine_segments or not self.state.game_engine_segments['game_class']:
                    import re
                    game_class_match = re.search(r'// GAME_CLASS EXTENSIONS\s*(.*?)// ', engine_code, re.DOTALL)
                    if game_class_match:
                        self.state.game_engine_segments['game_class'] = game_class_match.group(1).strip()
                        print(f"Extracted Game class extensions from file")
                
                if 'game_logic' not in self.state.game_engine_segments or not self.state.game_engine_segments['game_logic']:
                    game_logic_match = re.search(r'// GAME_LOGIC EXTENSIONS\s*(.*?)// ', engine_code, re.DOTALL)
                    if game_logic_match:
                        self.state.game_engine_segments['game_logic'] = game_logic_match.group(1).strip()
                        print(f"Extracted GameLogic extensions from file")
            else:
                # If crew returned structured segments but no legacy file, compile them
                if self.state.game_engine_segments:
                    combined_code = "// Engine Extensions for Template Integration\n\n"
                    for segment_name, segment_code in self.state.game_engine_segments.items():
                        combined_code += f"// {segment_name.upper()} EXTENSIONS\n{segment_code}\n\n"
                    
                    self.state.game_engine_file = combined_code
                    with open(engine_file_path, "w") as f:
                        f.write(combined_code)
                    print(f"Created legacy game_engine.js from segments ({len(combined_code)} bytes)")
                else:
                    # Still fall back to any final integration task
                    if hasattr(engine_output, 'final_integration_task'):
                        self.state.game_engine_file = engine_output.final_integration_task
                        with open(engine_file_path, "w") as f:
                            f.write(engine_output.final_integration_task)
                        print(f"Extracted game_engine.js from output ({len(engine_output.final_integration_task)} bytes)")
                    else:
                        print("Warning: No engine code segments or files were generated")
            
            # Create hardcoded fallback files with default content if no segments were found
            if not self.state.game_engine_segments or not self.state.game_engine_segments.get('game_class'):
                fallback_game_class = """
                // Default Game class extensions
                initializeGameObjects() {
                    console.log("Initializing game objects with fallback implementation");
                    this.player = {
                        x: 100,
                        y: 100,
                        width: 32,
                        height: 32,
                        speed: 5
                    };
                    this.gameObjects = [this.player];
                }
                
                handleInput(keys) {
                    // Basic input handling
                    if(keys.ArrowRight) this.player.x += this.player.speed;
                    if(keys.ArrowLeft) this.player.x -= this.player.speed;
                    if(keys.ArrowUp) this.player.y -= this.player.speed;
                    if(keys.ArrowDown) this.player.y += this.player.speed;
                }
                """
                self.state.game_engine_segments['game_class'] = fallback_game_class
                print("Added fallback Game class extensions")
                
            if not self.state.game_engine_segments or not self.state.game_engine_segments.get('game_logic'):
                fallback_game_logic = """
                // Default Game logic extensions
                update(deltaTime) {
                    console.log("Updating game with fallback implementation");
                    // Basic collision detection
                    this.checkBoundaries();
                }
                
                checkBoundaries() {
                    // Keep player within game boundaries
                    if(this.player.x < 0) this.player.x = 0;
                    if(this.player.y < 0) this.player.y = 0;
                    if(this.player.x > 800 - this.player.width) this.player.x = 800 - this.player.width;
                    if(this.player.y > 600 - this.player.height) this.player.y = 600 - this.player.height;
                }
                """
                self.state.game_engine_segments['game_logic'] = fallback_game_logic
                print("Added fallback GameLogic extensions")
        except Exception as e:
            print(f"Error processing engine output: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Add fallback content even in case of exception
            self.state.game_engine_segments = self.state.game_engine_segments or {}
            if 'game_class' not in self.state.game_engine_segments:
                self.state.game_engine_segments['game_class'] = "// FALLBACK: Error occurred during engine code processing\nconsole.log('Using fallback engine code');"
            if 'game_logic' not in self.state.game_engine_segments:
                self.state.game_engine_segments['game_logic'] = "// FALLBACK: Error occurred during engine code processing\nconsole.log('Using fallback engine logic');"
        
        # Mark the engine development phase as complete
        self.state.engine_development_complete = True
        
        print("Core Engine Development Phase completed successfully with template integration")
        
        return "Core Engine Development Phase completed successfully with template integration"

    @listen(initiate_code_generation)
    def entity_crew_generation(self):
        """
        Entity System Development Phase of the Game Development Flow
        
        This phase is responsible for:
        - Entity system integration with template
        - Component system extensions
        - Physics system integration with template game loop
        - Entity behavior patterns and AI
        """
        print("Starting Entity System Development Phase with Template Integration")
        
        # Run the Entity Crew with the technical design outputs and template information
        entity_output = (
            EntityCrew()
            .crew()
            .kickoff(inputs={
                # Primary technical design inputs
                "core_systems_design": self.state.core_systems_design,
                "component_interfaces": self.state.component_interfaces,
                "concept_expansion": self.state.concept_expansion,  # For enemy information
                "refined_technical_design": self.state.refined_technical_design,
                
                # Template integration information
                "template_analysis": self.state.template_analysis,
                "integration_mapping": self.state.integration_mapping,
                "game_template_path": self.state.game_template_path,
                
                # Template insertion points
                "template_game_logic_insertion_point": self.state.template_game_logic_insertion_point,
                
                # Previously generated engine segments/code
                "game_engine_segments": self.state.game_engine_segments,
                "game_engine_file": self.state.game_engine_file  # For backward compatibility
            })
        )
        
        # Process the output
        try:
            # Store the raw output for debugging
            with open(self._get_output_path("debug_entity_output.json"), "w") as f:
                if hasattr(entity_output, 'raw'):
                    f.write(entity_output.raw)
                else:
                    f.write(str(entity_output))
            
            # Initialize segments dictionary if not exists
            if self.state.game_entities_segments is None:
                self.state.game_entities_segments = {}
            
            # Process segmented code output for template integration
            if hasattr(entity_output, 'game_logic_extensions'):
                # Store code segments for template integration
                self.state.game_entities_segments['game_logic'] = entity_output.game_logic_extensions
                print(f"Successfully generated GameLogic entity extensions ({len(entity_output.game_logic_extensions)} bytes)")
            
            # Try to parse raw output if attributes are missing
            if hasattr(entity_output, 'raw') and (
                'game_logic' not in self.state.game_entities_segments or 
                not self.state.game_entities_segments.get('game_logic')
            ):
                try:
                    # Try to parse as JSON
                    entity_data = json.loads(entity_output.raw)
                    
                    # Store segments by type
                    if 'game_logic' in entity_data and ('game_logic' not in self.state.game_entities_segments or not self.state.game_entities_segments['game_logic']):
                        self.state.game_entities_segments['game_logic'] = entity_data['game_logic']
                        print(f"Parsed GameLogic entity extensions from raw output")
                
                except json.JSONDecodeError:
                    print("Raw output is not valid JSON, trying regex extraction")
                    # Try to extract segments using regex
                    import re
                    
                    if 'game_logic' not in self.state.game_entities_segments or not self.state.game_entities_segments['game_logic']:
                        # Try different regex patterns to extract entity logic code
                        patterns = [
                            r'```javascript\s*// Entity Logic Extensions\s*(.*?)```',
                            r'```js\s*// Entity Logic Extensions\s*(.*?)```',
                            r'```javascript\s*(.*?createEntities.*?)```',
                            r'// ENTITY_LOGIC EXTENSIONS\s*(.*?)(?://|$)',
                            r'// GAME_LOGIC EXTENSIONS\s*(.*?)(?://|$)',
                            r'createEntities\(\)\s*{(.*?)}'
                        ]
                        
                        for pattern in patterns:
                            game_logic_match = re.search(pattern, entity_output.raw, re.DOTALL)
                            if game_logic_match:
                                self.state.game_entities_segments['game_logic'] = game_logic_match.group(1).strip()
                                print(f"Extracted GameLogic entity extensions using regex pattern: {pattern}")
                                break
            
            # For backward compatibility, still check for the standalone file
            entity_file_path = "GameGenerationOutput/game_entities.js"
            if os.path.exists(entity_file_path):
                with open(entity_file_path, "r") as f:
                    entity_code = f.read()
                self.state.game_entities_file = entity_code
                print(f"Also found legacy game_entities.js ({len(entity_code)} bytes)")
                
                # Extract segments from file if not already set
                if 'game_logic' not in self.state.game_entities_segments or not self.state.game_entities_segments['game_logic']:
                    import re
                    game_logic_match = re.search(r'// GAME_LOGIC EXTENSIONS\s*(.*?)// ', entity_code, re.DOTALL)
                    if game_logic_match:
                        self.state.game_entities_segments['game_logic'] = game_logic_match.group(1).strip()
                        print(f"Extracted GameLogic entity extensions from file")
                    else:
                        # Try alternative pattern if the first one fails
                        game_logic_match = re.search(r'// GAME_LOGIC EXTENSIONS\s*(.*?)$', entity_code, re.DOTALL)
                        if game_logic_match:
                            self.state.game_entities_segments['game_logic'] = game_logic_match.group(1).strip()
                            print(f"Extracted GameLogic entity extensions from file (alt pattern)")
            else:
                # If crew returned structured segments but no legacy file, compile them
                if self.state.game_entities_segments:
                    combined_code = "// Entity Extensions for Template Integration\n\n"
                    for segment_name, segment_code in self.state.game_entities_segments.items():
                        combined_code += f"// {segment_name.upper()} EXTENSIONS\n{segment_code}\n\n"
                    
                    self.state.game_entities_file = combined_code
                    with open(entity_file_path, "w") as f:
                        f.write(combined_code)
                    print(f"Created legacy game_entities.js from segments ({len(combined_code)} bytes)")
                else:
                    # Still fall back to any final integration task
                    if hasattr(entity_output, 'legacy_integration_task'):
                        self.state.game_entities_file = entity_output.legacy_integration_task
                        with open(entity_file_path, "w") as f:
                            f.write(entity_output.legacy_integration_task)
                        print(f"Extracted game_entities.js from output ({len(entity_output.legacy_integration_task)} bytes)")
                    elif hasattr(entity_output, 'final_integration_task'):
                        self.state.game_entities_file = entity_output.final_integration_task
                        with open(entity_file_path, "w") as f:
                            f.write(entity_output.final_integration_task)
                        print(f"Extracted game_entities.js from output ({len(entity_output.final_integration_task)} bytes)")
                    else:
                        print("Warning: No entity code segments or files were generated")
                    
            # Create hardcoded fallback files with default content if no segments were found
            if not self.state.game_entities_segments or not self.state.game_entities_segments.get('game_logic'):
                fallback_entity_logic = """
                // Default Entity logic extensions
                createEntities() {
                    console.log("Creating entities with fallback implementation");
                    this.enemies = [];
                    
                    // Create a basic enemy
                    this.enemies.push({
                        x: 400,
                        y: 300,
                        width: 32,
                        height: 32,
                        speed: 2,
                        direction: 1
                    });
                    
                    // Add enemies to game objects
                    this.gameObjects = [...this.gameObjects, ...this.enemies];
                }
                
                updateEntities(deltaTime) {
                    // Basic enemy movement
                    for (let enemy of this.enemies) {
                        enemy.x += enemy.speed * enemy.direction;
                        
                        // Simple boundary check
                        if (enemy.x <= 0 || enemy.x >= 800 - enemy.width) {
                            enemy.direction *= -1;
                        }
                        
                        // Simple collision with player
                        if (this.checkCollision(this.player, enemy)) {
                            console.log("Player hit enemy!");
                        }
                    }
                }
                
                checkCollision(objA, objB) {
                    return objA.x < objB.x + objB.width &&
                           objA.x + objA.width > objB.x &&
                           objA.y < objB.y + objB.height &&
                           objA.y + objA.height > objB.y;
                }
                """
                self.state.game_entities_segments['game_logic'] = fallback_entity_logic
                print("Added fallback GameLogic entity extensions")
        except Exception as e:
            print(f"Error processing entity output: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Add fallback content even in case of exception
            self.state.game_entities_segments = self.state.game_entities_segments or {}
            if 'game_logic' not in self.state.game_entities_segments:
                self.state.game_entities_segments['game_logic'] = "// FALLBACK: Error occurred during entity code processing\nconsole.log('Using fallback entity code');"
        
        # Mark the entity development phase as complete
        self.state.entity_development_complete = True
        
        print("Entity System Development Phase completed successfully with template integration")
        
        return "Entity System Development Phase completed successfully with template integration"
        
    @listen(initiate_code_generation)
    def level_crew_generation(self):
        """
        Level System Development Phase of the Game Development Flow
        
        This phase is responsible for:
        - Level system integration with template
        - Map generation and management
        - Player progression tracking
        - Challenge balancing and difficulty progression
        """
        print("Starting Level System Development Phase with Template Integration")
        
        # Run the Level Crew with the technical design outputs and template information
        level_output = (
            LevelCrew()
            .crew()
            .kickoff(inputs={
                # Primary inputs as specified in requirements
                "core_systems_design": self.state.core_systems_design,
                "component_interfaces": self.state.component_interfaces,
                "concept_expansion": self.state.concept_expansion,  # For level information
                
                # Template integration information
                "template_analysis": self.state.template_analysis,
                "integration_mapping": self.state.integration_mapping,
                "game_template_path": self.state.game_template_path,
                
                # Template insertion points
                "template_game_logic_insertion_point": self.state.template_game_logic_insertion_point,
                "template_game_class_insertion_point": self.state.template_game_class_insertion_point,
                
                # Previously generated code
                "game_engine_file": self.state.game_engine_file,
                "game_entities_file": self.state.game_entities_file,
                "refined_technical_design": self.state.refined_technical_design
            })
        )
        
        # Process the output
        try:
            # Store the raw output for debugging
            with open(self._get_output_path("debug_level_output.json"), "w") as f:
                if hasattr(level_output, 'raw'):
                    f.write(level_output.raw)
                else:
                    f.write(str(level_output))
            
            # Initialize segments dictionary if not exists
            if self.state.game_levels_segments is None:
                self.state.game_levels_segments = {}
            
            # Process segmented code output for template integration
            if hasattr(level_output, 'game_logic_extensions'):
                # Store code segments for template integration
                self.state.game_levels_segments['game_logic'] = level_output.game_logic_extensions
                print(f"Successfully generated GameLogic level extensions ({len(level_output.game_logic_extensions)} bytes)")
                
            if hasattr(level_output, 'game_class_extensions'):
                self.state.game_levels_segments['game_class'] = level_output.game_class_extensions
                print(f"Successfully generated Game class level extensions ({len(level_output.game_class_extensions)} bytes)")
            
            # Try to parse raw output if attributes are missing
            if hasattr(level_output, 'raw') and (
                'game_logic' not in self.state.game_levels_segments or 
                not self.state.game_levels_segments.get('game_logic') or
                'game_class' not in self.state.game_levels_segments or 
                not self.state.game_levels_segments.get('game_class')
            ):
                try:
                    # Try to parse as JSON
                    level_data = json.loads(level_output.raw)
                    
                    # Store segments by type
                    if 'game_logic' in level_data and ('game_logic' not in self.state.game_levels_segments or not self.state.game_levels_segments['game_logic']):
                        self.state.game_levels_segments['game_logic'] = level_data['game_logic']
                        print(f"Parsed GameLogic level extensions from raw output")
                    
                    if 'game_class' in level_data and ('game_class' not in self.state.game_levels_segments or not self.state.game_levels_segments['game_class']):
                        self.state.game_levels_segments['game_class'] = level_data['game_class']
                        print(f"Parsed Game class level extensions from raw output")
                
                except json.JSONDecodeError:
                    print("Raw output is not valid JSON, trying regex extraction")
                    # Try to extract segments using regex
                    import re
                    
                    if 'game_logic' not in self.state.game_levels_segments or not self.state.game_levels_segments['game_logic']:
                        # Try different regex patterns to extract level logic code
                        patterns = [
                            r'```javascript\s*// Level Logic Extensions\s*(.*?)```',
                            r'```js\s*// Level Logic Extensions\s*(.*?)```',
                            r'```javascript\s*(.*?loadLevel.*?)```',
                            r'// LEVEL_LOGIC EXTENSIONS\s*(.*?)(?://|$)',
                            r'// GAME_LOGIC EXTENSIONS\s*(.*?)(?://|$)',
                            r'loadLevel\(.*?\)\s*{(.*?)}'
                        ]
                        
                        for pattern in patterns:
                            game_logic_match = re.search(pattern, level_output.raw, re.DOTALL)
                            if game_logic_match:
                                self.state.game_levels_segments['game_logic'] = game_logic_match.group(1).strip()
                                print(f"Extracted GameLogic level extensions using regex pattern: {pattern}")
                                break
                    
                    if 'game_class' not in self.state.game_levels_segments or not self.state.game_levels_segments['game_class']:
                        # Try different regex patterns to extract level class code
                        patterns = [
                            r'```javascript\s*// Level Class Extensions\s*(.*?)```',
                            r'```js\s*// Level Class Extensions\s*(.*?)```',
                            r'```javascript\s*(.*?initializeLevels.*?)```',
                            r'// LEVEL_CLASS EXTENSIONS\s*(.*?)(?://|$)',
                            r'// GAME_CLASS EXTENSIONS\s*(.*?)(?://|$)',
                            r'initializeLevels\(\)\s*{(.*?)}'
                        ]
                        
                        for pattern in patterns:
                            game_class_match = re.search(pattern, level_output.raw, re.DOTALL)
                            if game_class_match:
                                self.state.game_levels_segments['game_class'] = game_class_match.group(1).strip()
                                print(f"Extracted Game class level extensions using regex pattern: {pattern}")
                                break
            
            # For backward compatibility, still check for the standalone file
            level_file_path = "GameGenerationOutput/game_levels.js"
            if os.path.exists(level_file_path):
                with open(level_file_path, "r") as f:
                    level_code = f.read()
                self.state.game_levels_file = level_code
                print(f"Also found legacy game_levels.js ({len(level_code)} bytes)")
                
                # Extract segments from file if not already set
                if 'game_logic' not in self.state.game_levels_segments or not self.state.game_levels_segments['game_logic']:
                    import re
                    game_logic_match = re.search(r'// GAME_LOGIC EXTENSIONS\s*(.*?)// ', level_code, re.DOTALL)
                    if game_logic_match:
                        self.state.game_levels_segments['game_logic'] = game_logic_match.group(1).strip()
                        print(f"Extracted GameLogic level extensions from file")
                    else:
                        # Try alternative pattern if the first one fails
                        game_logic_match = re.search(r'// GAME_LOGIC EXTENSIONS\s*(.*?)$', level_code, re.DOTALL)
                        if game_logic_match:
                            self.state.game_levels_segments['game_logic'] = game_logic_match.group(1).strip()
                            print(f"Extracted GameLogic level extensions from file (alt pattern)")
                
                if 'game_class' not in self.state.game_levels_segments or not self.state.game_levels_segments['game_class']:
                    game_class_match = re.search(r'// GAME_CLASS EXTENSIONS\s*(.*?)// ', level_code, re.DOTALL)
                    if game_class_match:
                        self.state.game_levels_segments['game_class'] = game_class_match.group(1).strip()
                        print(f"Extracted Game class level extensions from file")
                    else:
                        # Try alternative pattern if the first one fails
                        game_class_match = re.search(r'// GAME_CLASS EXTENSIONS\s*(.*?)$', level_code, re.DOTALL)
                        if game_class_match:
                            self.state.game_levels_segments['game_class'] = game_class_match.group(1).strip()
                            print(f"Extracted Game class level extensions from file (alt pattern)")
            else:
                # If crew returned structured segments but no legacy file, compile them
                if self.state.game_levels_segments:
                    combined_code = "// Level Extensions for Template Integration\n\n"
                    for segment_name, segment_code in self.state.game_levels_segments.items():
                        combined_code += f"// {segment_name.upper()} EXTENSIONS\n{segment_code}\n\n"
                    
                    self.state.game_levels_file = combined_code
                    with open(level_file_path, "w") as f:
                        f.write(combined_code)
                    print(f"Created legacy game_levels.js from segments ({len(combined_code)} bytes)")
                else:
                    # Still fall back to any final integration task
                    if hasattr(level_output, 'final_integration_task'):
                        self.state.game_levels_file = level_output.final_integration_task
                        with open(level_file_path, "w") as f:
                            f.write(level_output.final_integration_task)
                        print(f"Extracted game_levels.js from output ({len(level_output.final_integration_task)} bytes)")
                    else:
                        print("Warning: No level code segments or files were generated")
                    
            # Create hardcoded fallback files with default content if no segments were found
            if not self.state.game_levels_segments or not self.state.game_levels_segments.get('game_logic'):
                fallback_level_logic = """
                // Default Level logic extensions
                loadLevel(levelNumber) {
                    console.log("Loading level with fallback implementation: " + levelNumber);
                    this.currentLevel = levelNumber;
                    this.levelData = {
                        platforms: [
                            {x: 0, y: 500, width: 800, height: 20},
                            {x: 200, y: 400, width: 100, height: 20},
                            {x: 400, y: 300, width: 100, height: 20},
                            {x: 600, y: 200, width: 100, height: 20}
                        ],
                        collectibles: [
                            {x: 250, y: 370, width: 20, height: 20, type: 'coin'},
                            {x: 450, y: 270, width: 20, height: 20, type: 'coin'},
                            {x: 650, y: 170, width: 20, height: 20, type: 'coin'}
                        ]
                    };
                    
                    // Add level objects to game objects
                    this.platforms = this.levelData.platforms;
                    this.collectibles = this.levelData.collectibles;
                    this.gameObjects = [...this.gameObjects, ...this.platforms, ...this.collectibles];
                }
                
                checkLevelCollisions() {
                    // Check platform collisions
                    for (let platform of this.platforms) {
                        if (this.player.y + this.player.height <= platform.y && 
                            this.player.y + this.player.height + this.player.velocity.y >= platform.y &&
                            this.player.x < platform.x + platform.width &&
                            this.player.x + this.player.width > platform.x) {
                            this.player.y = platform.y - this.player.height;
                            this.player.velocity.y = 0;
                            this.player.isJumping = false;
                        }
                    }
                    
                    // Check collectible collisions
                    for (let i = this.collectibles.length - 1; i >= 0; i--) {
                        const collectible = this.collectibles[i];
                        if (this.checkCollision(this.player, collectible)) {
                            console.log("Collected item: " + collectible.type);
                            this.collectibles.splice(i, 1);
                            // Remove from gameObjects too
                            const index = this.gameObjects.indexOf(collectible);
                            if (index > -1) {
                                this.gameObjects.splice(index, 1);
                            }
                        }
                    }
                }
                """
                self.state.game_levels_segments['game_logic'] = fallback_level_logic
                print("Added fallback GameLogic level extensions")
            
            if not self.state.game_levels_segments or not self.state.game_levels_segments.get('game_class'):
                fallback_level_class = """
                // Default Level class extensions
                initializeLevels() {
                    console.log("Initializing levels with fallback implementation");
                    this.levels = [1, 2, 3];
                    this.currentLevel = 1;
                    this.loadLevel(this.currentLevel);
                }
                
                nextLevel() {
                    if (this.currentLevel < this.levels.length) {
                        this.currentLevel++;
                        this.loadLevel(this.currentLevel);
                        return true;
                    }
                    return false;
                }
                
                resetLevel() {
                    this.loadLevel(this.currentLevel);
                }
                """
                self.state.game_levels_segments['game_class'] = fallback_level_class
                print("Added fallback Game class level extensions")
        except Exception as e:
            print(f"Error processing level output: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Add fallback content even in case of exception
            self.state.game_levels_segments = self.state.game_levels_segments or {}
            if 'game_logic' not in self.state.game_levels_segments:
                self.state.game_levels_segments['game_logic'] = "// FALLBACK: Error occurred during level code processing\nconsole.log('Using fallback level logic');"
            if 'game_class' not in self.state.game_levels_segments:
                self.state.game_levels_segments['game_class'] = "// FALLBACK: Error occurred during level code processing\nconsole.log('Using fallback level code');"
        
        # Mark the level development phase as complete
        self.state.level_development_complete = True
        
        print("Level System Development Phase completed successfully with template integration")
        
        return "Level System Development Phase completed successfully with template integration"

    @listen(initiate_code_generation)
    def ui_crew_generation(self):
        """
        UI System Development Phase of the Game Development Flow
        
        This phase is responsible for:
        - UI system integration with template
        - UI framework extensions
        - Responsive layouts and interfaces
        - UI animations and transitions
        """
        print("Starting UI System Development Phase with Template Integration")
        
        # Run the UI Crew with the style guide, technical design outputs, and template information
        ui_output = (
            UICrew()
            .crew()
            .kickoff(inputs={
                # Primary inputs as specified in requirements
                "style_guide": self.state.style_guide,  # For UI visual guidelines
                "component_interfaces": self.state.component_interfaces,  # For UI component interfaces
                "core_systems_design": self.state.core_systems_design,  # For UI system specifications
                
                # Template integration information
                "template_analysis": self.state.template_analysis,
                "integration_mapping": self.state.integration_mapping,
                "game_template_path": self.state.game_template_path,
                
                # Template insertion points
                "template_game_ui_insertion_point": self.state.template_game_ui_insertion_point,
                "template_css_insertion_point": self.state.template_css_insertion_point,
                "template_audio_insertion_point": self.state.template_audio_insertion_point,
                
                # Previously generated code
                "game_engine_file": self.state.game_engine_file,
                "game_entities_file": self.state.game_entities_file,
                "game_levels_file": self.state.game_levels_file
            })
        )
        
        # Process the output
        try:
            # Store the raw output for debugging
            with open(self._get_output_path("debug_ui_output.json"), "w") as f:
                if hasattr(ui_output, 'raw'):
                    f.write(ui_output.raw)
                else:
                    f.write(str(ui_output))
            
            # Initialize segments dictionary if not exists
            if self.state.game_ui_segments is None:
                self.state.game_ui_segments = {}
            
            # Process segmented code output for template integration
            if hasattr(ui_output, 'game_ui_extensions'):
                # Store code segments for template integration
                self.state.game_ui_segments['game_ui'] = ui_output.game_ui_extensions
                print(f"Successfully generated GameUI extensions ({len(ui_output.game_ui_extensions)} bytes)")
                
            if hasattr(ui_output, 'css_extensions'):
                self.state.game_ui_segments['css'] = ui_output.css_extensions
                print(f"Successfully generated CSS extensions ({len(ui_output.css_extensions)} bytes)")
                
            if hasattr(ui_output, 'audio_extensions'):
                self.state.game_ui_segments['audio'] = ui_output.audio_extensions
                print(f"Successfully generated audio extensions ({len(ui_output.audio_extensions)} bytes)")
            
            # Try to parse raw output if attributes are missing
            if hasattr(ui_output, 'raw') and (
                'game_ui' not in self.state.game_ui_segments or 
                not self.state.game_ui_segments.get('game_ui') or
                'css' not in self.state.game_ui_segments or 
                not self.state.game_ui_segments.get('css') or
                'audio' not in self.state.game_ui_segments or 
                not self.state.game_ui_segments.get('audio')
            ):
                try:
                    # Try to parse as JSON
                    ui_data = json.loads(ui_output.raw)
                    
                    # Store segments by type
                    if 'game_ui' in ui_data and ('game_ui' not in self.state.game_ui_segments or not self.state.game_ui_segments['game_ui']):
                        self.state.game_ui_segments['game_ui'] = ui_data['game_ui']
                        print(f"Parsed GameUI extensions from raw output")
                    
                    if 'css' in ui_data and ('css' not in self.state.game_ui_segments or not self.state.game_ui_segments['css']):
                        self.state.game_ui_segments['css'] = ui_data['css']
                        print(f"Parsed CSS extensions from raw output")
                    
                    if 'audio' in ui_data and ('audio' not in self.state.game_ui_segments or not self.state.game_ui_segments['audio']):
                        self.state.game_ui_segments['audio'] = ui_data['audio']
                        print(f"Parsed audio extensions from raw output")
                    
                except json.JSONDecodeError:
                    print("Raw output is not valid JSON, trying regex extraction")
                    # Try to extract segments using regex
                    import re
                    
                    if 'game_ui' not in self.state.game_ui_segments or not self.state.game_ui_segments['game_ui']:
                        # Try different regex patterns to extract UI code
                        patterns = [
                            r'```javascript\s*// UI Extensions\s*(.*?)```',
                            r'```js\s*// UI Extensions\s*(.*?)```',
                            r'```javascript\s*(.*?updateHUD.*?)```',
                            r'// UI EXTENSIONS\s*(.*?)(?://|$)',
                            r'// GAME_UI EXTENSIONS\s*(.*?)(?://|$)',
                            r'updateHUD\(\)\s*{(.*?)}'
                        ]
                        
                        for pattern in patterns:
                            game_ui_match = re.search(pattern, ui_output.raw, re.DOTALL)
                            if game_ui_match:
                                self.state.game_ui_segments['game_ui'] = game_ui_match.group(1).strip()
                                print(f"Extracted GameUI extensions using regex pattern: {pattern}")
                                break
                    
                    if 'css' not in self.state.game_ui_segments or not self.state.game_ui_segments['css']:
                        # Try different regex patterns to extract CSS code
                        patterns = [
                            r'```css\s*(.*?)```',
                            r'/\* CSS Extensions \*/\s*(.*?)(?:/\*|$)',
                            r'<style>\s*(.*?)</style>',
                            r'// CSS EXTENSIONS\s*(.*?)(?://|$)'
                        ]
                        
                        for pattern in patterns:
                            css_match = re.search(pattern, ui_output.raw, re.DOTALL)
                            if css_match:
                                self.state.game_ui_segments['css'] = css_match.group(1).strip()
                                print(f"Extracted CSS extensions using regex pattern: {pattern}")
                                break
                    
                    if 'audio' not in self.state.game_ui_segments or not self.state.game_ui_segments['audio']:
                        # Try different regex patterns to extract audio HTML code
                        patterns = [
                            r'```html\s*(.*?)```',
                            r'<!-- Audio Extensions -->\s*(.*?)(?:<!--|$)',
                            r'<audio.*?>(.*?)</audio>',
                            r'// AUDIO EXTENSIONS\s*(.*?)(?://|$)'
                        ]
                        
                        for pattern in patterns:
                            audio_match = re.search(pattern, ui_output.raw, re.DOTALL)
                            if audio_match:
                                self.state.game_ui_segments['audio'] = audio_match.group(1).strip()
                                print(f"Extracted audio extensions using regex pattern: {pattern}")
                                break
            
            # For backward compatibility, still check for the standalone file
            ui_file_path = "GameGenerationOutput/game_ui.js"
            if os.path.exists(ui_file_path):
                with open(ui_file_path, "r") as f:
                    ui_code = f.read()
                self.state.game_ui_file = ui_code
                print(f"Also found legacy game_ui.js ({len(ui_code)} bytes)")
                
                # Extract segments from file if not already set
                if 'game_ui' not in self.state.game_ui_segments or not self.state.game_ui_segments['game_ui']:
                    import re
                    game_ui_match = re.search(r'// GAME_UI EXTENSIONS\s*(.*?)// ', ui_code, re.DOTALL)
                    if game_ui_match:
                        self.state.game_ui_segments['game_ui'] = game_ui_match.group(1).strip()
                        print(f"Extracted GameUI extensions from file")
                    else:
                        # Try alternative pattern if the first one fails
                        game_ui_match = re.search(r'// GAME_UI EXTENSIONS\s*(.*?)$', ui_code, re.DOTALL)
                        if game_ui_match:
                            self.state.game_ui_segments['game_ui'] = game_ui_match.group(1).strip()
                            print(f"Extracted GameUI extensions from file (alt pattern)")
                
                # Check for CSS and audio files as well
                css_file_path = "GameGenerationOutput/css_extensions.css"
                if os.path.exists(css_file_path) and ('css' not in self.state.game_ui_segments or not self.state.game_ui_segments['css']):
                    with open(css_file_path, "r") as f:
                        css_code = f.read()
                    self.state.game_ui_segments['css'] = css_code
                    print(f"Extracted CSS extensions from separate file")
                
                audio_file_path = "GameGenerationOutput/audio_extensions.html"
                if os.path.exists(audio_file_path) and ('audio' not in self.state.game_ui_segments or not self.state.game_ui_segments['audio']):
                    with open(audio_file_path, "r") as f:
                        audio_code = f.read()
                    self.state.game_ui_segments['audio'] = audio_code
                    print(f"Extracted audio extensions from separate file")
            else:
                # If crew returned structured segments but no legacy file, compile them
                if self.state.game_ui_segments:
                    combined_code = "// UI Extensions for Template Integration\n\n"
                    for segment_name, segment_code in self.state.game_ui_segments.items():
                        combined_code += f"// {segment_name.upper()} EXTENSIONS\n{segment_code}\n\n"
                    
                    self.state.game_ui_file = combined_code
                    with open(ui_file_path, "w") as f:
                        f.write(combined_code)
                    print(f"Created legacy game_ui.js from segments ({len(combined_code)} bytes)")
                else:
                    # Still fall back to any final integration task
                    if hasattr(ui_output, 'final_integration_task'):
                        self.state.game_ui_file = ui_output.final_integration_task
                        with open(ui_file_path, "w") as f:
                            f.write(ui_output.final_integration_task)
                        print(f"Extracted game_ui.js from output ({len(ui_output.final_integration_task)} bytes)")
                    else:
                        print("Warning: No UI code segments or files were generated")
                    
            # Create hardcoded fallback files with default content if no segments were found
            if not self.state.game_ui_segments or not self.state.game_ui_segments.get('game_ui'):
                fallback_game_ui = """
                // Default UI extensions
                updateHUD() {
                    console.log("Updating HUD with fallback implementation");
                    const hud = document.getElementById('hud');
                    if (hud) {
                        hud.innerHTML = `
                            <div class="hud-container">
                                <div class="hud-item">Level: ${this.currentLevel || 1}</div>
                                <div class="hud-item">Score: ${this.score || 0}</div>
                                <div class="hud-item">Health: ${this.health || 100}</div>
                            </div>
                        `;
                    }
                }
                
                showMessage(message, duration = 3000) {
                    const messageElement = document.createElement('div');
                    messageElement.className = 'game-message';
                    messageElement.textContent = message;
                    document.getElementById('game-container').appendChild(messageElement);
                    
                    setTimeout(() => {
                        messageElement.classList.add('fade-out');
                        setTimeout(() => {
                            messageElement.remove();
                        }, 500);
                    }, duration);
                }
                
                updateUI() {
                    this.updateHUD();
                }
                """
                self.state.game_ui_segments['game_ui'] = fallback_game_ui
                print("Added fallback GameUI extensions")
                
            if not self.state.game_ui_segments or not self.state.game_ui_segments.get('css'):
                fallback_css = """
                /* Default CSS extensions */
                .hud-container {
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 10px;
                    font-family: 'Orbitron', sans-serif;
                }
                
                .hud-item {
                    background-color: rgba(0, 0, 0, 0.5);
                    color: #fff;
                    padding: 5px 10px;
                    border-radius: 5px;
                    margin: 0 5px;
                }
                
                .game-message {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background-color: rgba(0, 0, 0, 0.7);
                    color: #fff;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 18px;
                    z-index: 100;
                    transition: opacity 0.5s;
                }
                
                .fade-out {
                    opacity: 0;
                }
                
                /* Game object styles */
                .player {
                    background-color: #45a247;
                    border: 2px solid #fff;
                }
                
                .enemy {
                    background-color: #e94560;
                    border: 2px solid #fff;
                }
                
                .collectible {
                    background-color: #ffcc00;
                    border: 2px solid #fff;
                    border-radius: 50%;
                }
                
                .platform {
                    background-color: #283c86;
                    border: 1px solid #fff;
                }
                """
                self.state.game_ui_segments['css'] = fallback_css
                print("Added fallback CSS extensions")
                
            if not self.state.game_ui_segments or not self.state.game_ui_segments.get('audio'):
                fallback_audio = """
                <audio id="jump-sound">
                    <source src="jump-sound.mp3" type="audio/mpeg">
                </audio>
                <audio id="collect-sound">
                    <source src="collect-sound.mp3" type="audio/mpeg">
                </audio>
                <audio id="hit-sound">
                    <source src="hit-sound.mp3" type="audio/mpeg">
                </audio>
                <audio id="level-complete-sound">
                    <source src="level-complete-sound.mp3" type="audio/mpeg">
                </audio>
                """
                self.state.game_ui_segments['audio'] = fallback_audio
                print("Added fallback audio extensions")
        except Exception as e:
            print(f"Error processing ui output: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Add fallback content even in case of exception
            self.state.game_ui_segments = self.state.game_ui_segments or {}
            if 'game_ui' not in self.state.game_ui_segments:
                self.state.game_ui_segments['game_ui'] = "// FALLBACK: Error occurred during UI code processing\nconsole.log('Using fallback UI code');"
            if 'css' not in self.state.game_ui_segments:
                self.state.game_ui_segments['css'] = "/* FALLBACK: Error occurred during CSS processing */\n.fallback { color: red; }"
            if 'audio' not in self.state.game_ui_segments:
                self.state.game_ui_segments['audio'] = "<!-- FALLBACK: Error occurred during audio processing -->\n<audio id=\"error-sound\"></audio>"
        
        # Mark the ui development phase as complete
        self.state.ui_development_complete = True
        
        print("UI System Development Phase completed successfully with template integration")
        
        return "UI System Development Phase completed successfully with template integration"

    def _validate_code_segment(self, segment_type, content, required_patterns=None):
        """
        Validates a code segment before integration into the template.
        
        Args:
            segment_type: The type of code segment (game_ui, game_logic, game_class, css, audio)
            content: The code segment to validate
            required_patterns: Optional list of patterns that must be present in valid code
            
        Returns:
            tuple: (is_valid, sanitized_content, error_message)
        """
        if not content or not isinstance(content, str):
            return False, "", f"Invalid {segment_type} segment: content is empty or not a string"
        
        # Trim whitespace
        sanitized_content = content.strip()
        if not sanitized_content:
            return False, "", f"Invalid {segment_type} segment: content is empty after trimming whitespace"
        
        # Check for minimum length based on segment type
        min_lengths = {
            "game_ui": 10,
            "game_logic": 10,
            "game_class": 10,
            "css": 5,
            "audio": 5
        }
        
        min_length = min_lengths.get(segment_type, 10)
        if len(sanitized_content) < min_length:
            return False, "", f"Invalid {segment_type} segment: content too short (min {min_length} chars)"
        
        # JavaScript segment validation
        if segment_type in ["game_ui", "game_logic", "game_class"]:
            # Check for basic syntax issues
            js_syntax_errors = self._check_js_syntax(sanitized_content)
            if js_syntax_errors:
                return False, "", f"Invalid {segment_type} JS segment: {js_syntax_errors}"
            
            # Check if the segment contains function definitions
            if "function" not in sanitized_content and "=>" not in sanitized_content and "class" not in sanitized_content:
                return False, "", f"Invalid {segment_type} segment: Missing expected function or class definitions"
            
            # Check for balanced braces/parentheses
            if not self._has_balanced_delimiters(sanitized_content):
                return False, "", f"Invalid {segment_type} segment: Unbalanced braces, brackets, or parentheses"
        
        # CSS segment validation
        elif segment_type == "css":
            # Check for CSS syntax (basic validation)
            if "{" not in sanitized_content or "}" not in sanitized_content:
                return False, "", "Invalid CSS segment: Missing curly braces for style rules"
            
            # Check for balanced braces
            if not self._has_balanced_delimiters(sanitized_content):
                return False, "", "Invalid CSS segment: Unbalanced braces"
        
        # Audio segment validation
        elif segment_type == "audio":
            # Simple validation for audio (HTML tags)
            if "<audio" not in sanitized_content.lower() and "<source" not in sanitized_content.lower():
                return False, "", "Invalid audio segment: Missing audio or source tags"
        
        # Check for required patterns if specified
        if required_patterns:
            for pattern in required_patterns:
                if pattern not in sanitized_content:
                    return False, "", f"Invalid {segment_type} segment: Missing required pattern '{pattern}'"
        
        return True, sanitized_content, ""

    def _check_js_syntax(self, js_content):
        """
        Performs basic JavaScript syntax validation.
        
        Args:
            js_content: JavaScript code content to validate
            
        Returns:
            str: Error message if validation fails, empty string if valid
        """
        # Check for unclosed strings
        in_single_quote = False
        in_double_quote = False
        in_template_literal = False
        escaped = False
        
        for i, char in enumerate(js_content):
            if escaped:
                escaped = False
                continue
            
            if char == '\\':
                escaped = True
                continue
            
            if char == "'" and not in_double_quote and not in_template_literal:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote and not in_template_literal:
                in_double_quote = not in_double_quote
            elif char == '`' and not in_single_quote and not in_double_quote:
                in_template_literal = not in_template_literal
        
        if in_single_quote:
            return "Unclosed single quote string"
        if in_double_quote:
            return "Unclosed double quote string"
        if in_template_literal:
            return "Unclosed template literal"
        
        # Check for common syntax errors
        if js_content.count('//') > js_content.count('\n'):
            return "Too many single-line comments, possible syntax error"
        
        return ""

    def _has_balanced_delimiters(self, content):
        """
        Check if code has balanced delimiters (parentheses, braces, brackets).
        
        Args:
            content: Code content to check
            
        Returns:
            bool: True if delimiters are balanced
        """
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        
        # Skip strings and comments for accurate validation
        i = 0
        in_string = False
        string_char = None
        in_comment = False
        in_multiline_comment = False
        
        while i < len(content):
            char = content[i]
            
            # Handle string literals
            if not in_comment and not in_multiline_comment and char in ["'", '"', '`'] and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
            
            # Handle comments
            elif not in_string:
                if not in_comment and not in_multiline_comment and char == '/' and i+1 < len(content):
                    if content[i+1] == '/':
                        in_comment = True
                        i += 1
                    elif content[i+1] == '*':
                        in_multiline_comment = True
                        i += 1
                elif in_comment and char == '\n':
                    in_comment = False
                elif in_multiline_comment and char == '*' and i+1 < len(content) and content[i+1] == '/':
                    in_multiline_comment = False
                    i += 1
                
                # Process delimiters only if not in comment or string
                elif not in_comment and not in_multiline_comment:
                    if char in '({[':
                        stack.append(char)
                    elif char in ')}]':
                        if not stack or stack.pop() != pairs[char]:
                            return False
            
            i += 1
        
        # If stack is empty, delimiters are balanced
        return len(stack) == 0

    @listen(and_(engine_crew_generation, entity_crew_generation, level_crew_generation, ui_crew_generation))
    def template_integration(self):
        """
        Template Integration Phase of the Game Development Flow
        
        This phase is responsible for:
        - Integrating all code segments into the final game
        - Validating and sanitizing code segments before integration
        - Handling errors gracefully with meaningful feedback
        - Generating the final game executable
        """
        print("Starting Template Integration Phase - All Code Generation Crews Have Completed")
        
        # Check if all crew phases are complete
        required_phases = [
            self.state.engine_development_complete,
            self.state.entity_development_complete, 
            self.state.level_development_complete,
            self.state.ui_development_complete
        ]
        
        if not all(required_phases):
            print("Warning: Not all code generation phases are complete. Integration proceeding anyway.")
        
        # Ensure all code segments are defined with fallbacks
        if not self.state.game_engine_segments:
            print("Warning: Engine code segments are missing. Using hardcoded fallbacks.")
            self.state.game_engine_segments = {
                'game_logic': "// HARDCODED FALLBACK: Engine Logic\nconsole.log('Using hardcoded fallback engine logic');",
                'game_class': "// HARDCODED FALLBACK: Engine Class\nconsole.log('Using hardcoded fallback engine class');"
            }
        
        if not self.state.game_entities_segments:
            print("Warning: Entity code segments are missing. Using hardcoded fallbacks.")
            self.state.game_entities_segments = {
                'game_logic': "// HARDCODED FALLBACK: Entity Logic\nconsole.log('Using hardcoded fallback entity logic');"
            }
        
        if not self.state.game_levels_segments:
            print("Warning: Level code segments are missing. Using hardcoded fallbacks.")
            self.state.game_levels_segments = {
                'game_logic': "// HARDCODED FALLBACK: Level Logic\nconsole.log('Using hardcoded fallback level logic');",
                'game_class': "// HARDCODED FALLBACK: Level Class\nconsole.log('Using hardcoded fallback level class');"
            }
        
        if not self.state.game_ui_segments:
            print("Warning: UI code segments are missing. Using hardcoded fallbacks.")
            self.state.game_ui_segments = {
                'game_ui': "// HARDCODED FALLBACK: UI\nconsole.log('Using hardcoded fallback UI');",
                'css': "/* HARDCODED FALLBACK: CSS */\n.fallback { color: red; }",
                'audio': "<!-- HARDCODED FALLBACK: Audio -->\n<audio id=\"fallback-sound\"></audio>"
            }
        
        # Integrate all code segments into the final game executable
        try:
            # Read the template HTML file
            try:
                with open(self.state.game_template_path, "r") as f:
                    template_content = f.read()
                print(f"Successfully loaded template from {self.state.game_template_path}")
            except Exception as e:
                print(f"Error loading template: {str(e)}")
                
                # Try to find the template in alternative locations
                alternative_paths = [
                    "game_template.html",
                    os.path.join("src", "game_template.html"),
                    os.path.join("GameGenerationOutput", "template.html"),
                    "backup/game_template.html"
                ]
                
                template_content = None
                backup_template_path = None
                
                for path in alternative_paths:
                    try:
                        if os.path.exists(path):
                            with open(path, "r") as f:
                                template_content = f.read()
                            backup_template_path = path
                            print(f"Successfully loaded template from alternate location: {path}")
                            break
                    except Exception as e2:
                        print(f"Error loading from {path}: {str(e2)}")
                
                if template_content is None:
                    # Create a minimal template as last resort
                    template_content = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8" />
                        <title>Emergency Fallback Template</title>
                        <style>
                            /*Your style goes here */
                        </style>
                    </head>
                    <body>
                        <div id="game-container"></div>
                        <!--Extra audio tags for sound effects-->
                        <script>
                            document.addEventListener('DOMContentLoaded', () => {
                                class GameUI {
                                    // Your UI functions here;
                                }
                                class GameLogic {
                                    // Your game logic here;
                                }
                                class Game {
                                    // Prepare game container DOM elements here;
                                }
                                const game = new Game();
                            });
                        </script>
                    </body>
                    </html>
                    """
                    print("Created emergency fallback template")
            
            # Create integration points dictionary with hardcoded fallbacks
            integration_points = {
                "css": self.state.template_css_insertion_point or "/*Your style goes here */",
                "audio": self.state.template_audio_insertion_point or "<!--Extra audio tags for sound effects-->",
                "game_ui": self.state.template_game_ui_insertion_point or "// Your UI functions here;",
                "game_logic": self.state.template_game_logic_insertion_point or "// Your game logic here;",
                "game_class": self.state.template_game_class_insertion_point or "// Prepare game container DOM elements here;"
            }
            
            # Verify that the template has the necessary insertion points
            css_marker_exists = integration_points["css"] in template_content
            audio_marker_exists = integration_points["audio"] in template_content
            gameui_marker_exists = integration_points["game_ui"] in template_content
            gamelogic_marker_exists = integration_points["game_logic"] in template_content
            game_marker_exists = integration_points["game_class"] in template_content
            
            # Log verification results
            if not css_marker_exists:
                print(f"Warning: CSS insertion marker '{integration_points['css']}' not found in template. Integration may fail.")
            if not audio_marker_exists:
                print(f"Warning: Audio insertion marker '{integration_points['audio']}' not found in template. Integration may fail.")
            if not gameui_marker_exists:
                print(f"Warning: GameUI class marker '{integration_points['game_ui']}' not found in template. Integration may fail.")
            if not gamelogic_marker_exists:
                print(f"Warning: GameLogic class marker '{integration_points['game_logic']}' not found in template. Integration may fail.")
            if not game_marker_exists:
                print(f"Warning: Game class marker '{integration_points['game_class']}' not found in template. Integration may fail.")
            
            # Prepare integration content
            integration_content = {
                "css": "",
                "audio": "",
                "game_ui": "",
                "game_logic": "",
                "game_class": ""
            }
            
            # Add engine extensions
            if self.state.game_engine_segments:
                if 'game_logic' in self.state.game_engine_segments:
                    integration_content["game_logic"] += self.state.game_engine_segments['game_logic'] + "\n\n"
                if 'game_class' in self.state.game_engine_segments:
                    integration_content["game_class"] += self.state.game_engine_segments['game_class'] + "\n\n"
            
            # Add entity extensions
            if self.state.game_entities_segments:
                if 'game_logic' in self.state.game_entities_segments:
                    integration_content["game_logic"] += self.state.game_entities_segments['game_logic'] + "\n\n"
            
            # Add level extensions
            if self.state.game_levels_segments:
                if 'game_logic' in self.state.game_levels_segments:
                    integration_content["game_logic"] += self.state.game_levels_segments['game_logic'] + "\n\n"
                if 'game_class' in self.state.game_levels_segments:
                    integration_content["game_class"] += self.state.game_levels_segments['game_class'] + "\n\n"
            
            # Add UI extensions
            if self.state.game_ui_segments:
                if 'game_ui' in self.state.game_ui_segments:
                    integration_content["game_ui"] += self.state.game_ui_segments['game_ui'] + "\n\n"
                if 'css' in self.state.game_ui_segments:
                    integration_content["css"] += self.state.game_ui_segments['css'] + "\n\n"
                if 'audio' in self.state.game_ui_segments:
                    integration_content["audio"] += self.state.game_ui_segments['audio'] + "\n\n"
            
            # Add insertion tracking comment to detect if code was inserted
            for point_type in integration_content:
                if integration_content[point_type]:
                    integration_content[point_type] += f"\n// {point_type.upper()}_INSERTION_MARKER - DO NOT REMOVE\n"
            
            # Clone the template for integration
            updated_template = template_content
            
            # Perform the actual integration
            for point_type, marker in integration_points.items():
                content = integration_content[point_type]
                
                if content:
                    # Handle different types of code segments
                    if point_type in ["game_ui", "game_logic", "game_class"]:
                        # Find the class declaration and add our content after it but before the constructor
                        insert_after = marker
                        if insert_after in updated_template:
                            updated_template = updated_template.replace(
                                insert_after, 
                                insert_after + "\n    // " + point_type.upper() + " EXTENSIONS\n    " + 
                                content.replace("\n", "\n    ")
                            )
                            print(f"Inserted {point_type} code segment after marker: {marker[:30]}...")
                        else:
                            print(f"Warning: Could not find {point_type} marker in template")
                            # Add a comment to indicate the code wasn't inserted
                            updated_template += f"\n\n<!-- WARNING: {point_type.upper()} CODE WAS NOT INSERTED - MARKER NOT FOUND -->\n"
                    elif point_type == "css":
                        # For CSS, use proper CSS comment syntax
                        if marker in updated_template:
                            updated_template = updated_template.replace(
                                marker,
                                marker + "\n\n/* GENERATED CSS EXTENSIONS */\n" + content
                            )
                            print(f"Inserted CSS content at marker: {marker[:30]}...")
                        else:
                            print(f"Warning: CSS marker not found in template")
                            # Add a comment to indicate the code wasn't inserted
                            updated_template += f"\n\n<!-- WARNING: CSS CODE WAS NOT INSERTED - MARKER NOT FOUND -->\n"
                    elif point_type == "audio":
                        # For audio, use HTML comment format
                        if marker in updated_template:
                            updated_template = updated_template.replace(
                                marker,
                                marker + "\n\n<!-- GENERATED AUDIO EXTENSIONS -->\n" + content
                            )
                            print(f"Inserted audio content at marker: {marker[:30]}...")
                        else:
                            print(f"Warning: Audio marker not found in template")
                            # Add a comment to indicate the code wasn't inserted
                            updated_template += f"\n\n<!-- WARNING: AUDIO CODE WAS NOT INSERTED - MARKER NOT FOUND -->\n"
                    else:
                        # For any other integration points
                        if marker in updated_template:
                            updated_template = updated_template.replace(
                                marker, 
                                marker + "\n" + content
                            )
                            print(f"Inserted {point_type} content at marker: {marker[:30]}...")
                        else:
                            print(f"Warning: {point_type} marker not found in template")
                            # Add a comment to indicate the code wasn't inserted
                            updated_template += f"\n\n<!-- WARNING: {point_type.upper()} CODE WAS NOT INSERTED - MARKER NOT FOUND -->\n"
                else:
                    print(f"Warning: No content available for {point_type} segment")
                    # Add a comment to indicate the code wasn't inserted
                    if marker in updated_template:
                        updated_template = updated_template.replace(
                            marker,
                            marker + f"\n\n// WARNING: FILE WAS TOUCHED BUT THE {point_type.upper()} CODE WASN'T INSERTED\n"
                        )
            
            # Verify if code was actually inserted by checking for insertion markers
            insertion_success = {
                "css": "_INSERTION_MARKER" in updated_template,
                "audio": "_INSERTION_MARKER" in updated_template,
                "game_ui": "_INSERTION_MARKER" in updated_template,
                "game_logic": "_INSERTION_MARKER" in updated_template,
                "game_class": "_INSERTION_MARKER" in updated_template
            }
            
            # Log insertion results
            for point_type, success in insertion_success.items():
                if success:
                    print(f"✅ {point_type} code was successfully inserted")
                else:
                    print(f"❌ {point_type} code was NOT inserted")
                    # Add a final warning comment at the end of the file
                    updated_template += f"\n\n<!-- FINAL WARNING: {point_type.upper()} CODE WAS NOT PROPERLY INSERTED -->\n"
            
            # Save the integrated template as the final game
            final_game_path = self._get_output_path("final_game.html")
            with open(final_game_path, "w") as f:
                f.write(updated_template)
            
            print(f"Successfully integrated all code into final game HTML file at {final_game_path}")
            
            # Also save a backup copy
            backup_path = self._get_output_path("final_game_backup.html")
            with open(backup_path, "w") as f:
                f.write(updated_template)
            
            # Also generate a legacy JavaScript file for reference
            with open(self._get_output_path("final_game_executable.js"), "w") as f:
                f.write("// COMBINED GAME CODE FOR REFERENCE\n\n")
                f.write("// ENGINE EXTENSIONS\n")
                f.write(self.state.game_engine_file or "// No engine code available\n\n")
                f.write("// ENTITY EXTENSIONS\n")
                f.write(self.state.game_entities_file or "// No entity code available\n\n")
                f.write("// LEVEL EXTENSIONS\n")
                f.write(self.state.game_levels_file or "// No level code available\n\n")
                f.write("// UI EXTENSIONS\n")
                f.write(self.state.game_ui_file or "// No UI code available\n\n")
            
            print(f"Also generated legacy combined JavaScript file for reference")
            
        except Exception as e:
            print(f"Error integrating code segments: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Create an emergency fallback game file
            emergency_game = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8" />
                <title>Emergency Fallback Game</title>
                <style>
                    body { font-family: Arial, sans-serif; background-color: #f0f0f0; text-align: center; padding: 50px; }
                    .error { color: red; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>Emergency Fallback Game</h1>
                <p class="error">The template integration process encountered an error:</p>
                <pre>""" + str(e) + """</pre>
                <p>Please check the logs for more information.</p>
                <script>
                    console.error("Template integration failed:", """ + json.dumps(str(e)) + """);
                </script>
            </body>
            </html>
            """
            
            emergency_path = self._get_output_path("emergency_fallback_game.html")
            with open(emergency_path, "w") as f:
                f.write(emergency_game)
            print(f"Created emergency fallback game at {emergency_path}")
        
        # Mark the template integration phase as complete
        self.state.template_integration_complete = True
        
        print("Template Integration Phase completed")
        
        return "Template Integration Phase completed"

    @listen(template_integration)
    def validation_phase(self):
        """
        Validation Phase of the Game Development Flow
        
        This phase is responsible for:
        - Validating the integrated code using specialized validation agents
        - Identifying syntax, integration, functional, and style issues
        - Categorizing issues by severity and responsible crew
        - Generating structured feedback for refinement
        """
        print("Starting Validation Phase - Analyzing Integrated Code")
        
        # Check if template integration was completed
        if not self.state.template_integration_complete:
            print("Warning: Template integration was not completed. Validation may be incomplete.")
        
        # Get the path to the integrated game file
        final_game_path = self._get_output_path("final_game.html")
        if not os.path.exists(final_game_path):
            print(f"Error: Integrated game file not found at {final_game_path}")
            return "Validation Phase failed: Integrated game file not found"
        
        # Read the integrated game file
        try:
            with open(final_game_path, "r") as f:
                integrated_code = f.read()
            print(f"Successfully loaded integrated game file ({len(integrated_code)} bytes)")
        except Exception as e:
            print(f"Error reading integrated game file: {str(e)}")
            return "Validation Phase failed: Could not read integrated game file"
        
        # Extract code segments for validation
        try:
            # Extract CSS
            css_match = re.search(r'<style>(.*?)</style>', integrated_code, re.DOTALL)
            css_code = css_match.group(1) if css_match else ""
            
            # Extract JavaScript
            js_match = re.search(r'<script>(.*?)</script>', integrated_code, re.DOTALL)
            js_code = js_match.group(1) if js_match else ""
            
            # Extract HTML body
            body_match = re.search(r'<body>(.*?)</body>', integrated_code, re.DOTALL)
            body_code = body_match.group(1) if body_match else ""
            
            # Extract specific segments
            game_ui_match = re.search(r'class GameUI\s*{(.*?)}', js_code, re.DOTALL)
            game_ui_code = game_ui_match.group(1) if game_ui_match else ""
            
            game_logic_match = re.search(r'class GameLogic\s*{(.*?)}', js_code, re.DOTALL)
            game_logic_code = game_logic_match.group(1) if game_logic_match else ""
            
            game_class_match = re.search(r'class Game\s*{(.*?)}', js_code, re.DOTALL)
            game_class_code = game_class_match.group(1) if game_class_match else ""
            
            print(f"Successfully extracted code segments for validation")
        except Exception as e:
            print(f"Error extracting code segments: {str(e)}")
            # Continue with validation even if extraction fails
        
        # Prepare validation inputs
        validation_inputs = {
            "integrated_code": integrated_code,
            "css_code": css_code,
            "js_code": js_code,
            "body_code": body_code,
            "game_ui_code": game_ui_code,
            "game_logic_code": game_logic_code,
            "game_class_code": game_class_code,
            "final_game_path": final_game_path,
            "engine_segments": self.state.game_engine_segments,
            "entity_segments": self.state.game_entities_segments,
            "level_segments": self.state.game_levels_segments,
            "ui_segments": self.state.game_ui_segments
        }
        
        # Run the ValidationCrew with the integrated code
        try:
            from unemployedstudios.crews.validation_crew import ValidationCrew
            
            validation_output = (
                ValidationCrew()
                .crew()
                .kickoff(inputs=validation_inputs)
            )
            
            # Process validation results
            if hasattr(validation_output, 'raw'):
                with open(self._get_output_path("validation_report.json"), "w") as f:
                    f.write(validation_output.raw)
                print(f"Saved validation report to validation_report.json")
                
                # Parse validation results
                try:
                    validation_results = json.loads(validation_output.raw)
                    
                    # Log validation summary
                    error_count = validation_results.get("error_count", 0)
                    warning_count = validation_results.get("warning_count", 0)
                    
                    print(f"Validation completed with {error_count} errors and {warning_count} warnings")
                    
                    # Store validation results in state for refinement phase
                    self.state.validation_results = validation_results
                    
                    # Check if refinement is needed
                    if error_count > 0:
                        print(f"Refinement needed: {error_count} errors found")
                        # Trigger refinement phase (to be implemented)
                    elif warning_count > 0:
                        print(f"Refinement suggested: {warning_count} warnings found")
                        # Trigger refinement phase with lower priority
                    else:
                        print("No issues found. Code integration successful!")
                        
                except json.JSONDecodeError:
                    print("Warning: Could not parse validation results as JSON")
                    # Store raw output for manual inspection
                    self.state.validation_results = {"raw": validation_output.raw}
            else:
                print("Warning: Validation crew did not return structured results")
                self.state.validation_results = {"error": "No structured validation results available"}
                
        except Exception as e:
            print(f"Error running validation crew: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Create a basic validation report for manual inspection
            basic_report = {
                "error": str(e),
                "error_count": 1,
                "warning_count": 0,
                "issues": [
                    {
                        "type": "system",
                        "severity": "error",
                        "message": f"Validation crew failed: {str(e)}",
                        "responsible_crew": None
                    }
                ]
            }
            
            with open(self._get_output_path("validation_error_report.json"), "w") as f:
                json.dump(basic_report, f, indent=2)
            
            self.state.validation_results = basic_report
        
        print("Validation Phase completed")
        
        return "Validation Phase completed with structured feedback for refinement"

    @listen(template_integration)
    def initiate_asset_generation(self):
        """
        Asset Generation Phase of the Game Development Flow
        
        This phase is responsible for:
        - Asset specification based on the style guide and game concept
        - Specifying visual assets (sprites, backgrounds, UI elements)
        - Specifying audio assets (music, sound effects)
        - Compiling all specifications into a structured collection
        
        The specifications will then be processed to download/generate the actual assets.
        """
        print("Starting Asset Generation Phase")
        
        # Create output directories if they don't exist
        os.makedirs("GameGenerationOutput", exist_ok=True)
        os.makedirs("GameGenerationOutput/assets/images", exist_ok=True)
        os.makedirs("GameGenerationOutput/assets/audio", exist_ok=True)
        
        try:
            # Import the tools
            from unemployedstudios.tools.custom_tool import GenerateAndDownloadImageTool, SearchAndSaveSoundTool
            
            # Check for required environment variables
            print(f"OPENAI_API_KEY available: {bool(os.getenv('OPENAI_API_KEY'))}")
            
            # Check for both Freesound credentials - both may be needed for successful API access
            freesound_api_key = os.getenv('FREESOUND_API_KEY')
            freesound_client_id = os.getenv('FREESOUND_CLIENT_ID')
            
            print(f"FREESOUND_API_KEY available: {bool(freesound_api_key)}")
            print(f"FREESOUND_CLIENT_ID available: {bool(freesound_client_id)}")
            
            # Note about Freesound credentials
            if not freesound_api_key or not freesound_client_id:
                print("WARNING: One or both Freesound credentials missing. Both FREESOUND_API_KEY and FREESOUND_CLIENT_ID may be required for audio asset generation.")
            
            # Initialize the tools
            image_tool = GenerateAndDownloadImageTool()
            audio_tool = SearchAndSaveSoundTool()
            
            # Prepare inputs for the asset generation crew
            asset_inputs = {
                "game_concept": self.state.game_concept,
                "style_guide": self.state.style_guide,
                "game_design_document": self.state.game_design_document
            }
            
            # Add concept data if available from concept expansion
            if self.state.concept_expansion:
                concept_data = {}
                if isinstance(self.state.concept_expansion, dict):
                    concept_data = self.state.concept_expansion
                else:
                    try:
                        # Try to parse as JSON if it's a string
                        concept_data = json.loads(str(self.state.concept_expansion))
                    except:
                        print("Warning: Could not parse concept expansion data")
                
                if concept_data:
                    if "main_character" in concept_data:
                        asset_inputs["main_character"] = concept_data["main_character"]
                    if "supporting_characters" in concept_data:
                        asset_inputs["supporting_characters"] = concept_data["supporting_characters"]
                    if "world_building" in concept_data:
                        asset_inputs["world_building"] = concept_data["world_building"]
                    if "levels" in concept_data:
                        asset_inputs["levels"] = concept_data["levels"]
                    if "visual_style" in concept_data:
                        asset_inputs["visual_style"] = concept_data["visual_style"]
                    if "audio_style" in concept_data:
                        asset_inputs["audio_style"] = concept_data["audio_style"]
                    if "title" in concept_data:
                        asset_inputs["title"] = concept_data["title"]
            
            print(f"Prepared asset inputs with keys: {list(asset_inputs.keys())}")
            
            # Run the Asset Generation Crew to get specifications
            print("Starting AssetGenerationCrew for specification generation...")
            asset_output = (
                AssetGenerationCrew()
                .crew()
                .kickoff(inputs=asset_inputs)
            )
            
            # Process and store the asset specifications
            try:
                # Create an instance to use its helper methods for extraction and validation
                asset_crew = AssetGenerationCrew()
                
                # Extract asset specifications using the improved extraction method
                asset_specs = asset_crew.extract_asset_specs_from_output(asset_output)
                
                # Validate the asset specifications
                validation_results = asset_crew.validate_asset_specifications(asset_specs)
                print(f"Asset specification validation: {validation_results['valid']}")
                
                if validation_results["errors"]:
                    print(f"Found {len(validation_results['errors'])} errors in asset specifications:")
                    for i, error in enumerate(validation_results["errors"]):
                        print(f"  Error {i+1}: {error}")
                
                if validation_results["warnings"]:
                    print(f"Found {len(validation_results['warnings'])} warnings in asset specifications:")
                    for i, warning in enumerate(validation_results["warnings"]):
                        print(f"  Warning {i+1}: {warning}")
                
                # Save the specifications to a file
                with open(self._get_output_path("asset_specifications.json"), "w") as f:
                    json.dump(asset_specs.dict() if hasattr(asset_specs, 'dict') else asset_specs.model_dump(), f, indent=2)
                
                # Store in state
                self.state.asset_specifications = asset_specs
                
                # Generate the actual assets
                self._generate_assets_with_retry(asset_specs, image_tool, audio_tool)
                
                # Organize generated assets
                self._organize_generated_assets()
                
            except Exception as e:
                print(f"Error processing asset specifications: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Create and use fallback specifications
                print("Creating fallback asset specifications")
                fallback_specs = self._create_fallback_asset_specs()
                self.state.asset_specifications = fallback_specs
                self._generate_assets_with_retry(fallback_specs, image_tool, audio_tool)
            
        except Exception as e:
            print(f"Error in asset generation phase: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Mark asset generation as complete
        self.state.asset_generation_complete = True
        
        print("Asset Generation Phase completed")
        
        return "Asset Generation Phase completed"

    def _generate_assets_with_retry(self, asset_specs, image_tool, audio_tool):
        """
        Generate assets with robust error handling and retry logic.
        This method is more reliable than the previous implementation.
        """
        # Track successful generations
        generated_images = {}
        generated_audio = {}
        
        # Process image assets
        if asset_specs and hasattr(asset_specs, 'image_assets') and asset_specs.image_assets:
            print(f"Generating {len(asset_specs.image_assets)} image assets...")
            
            # Limit to a reasonable number of images to avoid rate limiting
            max_images_to_generate = min(5, len(asset_specs.image_assets))
            
            for i, img_spec in enumerate(asset_specs.image_assets[:max_images_to_generate]):
                try:
                    print(f"Generating image {i+1}/{max_images_to_generate}: {img_spec.asset_id}")
                    
                    # Add delay between requests to avoid rate limiting
                    if i > 0:
                        import time
                        print("Waiting to avoid rate limiting...")
                        time.sleep(2)  # 2 second delay between requests
                    
                    # Ensure the directory exists for the image
                    full_path = f"GameGenerationOutput/{img_spec.filename}"
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Ensure size is one of the allowed values
                    size = getattr(img_spec, 'size', "1024x1024")
                    allowed_sizes = ["1024x1024", "1792x1024", "1024x1792"]
                    if size not in allowed_sizes:
                        print(f"Warning: Invalid size '{size}' for {img_spec.asset_id}, defaulting to 1024x1024")
                        size = "1024x1024"
                    
                    # Ensure model is one of the allowed values
                    model = getattr(img_spec, 'model', "dall-e-3")
                    allowed_models = ["gpt-image-1", "dall-e-2", "dall-e-3"]
                    if model not in allowed_models:
                        print(f"Warning: Invalid model '{model}' for {img_spec.asset_id}, defaulting to dall-e-3")
                        model = "dall-e-3"
                    
                    # Add retry logic
                    retry_count = 0
                    max_retries = 3
                    success = False
                    
                    while retry_count < max_retries and not success:
                        try:
                            result = image_tool._run(
                                prompt=img_spec.prompt,
                                file_name=full_path,
                                size=size,
                                model=model
                            )
                            
                            # Check if file was actually created
                            if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                                # Store the result
                                generated_images[img_spec.asset_id] = {
                                    "filename": img_spec.filename,
                                    "full_path": full_path,
                                    "size": size,
                                    "model": model,
                                    "prompt": img_spec.prompt,
                                    "result": result
                                }
                                
                                print(f"Generated image: {img_spec.asset_id}")
                                success = True
                            else:
                                raise Exception(f"Image file was not created or is empty: {full_path}")
                            
                        except Exception as retry_error:
                            retry_count += 1
                            error_str = str(retry_error).lower()
                            
                            # Check for specific error types
                            if "429" in error_str or "rate limit" in error_str:
                                # Rate limit error, wait longer and retry
                                wait_time = 5 * retry_count  # Progressive backoff
                                print(f"Rate limit encountered. Waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                                import time
                                time.sleep(wait_time)
                            elif "content policy" in error_str or "security" in error_str:
                                # Content policy violation - don't retry with same prompt
                                print(f"Content policy violation: {retry_error}")
                                print("Skipping this image and moving on.")
                                break
                            else:
                                print(f"Error generating image (attempt {retry_count}/{max_retries}): {str(retry_error)}")
                                if retry_count < max_retries:
                                    wait_time = 2 * retry_count
                                    print(f"Waiting {wait_time}s before retry...")
                                    import time
                                    time.sleep(wait_time)
                                else:
                                    print(f"Failed to generate image after {max_retries} attempts")
                                    break
                    
                except Exception as e:
                    print(f"Error generating image {img_spec.asset_id}: {str(e)}")
        
        # Process audio assets
        if asset_specs and hasattr(asset_specs, 'audio_assets') and asset_specs.audio_assets:
            print(f"Downloading {len(asset_specs.audio_assets)} audio assets...")
            
            # Check for Freesound credentials before trying to download audio
            freesound_api_key = os.getenv('FREESOUND_API_KEY')
            freesound_client_id = os.getenv('FREESOUND_CLIENT_ID')
            
            if not freesound_api_key:
                print("WARNING: FREESOUND_API_KEY not found in environment. Audio generation may fail.")
            
            if not freesound_client_id:
                print("WARNING: FREESOUND_CLIENT_ID not found in environment. Audio generation may fail.")
            
            # Limit to a reasonable number of audio files during testing
            max_audio_to_generate = min(5, len(asset_specs.audio_assets))
            
            for i, audio_spec in enumerate(asset_specs.audio_assets[:max_audio_to_generate]):
                try:
                    print(f"Downloading audio {i+1}/{max_audio_to_generate}: {audio_spec.asset_id}")
                    
                    # Add delay between requests
                    if i > 0:
                        import time
                        time.sleep(1)  # 1 second delay between requests
                    
                    # Ensure the directory exists
                    full_path = f"GameGenerationOutput/{audio_spec.filename}"
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Determine the search query - prioritize query field if available
                    query = audio_spec.query if hasattr(audio_spec, 'query') else audio_spec.search_terms
                    
                    # Improve query based on asset type for better search results
                    if query and not "search term enhanced" in query:
                        asset_type = audio_spec.asset_type.lower()
                        if asset_type == "effect" and "sound effect" not in query.lower():
                            query = f"{query}, sound effect"
                        elif asset_type == "music" and "8-bit" not in query.lower():
                            query = f"{query}, 8-bit"
                        elif "game sound" not in query.lower():
                            query = f"{query}, game sound"
                        # Mark as enhanced
                        query = f"{query} (search term enhanced)"
                    
                    # Prepare simplified query for fallback
                    simplified_query = query.split(',')[0].strip()
                    if len(simplified_query) > 3:
                        simplified_query += " sound"
                    
                    print(f"Using search query: '{query}'")
                    print(f"Fallback query if needed: '{simplified_query}'")
                    
                    # Add retry logic
                    retry_count = 0
                    max_retries = 3
                    success = False
                    
                    while retry_count < max_retries and not success:
                        try:
                            # Create a dictionary of optional params that might be needed
                            extra_params = {}
                            if freesound_api_key:
                                extra_params['api_key'] = freesound_api_key
                            if freesound_client_id:
                                extra_params['client_id'] = freesound_client_id
                                
                            result = audio_tool._run(
                                query=query,
                                output_path=full_path,
                                **extra_params
                            )
                            
                            # If no results found, try with simplified query
                            if isinstance(result, dict) and result.get('success') is False and "No results found" in result.get('message', ''):
                                print(f"No results found with original query. Trying simplified query: '{simplified_query}'")
                                result = audio_tool._run(
                                    query=simplified_query,
                                    output_path=full_path,
                                    **extra_params
                                )
                                
                                # If still no results, try a very basic search term
                                if isinstance(result, dict) and result.get('success') is False and "No results found" in result.get('message', ''):
                                    basic_term = ""
                                    if "jump" in query.lower():
                                        basic_term = "jump"
                                    elif "collect" in query.lower() or "item" in query.lower():
                                        basic_term = "collect"
                                    elif "enemy" in query.lower() or "defeat" in query.lower():
                                        basic_term = "hit"
                                    elif "button" in query.lower() or "click" in query.lower():
                                        basic_term = "click"
                                    elif "menu" in query.lower() or "transition" in query.lower():
                                        basic_term = "transition"
                                    elif "university" in query.lower() or "ambient" in query.lower():
                                        basic_term = "ambient"
                                    elif "office" in query.lower() or "internship" in query.lower():
                                        basic_term = "office"
                                    elif "city" in query.lower() or "job" in query.lower():
                                        basic_term = "city"
                                    else:
                                        basic_term = audio_spec.asset_type.lower()
                                        
                                    if basic_term:
                                        very_basic_query = f"{basic_term} sound"
                                        print(f"Still no results. Trying very basic query: '{very_basic_query}'")
                                        result = audio_tool._run(
                                            query=very_basic_query,
                                            output_path=full_path,
                                            **extra_params
                                        )
                            
                            # Verify file was actually created
                            if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                                # Store the result
                                generated_audio[audio_spec.asset_id] = {
                                    "filename": audio_spec.filename,
                                    "full_path": full_path,
                                    "query": query,
                                    "result": result
                                }
                                
                                print(f"Downloaded audio: {audio_spec.asset_id}")
                                print(f"File size: {os.path.getsize(full_path) / 1024:.2f} KB")
                                success = True
                            else:
                                # If we've tried all fallbacks and still failed
                                if retry_count >= max_retries - 1:
                                    print(f"Failed to download audio after multiple attempts with different queries")
                                    break
                                
                                retry_count += 1
                                wait_time = 2 * retry_count
                                print(f"Audio file not created. Waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                                import time
                                time.sleep(wait_time)
                            
                        except Exception as retry_error:
                            retry_count += 1
                            error_str = str(retry_error).lower()
                            
                            # Different retry strategy based on error
                            if "429" in error_str or "rate limit" in error_str:
                                # Rate limit error, wait longer
                                wait_time = 5 * retry_count
                                print(f"Rate limit encountered. Waiting {wait_time}s before retry...")
                                import time
                                time.sleep(wait_time)
                            else:
                                wait_time = 3 * retry_count
                                print(f"Error downloading audio (attempt {retry_count}/{max_retries}): {str(retry_error)}")
                                print(f"Waiting {wait_time}s before retry...")
                                import time
                                time.sleep(wait_time)
                                
                                if retry_count >= max_retries:
                                    print(f"Failed to download audio after {max_retries} attempts")
                                    break
                    
                except Exception as e:
                    print(f"Error downloading audio {audio_spec.asset_id}: {str(e)}")
        
        # Save the generation results
        with open(self._get_output_path("generated_assets.json"), "w") as f:
            json.dump({
                "images": generated_images,
                "audio": generated_audio
            }, f, indent=2)
        
        # Update the state
        self.state.generated_image_assets = generated_images
        self.state.generated_audio_assets = generated_audio
        
        # Create asset manifests for easier access
        if generated_images:
            with open(self._get_output_path("assets/manifest_images.json"), "w") as f:
                json.dump(generated_images, f, indent=2)
        
        if generated_audio:
            with open(self._get_output_path("assets/manifest_audio.json"), "w") as f:
                json.dump(generated_audio, f, indent=2)
        
        print(f"Asset generation complete: {len(generated_images)} images and {len(generated_audio)} audio files")

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
                description="The main player character for Code Quest",
                size="1024x1024",
                model="dall-e-3"
            ),
            ImageAssetSpec(
                asset_id="syntax_error_enemy",
                asset_type="character",
                filename="assets/images/syntax_error_enemy.png",
                prompt="A glitchy, error-like monster character in pixel art style with red highlights",
                style="minimalist pixel art",
                importance=1,
                description="A standard enemy character representing syntax errors",
                size="1024x1024",
                model="dall-e-3"
            ),
            ImageAssetSpec(
                asset_id="university_background",
                asset_type="environment",
                filename="assets/images/university_background.png",
                prompt="A pixel art university campus background with computer labs and classrooms",
                style="minimalist pixel art",
                importance=1,
                description="The background for the University level",
                size="1792x1024",
                model="dall-e-3"
            ),
            ImageAssetSpec(
                asset_id="code_collectible",
                asset_type="item",
                filename="assets/images/code_collectible.png",
                prompt="A glowing pixel art code snippet or programming symbol that can be collected",
                style="minimalist pixel art",
                importance=2,
                description="Collectible item representing code knowledge",
                size="1024x1024",
                model="dall-e-3"
            ),
            ImageAssetSpec(
                asset_id="health_bar",
                asset_type="ui",
                filename="assets/images/ui/health_bar.png",
                prompt="A simple pixel art health/energy bar with a code or programming theme",
                style="minimalist pixel art",
                importance=1,
                description="UI element showing player health/energy",
                size="1024x1024",
                model="dall-e-3"
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
                search_terms="game collect item sound effect positive 8-bit",
                description="Sound effect when the player collects a code snippet",
                importance=1
            ),
            AudioAssetSpec(
                asset_id="university_music",
                asset_type="music",
                filename="assets/audio/university_music.mp3",
                search_terms="8-bit university campus background music loop",
                description="Background music for the University level",
                importance=1
            )
        ]
        
        return AssetSpecCollection(image_assets=image_assets, audio_assets=audio_assets)

    def _organize_generated_assets(self):
        """
        Copy generated assets to a well-organized structure in the GameGenerationOutput directory.
        """
        import shutil
        
        # Define directories
        assets_root = os.path.join("GameGenerationOutput", "assets")
        images_dir = os.path.join(assets_root, "images")
        audio_dir = os.path.join(assets_root, "audio")
        
        # Ensure directories exist
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        
        # Copy image files if they exist
        if self.state.generated_image_assets:
            for asset_id, asset_info in self.state.generated_image_assets.items():
                if "full_path" in asset_info and os.path.exists(asset_info["full_path"]):
                    # Get the base filename
                    base_filename = os.path.basename(asset_info["full_path"])
                    # Copy to the images directory
                    target_path = os.path.join(images_dir, base_filename)
                    try:
                        shutil.copy2(asset_info["full_path"], target_path)
                        print(f"Copied image {asset_id} to {target_path}")
                    except Exception as e:
                        print(f"Error copying image {asset_id}: {str(e)}")
        
        # Copy audio files if they exist
        if self.state.generated_audio_assets:
            for asset_id, asset_info in self.state.generated_audio_assets.items():
                if "full_path" in asset_info and os.path.exists(asset_info["full_path"]):
                    # Get the base filename
                    base_filename = os.path.basename(asset_info["full_path"])
                    # Copy to the audio directory
                    target_path = os.path.join(audio_dir, base_filename)
                    try:
                        shutil.copy2(asset_info["full_path"], target_path)
                        print(f"Copied audio {asset_id} to {target_path}")
                    except Exception as e:
                        print(f"Error copying audio {asset_id}: {str(e)}")
        
        print(f"Organized assets in {assets_root}")

def kickoff():
    """Start the Game Development Flow"""
    flow = GameDevelopmentFlow()
    result = flow.kickoff()
    return result

def plot():
    """Generate a visualization of the flow"""
    flow = GameDevelopmentFlow()
    flow.plot()

if __name__ == "__main__":
    kickoff()
