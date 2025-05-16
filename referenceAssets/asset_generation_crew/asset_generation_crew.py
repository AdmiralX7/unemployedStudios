import base64
from openai import OpenAI
from pydantic import BaseModel, Field
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM
from crewai_tools import DallETool
from crewai.tools import BaseTool
import os
import re
import json
import pathlib
import requests
from typing import Any, List, Optional, Type
import dotenv

from bs4 import BeautifulSoup    

# Import our types
from unemploymentstudios.types import AssetSpecCollection, ImageAssetSpec, AudioAssetSpec

@CrewBase
class AssetGenerationCrew:
    """Asset Generation Crew for game development"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Basic configuration
    llm = LLM(model="gpt-4o")

    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------
    @agent
    def graphic_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["graphic_designer"],
            llm=self.llm
        )

    @agent
    def sound_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["sound_designer"],
            llm=self.llm
        )

    @agent
    def ui_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_designer"],
            llm=self.llm
        )

    @agent
    def asset_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["asset_manager"],
            llm=self.llm
        )

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    @task
    def analyze_asset_requirements(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_asset_requirements"]
        )

    @task
    def design_character_assets(self) -> Task:
        return Task(
            config=self.tasks_config["design_character_assets"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def design_environment_assets(self) -> Task:
        return Task(
            config=self.tasks_config["design_environment_assets"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def design_ui_elements(self) -> Task:
        return Task(
            config=self.tasks_config["design_ui_elements"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def create_sound_effects(self) -> Task:
        return Task(
            config=self.tasks_config["create_sound_effects"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def create_background_music(self) -> Task:
        return Task(
            config=self.tasks_config["create_background_music"],
            context=[self.analyze_asset_requirements()]
        )

    @task
    def finalize_assets(self) -> Task:
        return Task(
            config=self.tasks_config["finalize_assets"],
            context=[
                self.analyze_asset_requirements(),
                self.design_character_assets(),
                self.design_environment_assets(),
                self.design_ui_elements(),
                self.create_sound_effects(),
                self.create_background_music()
            ]
        )

    @task
    def specify_visual_assets(self) -> Task:
        """Create detailed specifications for visual assets."""
        return Task(
            config=self.tasks_config["specify_visual_assets"],
            context=[
                self.finalize_assets()
            ]
        )

    @task
    def specify_audio_assets(self) -> Task:
        """Create detailed specifications for audio assets."""
        return Task(
            config=self.tasks_config["specify_audio_assets"],
            context=[
                self.finalize_assets()
            ]
        )

    @task
    def compile_asset_specifications(self) -> Task:
        """Compile all asset specifications into a single collection."""
        return Task(
            config=self.tasks_config["compile_asset_specifications"],
            context=[
                self.specify_visual_assets(),
                self.specify_audio_assets()
            ]
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    @crew
    def crew(self) -> Crew:
        """Create the crew"""
        return Crew(
            agents=[
                self.asset_manager(),
                self.graphic_designer(),
                self.sound_designer(),
                self.ui_designer()
            ],
            tasks=[
                self.analyze_asset_requirements(),
                self.design_character_assets(),
                self.design_environment_assets(),
                self.design_ui_elements(),
                self.create_sound_effects(),
                self.create_background_music(),
                self.finalize_assets(),
                self.specify_visual_assets(),
                self.specify_audio_assets(),
                self.compile_asset_specifications()
            ],
            process=Process.sequential,
            verbose=True
        )
    