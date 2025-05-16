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
import json
import os

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
            
            # Process segmented code output for template integration
            if hasattr(engine_output, 'game_class_extensions'):
                # Store code segments for template integration
                self.state.game_engine_segments = {}
                self.state.game_engine_segments['game_class'] = engine_output.game_class_extensions
                print(f"Successfully generated Game class extensions ({len(engine_output.game_class_extensions)} bytes)")
                
            if hasattr(engine_output, 'game_logic_extensions'):
                if not self.state.game_engine_segments:
                    self.state.game_engine_segments = {}
                self.state.game_engine_segments['game_logic'] = engine_output.game_logic_extensions
                print(f"Successfully generated GameLogic extensions ({len(engine_output.game_logic_extensions)} bytes)")
            
            # For backward compatibility, still check for the standalone file
            engine_file_path = "GameGenerationOutput/game_engine.js"
            if os.path.exists(engine_file_path):
                with open(engine_file_path, "r") as f:
                    engine_code = f.read()
                self.state.game_engine_file = engine_code
                print(f"Also found legacy game_engine.js ({len(engine_code)} bytes)")
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
        except Exception as e:
            print(f"Error processing engine output: {str(e)}")
            # Continue anyway - we've saved the raw outputs
        
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
            
            # Process segmented code output for template integration
            if hasattr(entity_output, 'game_logic_extensions'):
                # Store code segments for template integration
                self.state.game_entities_segments = {}
                self.state.game_entities_segments['game_logic'] = entity_output.game_logic_extensions
                print(f"Successfully generated GameLogic entity extensions ({len(entity_output.game_logic_extensions)} bytes)")
            
            # For backward compatibility, still check for the standalone file
            entity_file_path = "GameGenerationOutput/game_entities.js"
            if os.path.exists(entity_file_path):
                with open(entity_file_path, "r") as f:
                    entity_code = f.read()
                self.state.game_entities_file = entity_code
                print(f"Also found legacy game_entities.js ({len(entity_code)} bytes)")
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
                    else:
                        print("Warning: No entity code segments or files were generated")
        except Exception as e:
            print(f"Error processing entity output: {str(e)}")
            # Continue anyway - we've saved the raw outputs
        
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
            
            # Process segmented code output for template integration
            if hasattr(level_output, 'game_logic_extensions'):
                # Store code segments for template integration
                self.state.game_levels_segments = {}
                self.state.game_levels_segments['game_logic'] = level_output.game_logic_extensions
                print(f"Successfully generated GameLogic level extensions ({len(level_output.game_logic_extensions)} bytes)")
                
            if hasattr(level_output, 'game_class_extensions'):
                if not self.state.game_levels_segments:
                    self.state.game_levels_segments = {}
                self.state.game_levels_segments['game_class'] = level_output.game_class_extensions
                print(f"Successfully generated Game class level extensions ({len(level_output.game_class_extensions)} bytes)")
            
            # For backward compatibility, still check for the standalone file
            level_file_path = "GameGenerationOutput/game_levels.js"
            if os.path.exists(level_file_path):
                with open(level_file_path, "r") as f:
                    level_code = f.read()
                self.state.game_levels_file = level_code
                print(f"Also found legacy game_levels.js ({len(level_code)} bytes)")
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
        except Exception as e:
            print(f"Error processing level output: {str(e)}")
            # Continue anyway - we've saved the raw outputs
        
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
            
            # Process segmented code output for template integration
            if hasattr(ui_output, 'game_ui_extensions'):
                # Store code segments for template integration
                self.state.game_ui_segments = {}
                self.state.game_ui_segments['game_ui'] = ui_output.game_ui_extensions
                print(f"Successfully generated GameUI extensions ({len(ui_output.game_ui_extensions)} bytes)")
                
            if hasattr(ui_output, 'css_extensions'):
                if not self.state.game_ui_segments:
                    self.state.game_ui_segments = {}
                self.state.game_ui_segments['css'] = ui_output.css_extensions
                print(f"Successfully generated CSS extensions ({len(ui_output.css_extensions)} bytes)")
                
            if hasattr(ui_output, 'audio_extensions'):
                if not self.state.game_ui_segments:
                    self.state.game_ui_segments = {}
                self.state.game_ui_segments['audio'] = ui_output.audio_extensions
                print(f"Successfully generated audio extensions ({len(ui_output.audio_extensions)} bytes)")
            
            # For backward compatibility, still check for the standalone file
            ui_file_path = "GameGenerationOutput/game_ui.js"
            if os.path.exists(ui_file_path):
                with open(ui_file_path, "r") as f:
                    ui_code = f.read()
                self.state.game_ui_file = ui_code
                print(f"Also found legacy game_ui.js ({len(ui_code)} bytes)")
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
        except Exception as e:
            print(f"Error processing ui output: {str(e)}")
            # Continue anyway - we've saved the raw outputs
        
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
        
        # Create validation report containers
        validation_results = {
            "game_class": {"valid": False, "message": "Not processed yet"},
            "game_logic": {"valid": False, "message": "Not processed yet"},
            "game_ui": {"valid": False, "message": "Not processed yet"},
            "css": {"valid": False, "message": "Not processed yet"},
            "audio": {"valid": False, "message": "Not processed yet"}
        }
        
        # Collect all code segments into structured containers for validation
        integration_content = {
            "css": "",
            "audio": "",
            "game_ui": "",
            "game_logic": "",
            "game_class": ""
        }
        
        # Collect segments from engine code
        if self.state.game_engine_segments:
            if 'game_logic' in self.state.game_engine_segments:
                integration_content["game_logic"] += self.state.game_engine_segments['game_logic'] + "\n\n"
            if 'game_class' in self.state.game_engine_segments:
                integration_content["game_class"] += self.state.game_engine_segments['game_class'] + "\n\n"
        
        # Collect segments from entity code
        if self.state.game_entities_segments:
            if 'game_logic' in self.state.game_entities_segments:
                integration_content["game_logic"] += self.state.game_entities_segments['game_logic'] + "\n\n"
        
        # Collect segments from level code
        if self.state.game_levels_segments:
            if 'game_logic' in self.state.game_levels_segments:
                integration_content["game_logic"] += self.state.game_levels_segments['game_logic'] + "\n\n"
            if 'game_class' in self.state.game_levels_segments:
                integration_content["game_class"] += self.state.game_levels_segments['game_class'] + "\n\n"
        
        # Collect segments from UI code
        if self.state.game_ui_segments:
            if 'game_ui' in self.state.game_ui_segments:
                integration_content["game_ui"] += self.state.game_ui_segments['game_ui'] + "\n\n"
            if 'css' in self.state.game_ui_segments:
                integration_content["css"] += self.state.game_ui_segments['css'] + "\n\n"
            if 'audio' in self.state.game_ui_segments:
                integration_content["audio"] += self.state.game_ui_segments['audio'] + "\n\n"
        
        # Define required patterns for each segment type
        required_patterns = {
            "game_class": [],  # Example: ["update", "render"]
            "game_logic": [],  # Example: ["update", "collision"]
            "game_ui": [],     # Example: ["draw", "update"]
            "css": [],         # Example: ["game-container", "player"]
            "audio": []        # Example: ["<audio", "src="]
        }
        
        # Validate each segment before integration
        for segment_type, content in integration_content.items():
            if content:
                is_valid, sanitized_content, error = self._validate_code_segment(
                    segment_type, 
                    content, 
                    required_patterns.get(segment_type)
                )
                
                if is_valid:
                    integration_content[segment_type] = sanitized_content
                    validation_results[segment_type] = {"valid": True, "message": "Validation passed"}
                    print(f"✅ {segment_type} code segment validation passed")
                else:
                    print(f"⚠️ {segment_type} validation failed: {error}")
                    validation_results[segment_type] = {"valid": False, "message": error}
                    
                    # Attempt to recover by using legacy files if available
                    if segment_type == "game_class" or segment_type == "game_logic":
                        if self.state.game_engine_file:
                            print(f"Attempting recovery of {segment_type} from legacy engine file")
                            # For simplicity, using the whole file (in a real system, you'd extract relevant parts)
                            is_valid, sanitized_content, error = self._validate_code_segment(
                                segment_type, 
                                self.state.game_engine_file
                            )
                            if is_valid:
                                integration_content[segment_type] = sanitized_content
                                validation_results[segment_type] = {"valid": True, "message": "Recovered from legacy file"}
                                print(f"✅ Recovered {segment_type} from legacy file")
        else:
            print(f"⚠️ No content available for {segment_type} segment")
            validation_results[segment_type] = {"valid": False, "message": "No content available"}
        
        # Save validation report
        with open(self._get_output_path("validation_report.json"), "w") as f:
            json.dump(validation_results, f, indent=2)
        
        # Integrate all code segments into the final game executable
        try:
            # Read the template HTML file
            try:
                with open(self.state.game_template_path, "r") as f:
                    template_content = f.read()
                print(f"Successfully loaded template from {self.state.game_template_path}")
            except Exception as e:
                print(f"Error reading template file: {str(e)}")
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
                    print("Failed to load template from any location. Integration cannot proceed.")
                    return "Template Integration Failed: No template found"
            
            # Verify that the template has the necessary markers
            integration_points = {
                "css": self.state.template_css_insertion_point or "/*Your style goes here */",
                "audio": self.state.template_audio_insertion_point or "<!--Extra audio tags for sound effects-->",
                "game_ui": self.state.template_game_ui_insertion_point or "class GameUI {",
                "game_logic": self.state.template_game_logic_insertion_point or "class GameLogic {",
                "game_class": self.state.template_game_class_insertion_point or "class Game {"
            }
            
            # Verify each marker exists in the template
            missing_markers = []
            for point_type, marker in integration_points.items():
                if marker not in template_content:
                    missing_markers.append(f"{point_type} ({marker})")
                    print(f"⚠️ Warning: {point_type} insertion marker '{marker}' not found in template")
            
            if missing_markers:
                print(f"Some insertion markers are missing: {', '.join(missing_markers)}")
                print("Integration will proceed but some code segments may not be properly inserted")
            
            # Clone the template for integration
            updated_template = template_content
            
            # Perform integration for each validated segment
            for point_type, marker in integration_points.items():
                content = integration_content[point_type]
                if content and validation_results[point_type]["valid"]:
                    print(f"Integrating {point_type} code segment...")
                    
                    # Handle class definitions differently - need to insert after class declaration, not replace it
                    if point_type in ["game_ui", "game_logic", "game_class"]:
                        # Find the class declaration and add our content after it but before the constructor
                        # Look for the class opening brace and constructor
                        class_pattern = marker
                        if class_pattern in updated_template:
                            # Find the position after the class declaration
                            class_pos = updated_template.find(class_pattern)
                            if class_pos >= 0:
                                # Find the opening brace after the class declaration
                                open_brace_pos = updated_template.find("{", class_pos)
                                if open_brace_pos >= 0:
                                    # Find the constructor (if any) or the position to insert
                                    constructor_pattern = "constructor"
                                    constructor_pos = updated_template.find(constructor_pattern, open_brace_pos)
                                    
                                    insertion_point = None
                                    
                                    if constructor_pos >= 0:
                                        # Find the end of the constructor (balanced braces)
                                        pos = constructor_pos
                                        brace_count = 0
                                        in_constructor = False
                                        
                                        # Skip past the constructor keyword
                                        pos = updated_template.find("(", pos)
                                        if pos >= 0:
                                            # Find the opening brace of the constructor
                                            pos = updated_template.find("{", pos)
                                            if pos >= 0:
                                                brace_count = 1
                                                in_constructor = True
                                                pos += 1
                                                
                                                # Find the matching closing brace
                                                while pos < len(updated_template) and brace_count > 0:
                                                    if updated_template[pos] == "{":
                                                        brace_count += 1
                                                    elif updated_template[pos] == "}":
                                                        brace_count -= 1
                                                    pos += 1
                                                    
                                                if brace_count == 0:
                                                    # We found the end of the constructor, insert after it
                                                    insertion_point = pos
                                                    updated_template = (
                                                        updated_template[:insertion_point] + 
                                                        "\n    // " + point_type.upper() + " EXTENSIONS\n    " + 
                                                        content.replace("\n", "\n    ") + 
                                                        updated_template[insertion_point:]
                                                    )
                                                    print(f"Inserted {point_type} content after constructor")
                                
                                    # If we couldn't find or process the constructor, insert after the opening brace
                                    if insertion_point is None:
                                        insertion_point = open_brace_pos + 1
                                        updated_template = (
                                            updated_template[:insertion_point] + 
                                            "\n    // " + point_type.upper() + " EXTENSIONS\n    " + 
                                            content.replace("\n", "\n    ") + 
                                            updated_template[insertion_point:]
                                        )
                                        print(f"Inserted {point_type} content at beginning of class")
                        else:
                            print(f"Warning: Could not find {point_type} marker in template")
                    
                    elif point_type == "css":
                        # For CSS, use proper CSS comment syntax and indentation
                        if marker in updated_template:
                            updated_template = updated_template.replace(
                                marker,
                                marker + "\n\n/* GENERATED CSS EXTENSIONS */\n" + content
                            )
                            print(f"Inserted CSS content at marker: {marker}")
                        else:
                            print(f"Warning: CSS marker '{marker}' not found in template")
                    
                    elif point_type == "audio":
                        # For audio tags, use HTML comment syntax
                        if marker in updated_template:
                            updated_template = updated_template.replace(
                                marker,
                                marker + "\n\n<!-- GENERATED AUDIO EXTENSIONS -->\n" + content
                            )
                            print(f"Inserted audio content at marker: {marker}")
                        else:
                            print(f"Warning: Audio marker '{marker}' not found in template")
            
            # Save the integrated template as the final game
            final_game_path = self._get_output_path("final_game.html")
            with open(final_game_path, "w") as f:
                f.write(updated_template)
            
            print(f"Successfully integrated all valid code into final game HTML file at {final_game_path}")
            
            # Also save a backup copy
            backup_path = self._get_output_path("final_game_backup.html")
            with open(backup_path, "w") as f:
                f.write(updated_template)
            
            # Also generate a legacy JavaScript file for reference
            with open(self._get_output_path("final_game_executable.js"), "w") as f:
                f.write("// COMBINED GAME CODE FOR REFERENCE\n\n")
                
                # Only include segments that passed validation
                for segment_type, result in validation_results.items():
                    if result["valid"]:
                        f.write(f"// {segment_type.upper()} EXTENSIONS\n")
                        f.write(integration_content[segment_type] + "\n\n")
                    else:
                        f.write(f"// {segment_type.upper()} EXTENSIONS - VALIDATION FAILED: {result['message']}\n\n")
            
            print(f"Also generated legacy combined JavaScript file for reference")
            
        except Exception as e:
            print(f"Error integrating code segments: {str(e)}")
            import traceback
            traceback.print_exc()
            return "Template Integration Failed with error: " + str(e)
        
        # Mark the template integration phase as complete
        self.state.template_integration_complete = True
        
        print("Template Integration Phase completed successfully with validation")
        
        return "Template Integration Phase completed successfully with validation"

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
