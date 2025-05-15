from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai import LLM
from typing import List, Dict, Any
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class TechnicalDesignCrew():
    """
    Technical Design Phase Crew for Game Development
    
    This crew handles the technical design phase of game development, including:
    - Template Analysis
    - Integration Planning
    - Component Interface Definition
    - Design Validation and Refinement
    """

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # LLM Configuration - Choose an appropriate model for technical tasks
    llm = LLM(model="openai/gpt-4o")
    
    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    
    @agent
    def template_analyzer(self) -> Agent:
        """Template analyzer for HTML5 game template"""
        return Agent(
            config=self.agents_config['template_analyzer'],
            llm=self.llm,
            verbose=True
        )
    
    @agent
    def core_systems_designer(self) -> Agent:
        """Core systems technical designer"""
        return Agent(
            config=self.agents_config['core_systems_designer'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def interface_designer(self) -> Agent:
        """Component interface designer"""
        return Agent(
            config=self.agents_config['interface_designer'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def design_validator(self) -> Agent:
        """Technical design validator"""
        return Agent(
            config=self.agents_config['design_validator'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def design_refiner(self) -> Agent:
        """Technical design refiner"""
        return Agent(
            config=self.agents_config['design_refiner'],
            llm=self.llm,
            verbose=True
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def template_analysis_task(self) -> Task:
        """Analyze the HTML5 game template to identify integration points"""
        return Task(
            config=self.tasks_config['template_analysis_task'],
            output_file='template_analysis.md'
        )
    
    @task
    def core_systems_design_task(self) -> Task:
        """Design the core systems for integration with the HTML5 game template"""
        return Task(
            config=self.tasks_config['core_systems_design_task'],
            context=[self.template_analysis_task()],
            output_file='core_systems_design.md'
        )

    @task
    def interface_definition_task(self) -> Task:
        """Define interfaces for template integration between game components"""
        return Task(
            config=self.tasks_config['interface_definition_task'],
            context=[self.template_analysis_task(), self.core_systems_design_task()],
            output_file='component_interfaces.md'
        )
    
    @task
    def integration_mapping_task(self) -> Task:
        """Create a detailed mapping of where each game component integrates with the template"""
        return Task(
            config=self.tasks_config['integration_mapping_task'],
            context=[self.template_analysis_task(), self.core_systems_design_task(), self.interface_definition_task()],
            output_file='integration_mapping.md'
        )

    @task
    def design_validation_task(self) -> Task:
        """Validate the template integration design for completeness and feasibility"""
        return Task(
            config=self.tasks_config['design_validation_task'],
            context=[self.core_systems_design_task(), self.interface_definition_task(), self.integration_mapping_task()],
            output_file='design_validation.md'
        )

    @task
    def design_refinement_task(self) -> Task:
        """Refine the technical design based on validation feedback"""
        return Task(
            config=self.tasks_config['design_refinement_task'],
            context=[self.core_systems_design_task(), self.interface_definition_task(), 
                    self.integration_mapping_task(), self.design_validation_task()],
            output_file='refined_technical_design.md'
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Creates the Technical Design Crew for the technical design phase of game development"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Tasks must be executed sequentially due to dependencies
            verbose=True,
            memory=True  # Enable memory for context preservation
        )
    
    def kickoff(self, inputs: Dict[str, Any] = None) -> Any:
        """
        Run the Technical Design Crew with the provided inputs
        
        Args:
            inputs: Dictionary containing:
                - 'game_concept': The initial game concept (required)
                - 'technical_architecture': The technical architecture from concept phase (required)
                - 'game_design_document': The GDD from concept phase (required)
                - 'concept_expansion': The expanded concept from concept phase (required)
                - 'style_guide': The style guide from concept phase (optional)
                - 'game_template_path': Path to the HTML5 game template file (required)
            
        Returns:
            The results of the crew execution
        """
        required_inputs = ['game_concept', 'technical_architecture', 'game_design_document', 
                          'concept_expansion', 'game_template_path']
        for input_name in required_inputs:
            if not inputs or input_name not in inputs:
                raise ValueError(f"The '{input_name}' input is required to start the Technical Design Crew")
        
        # Update the input to tasks.yaml with specific elements from the Pydantic models
        if 'concept_expansion' in inputs and 'levels' in inputs['concept_expansion']:
            levels = inputs['concept_expansion']['levels']
            level_names = [level['name'] for level in levels]
            inputs['level_names'] = ', '.join(level_names)
        
        if 'concept_expansion' in inputs and 'enemies' in inputs['concept_expansion']:
            enemies = inputs['concept_expansion']['enemies']
            enemy_names = [enemy['name'] for enemy in enemies]
            inputs['enemy_names'] = ', '.join(enemy_names)
        
        if 'concept_expansion' in inputs and 'gameplay_mechanics' in inputs['concept_expansion']:
            mechanics = inputs['concept_expansion']['gameplay_mechanics']
            mechanic_names = [mechanic['name'] for mechanic in mechanics]
            inputs['mechanic_names'] = ', '.join(mechanic_names)
        
        # Include specific details from GDD if available
        if 'game_design_document' in inputs and 'game_systems' in inputs['game_design_document']:
            systems = inputs['game_design_document']['game_systems']
            system_names = [system['name'] for system in systems]
            inputs['system_names'] = ', '.join(system_names)
            
        return self.crew().kickoff(inputs=inputs)
