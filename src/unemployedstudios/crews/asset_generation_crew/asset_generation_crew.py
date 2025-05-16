from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai import LLM
from typing import List, Dict, Any, Optional
import os

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
