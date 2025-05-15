from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any, Optional
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class EngineCrew:
    """
    Engine Crew responsible for developing the core game engine for the HTML5 game.
    This crew develops template extensions for the game loop, rendering pipeline, and input handling.
    Integration points:
    - Game.constructor() - For initialization
    - Game.updateGame() - For main update loop 
    - Game.gameLoop() - For timing and rendering
    - Helper methods for GameLogic and Game classes
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
        """Template Integrator responsible for analyzing the template and planning the integration"""
        return Agent(
            config=self.agents_config["template_integrator"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def game_loop_architect(self) -> Agent:
        """Game Loop Architect responsible for extending the template Game class"""
        return Agent(
            config=self.agents_config["game_loop_architect"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def rendering_engine_developer(self) -> Agent:
        """Rendering Engine Developer responsible for creating visual rendering extensions"""
        return Agent(
            config=self.agents_config["rendering_engine_developer"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def input_system_specialist(self) -> Agent:
        """Input System Specialist responsible for enhancing user input handling"""
        return Agent(
            config=self.agents_config["input_system_specialist"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def performance_optimizer(self) -> Agent:
        """Performance Optimizer responsible for ensuring game engine efficiency"""
        return Agent(
            config=self.agents_config["performance_optimizer"],
            llm=self.llm,
            verbose=True
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def integration_planning_task(self) -> Task:
        """Task to analyze the template and plan integration points"""
        return Task(
            config=self.tasks_config["integration_planning_task"]
        )
    
    @task
    def game_loop_extension_task(self) -> Task:
        """Task to develop extensions for the template Game class"""
        return Task(
            config=self.tasks_config["game_loop_extension_task"],
            context=[self.integration_planning_task()],
            output_file="GameGenerationOutput/game_class_extensions.js"
        )

    @task
    def game_logic_extension_task(self) -> Task:
        """Task to develop extensions for the template GameLogic class"""
        return Task(
            config=self.tasks_config["game_logic_extension_task"],
            context=[self.integration_planning_task(), self.game_loop_extension_task()],
            output_file="GameGenerationOutput/game_logic_extensions.js"
        )

    @task
    def rendering_system_task(self) -> Task:
        """Task to create rendering system extensions"""
        return Task(
            config=self.tasks_config["rendering_system_task"],
            context=[self.integration_planning_task(), self.game_loop_extension_task(), self.game_logic_extension_task()]
        )

    @task
    def input_system_task(self) -> Task:
        """Task to develop input handling system extensions"""
        return Task(
            config=self.tasks_config["input_system_task"],
            context=[self.integration_planning_task(), self.game_loop_extension_task(), 
                     self.game_logic_extension_task(), self.rendering_system_task()]
        )

    @task
    def performance_optimization_task(self) -> Task:
        """Task to optimize the game engine extensions"""
        return Task(
            config=self.tasks_config["performance_optimization_task"],
            context=[self.game_loop_extension_task(), self.game_logic_extension_task(), 
                     self.rendering_system_task(), self.input_system_task()]
        )

    @task
    def game_class_extensions(self) -> Task:
        """Task to finalize Game class extensions"""
        return Task(
            config=self.tasks_config["game_class_extensions"],
            context=[self.integration_planning_task(), self.game_loop_extension_task(), 
                     self.rendering_system_task(), self.input_system_task(), self.performance_optimization_task()],
            output_file="GameGenerationOutput/game_class_extensions.js"
        )
        
    @task
    def game_logic_extensions(self) -> Task:
        """Task to finalize GameLogic class extensions"""
        return Task(
            config=self.tasks_config["game_logic_extensions"],
            context=[self.integration_planning_task(), self.game_logic_extension_task(), 
                     self.rendering_system_task(), self.input_system_task(), self.performance_optimization_task()],
            output_file="GameGenerationOutput/game_logic_extensions.js"
        )

    @task
    def legacy_integration_task(self) -> Task:
        """Task to generate a legacy standalone file for backward compatibility"""
        return Task(
            config=self.tasks_config["legacy_integration_task"],
            context=[self.game_class_extensions(), self.game_logic_extensions()],
            output_file="GameGenerationOutput/game_engine.js"
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Creates the Engine Crew for developing the core game engine"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Run the Engine Crew with the provided inputs
        
        Args:
            inputs: Dictionary containing:
                - 'core_systems_design': Technical design for core systems
                - 'component_interfaces': Interface definitions
                - 'refined_technical_design': Refined technical design
                - 'template_analysis': Analysis of the HTML5 template structure
                - 'integration_mapping': Mapping of where to integrate code
                - 'game_template_path': Path to the HTML5 game template
                - 'template_game_class_insertion_point': Where to insert Game class extensions
                - 'template_game_logic_insertion_point': Where to insert GameLogic extensions
            
        Returns:
            The results of the crew execution with extensions for Game and GameLogic classes
        """
        required_inputs = ['core_systems_design', 'component_interfaces', 'template_analysis', 'game_template_path']
        for input_name in required_inputs:
            if not inputs or input_name not in inputs:
                raise ValueError(f"The '{input_name}' input is required for the Engine Crew")
        
        return self.crew().kickoff(inputs=inputs)
