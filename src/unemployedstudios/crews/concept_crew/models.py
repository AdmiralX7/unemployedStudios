from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Optional, Union

class GameplayMechanic(BaseModel):
    """A specific gameplay mechanic or feature"""
    name: str = Field(..., description="Name of the gameplay mechanic")
    description: str = Field(..., description="Detailed description of how the mechanic works")
    core_loop: str = Field(..., description="How this mechanic factors into the core gameplay loop")
    implementation_complexity: str = Field(..., description="Estimated complexity to implement (Low/Medium/High)")

class Character(BaseModel):
    """A character in the game (player character or NPC)"""
    name: str = Field(..., description="Name of the character")
    role: str = Field(..., description="Role in the game (e.g. Player, NPC, Quest Giver)")
    description: str = Field(..., description="Physical and personality description")
    abilities: List[str] = Field(default_factory=list, description="List of character abilities or skills")
    backstory: Optional[str] = Field(None, description="Character's backstory if relevant")

class Enemy(BaseModel):
    """An enemy or obstacle in the game"""
    name: str = Field(..., description="Name of the enemy type")
    description: str = Field(..., description="Description of the enemy's appearance and behavior")
    difficulty: str = Field(..., description="Difficulty level (Easy/Medium/Hard)")
    attack_pattern: str = Field(..., description="How the enemy attacks or challenges the player")
    weakness: str = Field(..., description="The enemy's weakness or how to defeat it")

class Level(BaseModel):
    """A game level or environment"""
    name: str = Field(..., description="Name of the level")
    theme: str = Field(..., description="Visual and thematic description")
    objectives: List[str] = Field(..., description="Main objectives for the player in this level")
    challenges: List[str] = Field(..., description="Key challenges or obstacles")
    enemies: List[Enemy] = Field(default_factory=list, description="Enemies featured in this level")
    special_mechanics: List[str] = Field(default_factory=list, description="Special mechanics unique to this level")
    progression: str = Field(..., description="How this level fits into overall game progression")

class MonetizationStrategy(BaseModel):
    """A monetization approach for the game"""
    strategy_type: str = Field(..., description="Type of monetization (e.g., Free-to-play, Premium, etc.)")
    description: str = Field(..., description="Description of the monetization approach")
    revenue_sources: List[str] = Field(..., description="Specific revenue sources in this strategy")
    player_experience_impact: str = Field(..., description="How this affects player experience")
    implementation_requirements: List[str] = Field(..., description="Technical requirements to implement")

class ConceptExpansion(BaseModel):
    """Comprehensive expansion of the game concept"""
    title: str = Field(..., description="Game title")
    high_concept: str = Field(..., description="One-paragraph high concept statement")
    core_gameplay_loop: str = Field(..., description="Description of the core gameplay loop")
    unique_selling_points: List[str] = Field(..., description="Key unique selling points")
    target_audience: List[str] = Field(..., description="Primary target audience segments")
    gameplay_mechanics: List[GameplayMechanic] = Field(..., description="Key gameplay mechanics")
    player_character: Character = Field(..., description="The player character")
    supporting_characters: List[Character] = Field(default_factory=list, description="Supporting characters and NPCs")
    enemies: List[Enemy] = Field(..., description="Enemies and obstacles")
    levels: List[Level] = Field(..., description="Game levels or environments")
    progression_system: str = Field(..., description="How player progression works")
    narrative_elements: str = Field(..., description="Key narrative themes and story elements")
    monetization_strategies: List[MonetizationStrategy] = Field(..., description="Possible monetization approaches")
    technical_considerations: List[str] = Field(..., description="Key technical considerations for HTML5 implementation")
    market_positioning: str = Field(..., description="How the game is positioned in the market")

class UIElement(BaseModel):
    """A user interface element"""
    name: str = Field(..., description="Name of the UI element")
    purpose: str = Field(..., description="Purpose and function of this element")
    description: str = Field(..., description="Visual and interaction description")
    states: List[str] = Field(..., description="Possible states this element can have")

