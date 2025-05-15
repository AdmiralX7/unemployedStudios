#!/usr/bin/env python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from crewai.flow import Flow, listen, start, router
from unemployedstudios.crews.concept_crew import ConceptCrew
from unemployedstudios.crews.concept_crew.models import ConceptExpansion, GameDesignDocument, TechnicalArchitecture, StyleGuide, GameplayMechanic, Character, Enemy, Level, MonetizationStrategy
from unemployedstudios.crews.technical_design_crew import TechnicalDesignCrew
import json
import os

class GameDevelopmentState(BaseModel):
    # Initial inputs
    game_concept: str = ""
    
    # Concept Phase outputs (structured with Pydantic models)
    concept_expansion: Optional[ConceptExpansion] = None
    game_design_document: Optional[GameDesignDocument] = None
    technical_architecture: Optional[TechnicalArchitecture] = None
    style_guide: Optional[StyleGuide] = None
    
    # Technical Design Phase outputs
    core_systems_design: Optional[Dict[str, Any]] = None
    component_interfaces: Optional[Dict[str, Any]] = None
    design_validation: Optional[Dict[str, Any]] = None
    refined_technical_design: Optional[Dict[str, Any]] = None
    
    # Status tracking
    concept_phase_complete: bool = False
    technical_design_phase_complete: bool = False

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
        - Core Systems Design
        - Component Interface Definition
        - Design Validation
        - Design Refinement (feedback loop)
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
                "enemy_names": enemy_names
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
                    
                    # Also extract specific outputs if available
                    if hasattr(tech_design_output, 'core_systems_design_task'):
                        self.state.core_systems_design = tech_design_output.core_systems_design_task
                    else:
                        self.state.core_systems_design = tech_design_data
                    
                    if hasattr(tech_design_output, 'interface_definition_task'):
                        self.state.component_interfaces = tech_design_output.interface_definition_task
                    else:
                        self.state.component_interfaces = tech_design_data
                    
                    if hasattr(tech_design_output, 'design_validation_task'):
                        self.state.design_validation = tech_design_output.design_validation_task
                    else:
                        self.state.design_validation = tech_design_data
                    
                    if hasattr(tech_design_output, 'design_refinement_task'):
                        self.state.refined_technical_design = tech_design_output.design_refinement_task
                    else:
                        self.state.refined_technical_design = tech_design_data
                    
                except json.JSONDecodeError:
                    # If not valid JSON, wrap it in a content field
                    with open(self._get_output_path("technical_design_output.json"), "w") as f:
                        json.dump({"content": tech_design_output.raw}, f, indent=2)
                        
                    self.state.core_systems_design = {"content": tech_design_output.raw}
                    self.state.component_interfaces = {"content": tech_design_output.raw}
                    self.state.design_validation = {"content": tech_design_output.raw}
                    self.state.refined_technical_design = {"content": tech_design_output.raw}
            else:
                raw_output = str(tech_design_output)
                with open(self._get_output_path("technical_design_output.json"), "w") as f:
                    json.dump({"content": raw_output}, f, indent=2)
                    
                self.state.core_systems_design = {"content": raw_output}
                self.state.component_interfaces = {"content": raw_output}
                self.state.design_validation = {"content": raw_output}
                self.state.refined_technical_design = {"content": raw_output}
        except Exception as e:
            print(f"Error processing technical design output: {str(e)}")
            # Continue anyway - we've saved the raw outputs
        
        # Mark the technical design phase as complete
        self.state.technical_design_phase_complete = True
        
        print("Technical Design Phase completed successfully")
        
        return "Technical Design Phase completed successfully"
    
    @router(condition=technical_design_phase)
    def route_to_next_phase(self):
        """Route to the next phase based on the current state"""
        if self.state.technical_design_phase_complete:
            print("Technical Design Phase completed. Moving to Code Generation Phase.")
            # In a full implementation, this would return the code generation phase step
            return None
        elif self.state.concept_phase_complete:
            print("Concept Phase completed. Moving to Technical Design Phase.")
            return self.technical_design_phase
        else:
            # If concept phase isn't complete, this shouldn't happen
            print("Error: Concept Phase was not completed successfully.")
            return None

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
