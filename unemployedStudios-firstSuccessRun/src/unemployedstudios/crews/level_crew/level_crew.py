from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any, Optional
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class LevelCrew:
    """
    Level System Crew responsible for developing the level system, map generation,
    progression system, and challenge balancing for the HTML5 game.
    
    Integration points:
    - GameLogic.constructor() - For level system initialization
    - GameLogic.update() - For level state updates
    - Game.constructor() - For level management options
    - Helper methods for level creation and progression
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
        os.makedirs("GameGenerationOutput", exist_ok=True)
    
    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    
    @agent
    def template_integrator(self) -> Agent:
        """Template Integrator responsible for analyzing the template and planning level system integration"""
        return Agent(
            config=self.agents_config["template_integrator"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def level_design_architect(self) -> Agent:
        """Level Design Architect responsible for creating the core level system"""
        return Agent(
            config=self.agents_config["level_design_architect"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def map_generator(self) -> Agent:
        """Map Generator responsible for level data representation and generation"""
        return Agent(
            config=self.agents_config["map_generator"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def progress_system_developer(self) -> Agent:
        """Progress System Developer responsible for player progression and level unlocking"""
        return Agent(
            config=self.agents_config["progress_system_developer"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def challenge_balancing_expert(self) -> Agent:
        """Challenge Balancing Expert responsible for difficulty progression"""
        return Agent(
            config=self.agents_config["challenge_balancing_expert"],
            llm=self.llm,
            verbose=True
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def integration_planning_task(self) -> Task:
        """Task to analyze the template and plan level system integration"""
        return Task(
            config=self.tasks_config["integration_planning_task"]
        )
    
    @task
    def level_system_task(self) -> Task:
        """Task to develop the core level system that extends the template"""
        return Task(
            config=self.tasks_config["level_system_task"],
            context=[self.integration_planning_task()]
        )

    @task
    def map_generation_task(self) -> Task:
        """Task to create the map generation and management systems"""
        return Task(
            config=self.tasks_config["map_generation_task"],
            context=[self.integration_planning_task(), self.level_system_task()]
        )

    @task
    def progression_system_task(self) -> Task:
        """Task to implement player progression through levels"""
        return Task(
            config=self.tasks_config["progression_system_task"],
            context=[self.integration_planning_task(), self.level_system_task(), self.map_generation_task()]
        )

    @task
    def challenge_balancing_task(self) -> Task:
        """Task to develop difficulty progression and challenge balancing"""
        return Task(
            config=self.tasks_config["challenge_balancing_task"],
            context=[self.integration_planning_task(), self.level_system_task(), self.map_generation_task(), self.progression_system_task()]
        )

    @task
    def game_logic_extensions(self) -> Task:
        """Task to finalize GameLogic class extensions for the level system"""
        return Task(
            config=self.tasks_config["game_logic_extensions"],
            context=[self.integration_planning_task(), self.level_system_task(), self.map_generation_task(), 
                     self.progression_system_task(), self.challenge_balancing_task()],
            output_file="GameGenerationOutput/game_logic_extensions.js"
        )
        
    @task
    def game_class_extensions(self) -> Task:
        """Task to finalize Game class extensions for the level system"""
        return Task(
            config=self.tasks_config["game_class_extensions"],
            context=[self.integration_planning_task(), self.level_system_task(), self.map_generation_task(), 
                     self.progression_system_task(), self.challenge_balancing_task()],
            output_file="GameGenerationOutput/game_class_extensions.js"
        )

    @task
    def legacy_integration_task(self) -> Task:
        """Task to generate a legacy standalone file for backward compatibility"""
        return Task(
            config=self.tasks_config["legacy_integration_task"],
            context=[self.game_logic_extensions(), self.game_class_extensions()],
            output_file="GameGenerationOutput/game_levels.js"
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Creates the Level Crew for developing the level system"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Run the Level Crew with the provided inputs
        
        Args:
            inputs: Dictionary containing:
                - 'core_systems_design': Technical design for core systems
                - 'component_interfaces': Interface definitions
                - 'concept_expansion': Concept expansion containing level information
                - 'refined_technical_design': Refined technical design
                - 'template_analysis': Analysis of the HTML5 template structure
                - 'integration_mapping': Mapping of where to integrate code
                - 'game_template_path': Path to the HTML5 game template
                - 'template_game_logic_insertion_point': Where to insert GameLogic extensions
                - 'template_game_class_insertion_point': Where to insert Game class extensions
                - 'game_engine_file': Previously generated engine file (for reference)
                - 'game_entities_file': Previously generated entities file (for reference)
            
        Returns:
            The results of the crew execution with extensions for Game and GameLogic classes
        """
        required_inputs = ['core_systems_design', 'component_interfaces', 'concept_expansion', 'template_analysis', 'game_template_path']
        for input_name in required_inputs:
            if not inputs or input_name not in inputs:
                raise ValueError(f"The '{input_name}' input is required for the Level Crew")
        
        return self.crew().kickoff(inputs=inputs)