class GameSystem(BaseModel):
    """A core game system or subsystem"""
    name: str = Field(..., description="Name of the system")
    purpose: str = Field(..., description="Main purpose of this system")
    components: List[str] = Field(..., description="Key components of this system")
    interactions: List[str] = Field(..., description="How this system interacts with other systems")

class Milestone(BaseModel):
    """A development milestone"""
    name: str = Field(..., description="Name of the milestone")
    description: str = Field(..., description="Description of what this milestone entails")
    deliverables: List[str] = Field(..., description="Deliverables for this milestone")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies for this milestone")

class GameDesignDocument(BaseModel):
    """Structured Game Design Document"""
    title: str = Field(..., description="Game title")
    version: str = Field(..., description="GDD version")
    overview: str = Field(..., description="Game overview")
    vision_statement: str = Field(..., description="Vision statement for the game")
    core_gameplay: str = Field(..., description="Description of core gameplay")
    game_flow: str = Field(..., description="How the game progresses from start to finish")
    player_character: Character = Field(..., description="The player character")
    game_systems: List[GameSystem] = Field(..., description="Core game systems/mechanics")
    levels: List[Dict[str, str]] = Field(..., description="Level descriptions and objectives")
    ui_design: List[UIElement] = Field(..., description="UI elements and their function")
    controls: Dict[str, Union[str, List[str]]] = Field(..., description="Control mappings and responsiveness")
    audio_design: Union[Dict[str, str], str] = Field(..., description="Music and sound effect specifications")
    asset_requirements: Union[Dict[str, List[str]], str] = Field(..., description="Required assets by category")
    technical_requirements: List[str] = Field(..., description="Technical requirements and constraints")
    development_roadmap: List[Milestone] = Field(..., description="Development milestones")
    
    @validator('controls', pre=True)
    def validate_controls(cls, value):
        """Convert controls to appropriate format"""
        if isinstance(value, list):
            # If agent returns a list instead of a dictionary, convert to a dictionary
            # with a 'controls_list' key
            return {"controls_list": value}
        elif isinstance(value, str):
            # If agent returns a string, convert to a simple dictionary
            return {"description": value}
        elif isinstance(value, dict) and 'types' in value and isinstance(value['types'], list):
            # Convert list to string for types field
            value['types'] = ', '.join(value['types'])
        return value
    
    @validator('audio_design', pre=True)
    def validate_audio_design(cls, value):
        """Convert string audio_design to dictionary if needed"""
        if isinstance(value, str):
            # Convert string to simple dictionary
            return {"description": value}
        return value
    
    @validator('asset_requirements', pre=True)
    def validate_asset_requirements(cls, value):
        """Convert string asset_requirements to dictionary if needed"""
        if isinstance(value, str):
            # Convert string to simple dictionary with default list
            return {"general": [value]}
        return value

class SystemComponent(BaseModel):
    """A component in the technical architecture"""
    name: str = Field(..., description="Name of the component")
    purpose: str = Field(..., description="Purpose of this component")
    responsibilities: List[str] = Field(..., description="Key responsibilities")
    dependencies: List[str] = Field(default_factory=list, description="Components this depends on")
    public_interfaces: List[str] = Field(..., description="Public interfaces/methods")

class TechnicalArchitecture(BaseModel):
    """Structured Technical Architecture Document"""
    engine_components: Dict[str, str] = Field(..., description="Core engine components and their purposes")
    system_relationships: str = Field(..., description="How systems interact")
    rendering_system: SystemComponent = Field(..., description="The rendering system design")
    input_system: SystemComponent = Field(..., description="The input handling system")
    physics_system: SystemComponent = Field(..., description="The physics/collision system")
    entity_system: SystemComponent = Field(..., description="The entity management system")
    level_system: SystemComponent = Field(..., description="The level management system")
    ui_system: SystemComponent = Field(..., description="The UI system")
    audio_system: SystemComponent = Field(..., description="The audio system")
    data_flow: str = Field(..., description="How data flows between systems")
    optimization_strategies: List[str] = Field(..., description="Optimization approaches")
    browser_compatibility: List[str] = Field(..., description="Browser compatibility considerations")
    technology_stack: Dict[str, str] = Field(..., description="Technologies used in each component")
    implementation_notes: Dict[str, str] = Field(..., description="Special implementation notes")

