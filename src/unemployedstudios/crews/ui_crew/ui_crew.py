from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any, Optional
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class UICrew:
    """
    UI System Crew responsible for developing the UI framework, components, screens,
    responsive layouts, and animations for the HTML5 game.
    
    Integration points:
    - GameUI.constructor() - For UI system initialization
    - GameUI methods - For UI rendering and interactions
    - CSS styles - For visual styling
    - Audio elements - For UI sound effects
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
        """Template Integrator responsible for analyzing the template and planning UI integration"""
        return Agent(
            config=self.agents_config["template_integrator"],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def ui_framework_developer(self) -> Agent:
        """UI Framework Developer responsible for creating the core UI architecture"""
        return Agent(
            config=self.agents_config["ui_framework_developer"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def user_experience_designer(self) -> Agent:
        """User Experience Designer responsible for creating intuitive UI screens and components"""
        return Agent(
            config=self.agents_config["user_experience_designer"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def responsive_design_expert(self) -> Agent:
        """Responsive Design Expert responsible for adapting UI to different screen sizes"""
        return Agent(
            config=self.agents_config["responsive_design_expert"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def animation_specialist(self) -> Agent:
        """Animation Specialist responsible for UI transitions and feedback animations"""
        return Agent(
            config=self.agents_config["animation_specialist"],
            llm=self.llm,
            verbose=True
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def integration_planning_task(self) -> Task:
        """Task to analyze the template and plan UI system integration"""
        return Task(
            config=self.tasks_config["integration_planning_task"]
        )
    
    @task
    def ui_framework_task(self) -> Task:
        """Task to develop the core UI framework that extends the template"""
        return Task(
            config=self.tasks_config["ui_framework_task"],
            context=[self.integration_planning_task()]
        )

    @task
    def user_experience_task(self) -> Task:
        """Task to create UI screens and components"""
        return Task(
            config=self.tasks_config["user_experience_task"],
            context=[self.integration_planning_task(), self.ui_framework_task()]
        )

    @task
    def responsive_design_task(self) -> Task:
        """Task to implement responsive layout systems"""
        return Task(
            config=self.tasks_config["responsive_design_task"],
            context=[self.integration_planning_task(), self.ui_framework_task(), self.user_experience_task()]
        )

    @task
    def animation_task(self) -> Task:
        """Task to develop UI animations and transitions"""
        return Task(
            config=self.tasks_config["animation_task"],
            context=[self.integration_planning_task(), self.ui_framework_task(), self.user_experience_task(), self.responsive_design_task()]
        )

    @task
    def game_ui_extensions(self) -> Task:
        """Task to finalize GameUI class extensions for the UI system"""
        return Task(
            config=self.tasks_config["game_ui_extensions"],
            context=[self.integration_planning_task(), self.ui_framework_task(), self.user_experience_task(), 
                     self.responsive_design_task(), self.animation_task()],
            output_file="GameGenerationOutput/game_ui_extensions.js"
        )
        
    @task
    def css_extensions(self) -> Task:
        """Task to finalize CSS style extensions for the UI system"""
        return Task(
            config=self.tasks_config["css_extensions"],
            context=[self.integration_planning_task(), self.ui_framework_task(), self.user_experience_task(), 
                     self.responsive_design_task(), self.animation_task()],
            output_file="GameGenerationOutput/css_extensions.js"
        )
        
    @task
    def audio_extensions(self) -> Task:
        """Task to finalize audio element extensions for the UI system"""
        return Task(
            config=self.tasks_config["audio_extensions"],
            context=[self.integration_planning_task(), self.ui_framework_task(), self.user_experience_task(), 
                     self.responsive_design_task(), self.animation_task()],
            output_file="GameGenerationOutput/audio_extensions.js"
        )

    @task
    def legacy_integration_task(self) -> Task:
        """Task to generate a legacy standalone file for backward compatibility"""
        return Task(
            config=self.tasks_config["legacy_integration_task"],
            context=[self.game_ui_extensions(), self.css_extensions(), self.audio_extensions()],
            output_file="GameGenerationOutput/game_ui.js"
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Creates the UI Crew for developing the UI system"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Run the UI Crew with the provided inputs
        
        Args:
            inputs: Dictionary containing:
                - 'style_guide': Style guide for visual design
                - 'component_interfaces': Interface definitions
                - 'core_systems_design': Core systems design
                - 'template_analysis': Analysis of the HTML5 template structure
                - 'integration_mapping': Mapping of where to integrate code
                - 'game_template_path': Path to the HTML5 game template
                - 'template_game_ui_insertion_point': Where to insert GameUI extensions
                - 'template_css_insertion_point': Where to insert CSS extensions
                - 'template_audio_insertion_point': Where to insert audio extensions
                - 'game_engine_file': Previously generated engine file (for reference)
                - 'game_entities_file': Previously generated entities file (for reference)
                - 'game_levels_file': Previously generated levels file (for reference)
            
        Returns:
            The results of the crew execution with extensions for GameUI, CSS, and audio elements
        """
        required_inputs = ['style_guide', 'component_interfaces', 'core_systems_design', 'template_analysis', 'game_template_path']
        for input_name in required_inputs:
            if not inputs or input_name not in inputs:
                raise ValueError(f"The '{input_name}' input is required for the UI Crew")
        
        return self.crew().kickoff(inputs=inputs)
