from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai import LLM
from typing import List, Dict, Any, Tuple, Union, cast
import json
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from .models import ConceptExpansion, GameDesignDocument, TechnicalArchitecture, StyleGuide

def validate_concept_expansion(result: Any) -> Tuple[bool, Any]:
    """Validate that the ConceptExpansion model has been properly populated"""
    try:
        # Handle TaskOutput objects
        if hasattr(result, 'raw'):
            content = result.raw
        else:
            content = result
            
        # If it's already a dictionary, use it directly
        if isinstance(content, dict):
            data = content
        else:
            # Try to parse the result as JSON
            data = json.loads(content)
        
        # Check for required fields
        required_fields = [
            "title", "high_concept", "gameplay_mechanics", "levels", "enemies", 
            "player_character", "progression_system"
        ]
        
        for field in required_fields:
            if field not in data:
                return (False, f"Missing required field: {field}")
            
        # Check if there are at least 3 levels defined
        if len(data.get("levels", [])) < 3:
            return (False, "Please define at least 3 game levels")
            
        # Check if there are at least 3 enemy types
        if len(data.get("enemies", [])) < 3:
            return (False, "Please define at least 3 enemy types")
            
        # All validations passed
        return (True, result)
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        return (False, f"Validation error: {str(e)}")

@CrewBase
class ConceptCrew():
    """
    Concept Phase Crew for Game Development
    
    This crew handles the initial concept phase of game development, including:
    - Concept Expansion
    - Game Design Document Creation
    - Architecture Planning
    - Style Guide Definition
    """

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # LLM Configuration - Choose an appropriate model for creative tasks
    llm = LLM(model="openai/gpt-4o")
    
    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    
    @agent
    def concept_expander(self) -> Agent:
        """Game concept expansion specialist"""
        return Agent(
            config=self.agents_config['concept_expander'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def gdd_writer(self) -> Agent:
        """Game design document specialist"""
        return Agent(
            config=self.agents_config['gdd_writer'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def architecture_planner(self) -> Agent:
        """Game architecture planner"""
        return Agent(
            config=self.agents_config['architecture_planner'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def style_guide_creator(self) -> Agent:
        """Game style guide designer"""
        return Agent(
            config=self.agents_config['style_guide_creator'],
            llm=self.llm,
            verbose=True
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def concept_expansion_task(self) -> Task:
        """Expand the initial game concept into a comprehensive idea"""
        return Task(
            config=self.tasks_config['concept_expansion_task'],
            output_file='concept_expansion.md',
            output_pydantic=ConceptExpansion,
            guardrail=validate_concept_expansion
        )

    @task
    def gdd_creation_task(self) -> Task:
        """Create a comprehensive Game Design Document"""
        return Task(
            config=self.tasks_config['gdd_creation_task'],
            context=[self.concept_expansion_task()],
            output_file='game_design_document.md',
            output_pydantic=GameDesignDocument
        )

    @task
    def architecture_planning_task(self) -> Task:
        """Design the technical architecture for the game"""
        return Task(
            config=self.tasks_config['architecture_planning_task'],
            context=[self.concept_expansion_task(), self.gdd_creation_task()],
            output_file='technical_architecture.md',
            output_pydantic=TechnicalArchitecture
        )

    @task
    def style_guide_task(self) -> Task:
        """Create a comprehensive style guide for the game"""
        return Task(
            config=self.tasks_config['style_guide_task'],
            context=[self.concept_expansion_task(), self.gdd_creation_task()],
            output_file='style_guide.md',
            output_pydantic=StyleGuide
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Creates the Concept Crew for the initial phase of game development"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Tasks must be executed sequentially as each builds on the previous
            verbose=True,
            memory=True,  # Enable memory for context preservation
            function_calling_llm=self.llm  # Use the same LLM for function calling (structured output)
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Run the Concept Crew with the provided inputs
        
        Args:
            inputs: Dictionary containing at minimum the 'game_concept' key with the initial game concept
            
        Returns:
            The results of the crew execution, with structured Pydantic outputs
        """
        if not inputs or 'game_concept' not in inputs:
            raise ValueError("The 'game_concept' input is required to start the Concept Crew")
            
        # Run the crew
        crew_results = self.crew().kickoff(inputs=inputs)
        
        # Format outputs to ensure consistent structure
        formatted_results = {}
        
        # Structure the results by task
        for task_name, task_output in crew_results.items():
            if hasattr(task_output, 'raw'):
                raw_output = task_output.raw
            else:
                raw_output = task_output.get('output', '{}')
                
            # Make sure the output is a dict
            if isinstance(raw_output, str):
                try:
                    raw_output = json.loads(raw_output)
                except:
                    # If JSON parsing fails, wrap the string in an output field
                    raw_output = {"output": raw_output}
                    
            formatted_results[task_name] = {"output": raw_output}
            
        return formatted_results