class ColorPalette(BaseModel):
    """Color palette for the game"""
    primary_colors: Dict[str, str] = Field(..., description="Primary colors with names and hex codes")
    secondary_colors: Dict[str, str] = Field(..., description="Secondary colors with names and hex codes")
    accent_colors: Dict[str, str] = Field(..., description="Accent colors with names and hex codes")
    ui_colors: Dict[str, str] = Field(..., description="UI-specific colors with names and hex codes")

class AssetStyle(BaseModel):
    """Style guidelines for a specific asset type"""
    asset_type: str = Field(..., description="Type of asset (character, environment, UI, etc.)")
    visual_style: str = Field(..., description="Visual style description")
    guidelines: List[str] = Field(..., description="Specific guidelines for this asset type")
    examples: List[str] = Field(..., description="Textual description of examples")

class AnimationGuideline(BaseModel):
    """Guidelines for a specific animation type"""
    animation_type: str = Field(..., description="Type of animation")
    description: str = Field(..., description="How this animation should look and feel")
    timing: str = Field(..., description="Timing and pacing guidelines")
    principles: List[str] = Field(..., description="Animation principles to follow")

class StyleGuide(BaseModel):
    """Structured Style Guide"""
    visual_style: str = Field(..., description="Overall visual style description")
    design_principles: List[str] = Field(..., description="Core design principles to follow")
    color_palette: ColorPalette = Field(..., description="Color palette specifications")
    typography: Union[Dict[str, str], str] = Field(..., description="Typography specifications (either a dictionary or a string)")
    asset_styles: List[AssetStyle] = Field(..., description="Style guidelines for different asset types")
    ui_style: str = Field(..., description="UI style guidelines")
    animation_guidelines: List[AnimationGuideline] = Field(..., description="Animation style guidelines")
    audio_style: Dict[str, str] = Field(..., description="Audio style guidelines")
    technical_constraints: List[str] = Field(..., description="Technical constraints for assets")
    style_references: List[str] = Field(..., description="Reference materials and inspirations")
    
    @root_validator(pre=True)
    def ensure_required_fields(cls, values):
        """Ensure all required fields are present"""
        # Provide defaults for commonly missing fields
        if 'audio_style' not in values:
            # Check if it's nested deeper in the data
            if isinstance(values.get('audio_style', None), dict):
                values['audio_style'] = values['audio_style']
            else:
                values['audio_style'] = {
                    "background_music": "Energetic pixel art style music with chiptunes",
                    "sound_effects": "Retro 8-bit sound effects for game actions",
                    "voice_overs": "None or minimal"
                }
        
        # Similar handling for other required fields if needed
        return values
    
    @validator('typography', pre=True)
    def validate_typography(cls, value):
        """Convert string typography to dictionary if needed"""
        if isinstance(value, str):
            # Basic conversion of a simple typography string to a dictionary
            # This is a simplistic approach and might need refinement based on actual string formats
            result = {}
            # Try to parse common typography string formats
            if ":" in value:
                # Try to parse key-value pairs separated by colon and/or semicolon
                pairs = value.replace(';', ',').split(',')
                for pair in pairs:
                    if ":" in pair:
                        key, val = pair.split(':', 1)
                        result[key.strip().lower().replace(' ', '_')] = val.strip()
            
            # If we couldn't parse anything, use the whole string as a default value
            if not result:
                result = {"default": value}
                
            return result
        return value
        
    @validator('audio_style', pre=True)
    def validate_audio_style(cls, value):
        """Handle various formats of audio_style data"""
        # If audio_style was provided in another structure of the JSON
        if isinstance(value, str):
            return {"description": value}
        
        # If the field is missing, return a default
        if value is None:
            return {
                "background_music": "Energetic pixel art style music with chiptunes",
                "sound_effects": "Retro 8-bit sound effects for game actions",
                "voice_overs": "None or minimal"
            }
        
        return value 