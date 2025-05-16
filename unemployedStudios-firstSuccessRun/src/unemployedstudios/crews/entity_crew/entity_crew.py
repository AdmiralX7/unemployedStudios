from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any, Optional
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class EntityCrew:
    """
    Entity System Crew responsible for developing the entity framework, component system,
    physics implementation, and entity behaviors for the HTML5 game.
    
    Integration points:
    - GameLogic.constructor() - For entity system initialization
    - GameLogic.update() - For entity and physics updates
    - Helper methods for entity creation and management
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
        """Template Integrator responsible for analyzing the template and planning entity integration"""
        return Agent(
            config=self.agents_config["template_integrator"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def entity_framework_developer(self) -> Agent:
        """Entity Framework Developer responsible for creating the core entity system"""
        return Agent(
            config=self.agents_config["entity_framework_developer"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def component_system_designer(self) -> Agent:
        """Component System Designer responsible for creating the modular component architecture"""
        return Agent(
            config=self.agents_config["component_system_designer"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def physics_implementation_expert(self) -> Agent:
        """Physics Implementation Expert responsible for entity physics and collisions"""
        return Agent(
            config=self.agents_config["physics_implementation_expert"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def entity_behavior_specialist(self) -> Agent:
        """Entity Behavior Specialist responsible for AI and behavior patterns"""
        return Agent(
            config=self.agents_config["entity_behavior_specialist"],
            llm=self.llm,
            verbose=True
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def integration_planning_task(self) -> Task:
        """Task to analyze the template and plan entity system integration"""
        return Task(
            config=self.tasks_config["integration_planning_task"]
        )
    
    @task
    def entity_framework_task(self) -> Task:
        """Task to develop the core entity framework that extends the template"""
        return Task(
            config=self.tasks_config["entity_framework_task"],
            context=[self.integration_planning_task()]
        )

    @task
    def component_system_task(self) -> Task:
        """Task to create the component system"""
        return Task(
            config=self.tasks_config["component_system_task"],
            context=[self.integration_planning_task(), self.entity_framework_task()]
        )

    @task
    def physics_system_task(self) -> Task:
        """Task to implement physics for entities"""
        return Task(
            config=self.tasks_config["physics_system_task"],
            context=[self.integration_planning_task(), self.entity_framework_task(), self.component_system_task()]
        )

    @task
    def entity_behavior_task(self) -> Task:
        """Task to develop entity behaviors and AI"""
        return Task(
            config=self.tasks_config["entity_behavior_task"],
            context=[self.integration_planning_task(), self.entity_framework_task(), self.component_system_task(), self.physics_system_task()]
        )

    @task
    def game_logic_extensions(self) -> Task:
        """Task to finalize GameLogic class extensions for the entity system"""
        return Task(
            config=self.tasks_config["game_logic_extensions"],
            context=[self.integration_planning_task(), self.entity_framework_task(), self.component_system_task(), 
                     self.physics_system_task(), self.entity_behavior_task()],
            output_file="GameGenerationOutput/game_logic_extensions.js"
        )

    @task
    def legacy_integration_task(self) -> Task:
        """Task to generate a legacy standalone file for backward compatibility"""
        return Task(
            config=self.tasks_config["legacy_integration_task"],
            context=[self.game_logic_extensions()],
            output_file="GameGenerationOutput/game_entities.js"
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Creates the Entity Crew for developing the entity system"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Run the Entity Crew with the provided inputs
        
        Args:
            inputs: Dictionary containing:
                - 'core_systems_design': Technical design for core systems
                - 'component_interfaces': Interface definitions
                - 'refined_technical_design': Refined technical design
                - 'template_analysis': Analysis of the HTML5 template structure
                - 'integration_mapping': Mapping of where to integrate code
                - 'game_template_path': Path to the HTML5 game template
                - 'template_game_logic_insertion_point': Where to insert GameLogic extensions
                - 'game_engine_segments': Previously generated engine segments (optional)
                - 'game_engine_file': Previously generated engine file (for backward compatibility)
            
        Returns:
            The results of the crew execution with extensions for GameLogic class
        """
        required_inputs = ['core_systems_design', 'component_interfaces', 'template_analysis', 'game_template_path']
        for input_name in required_inputs:
            if not inputs or input_name not in inputs:
                raise ValueError(f"The '{input_name}' input is required for the Entity Crew")
        
        return self.crew().kickoff(inputs=inputs)
