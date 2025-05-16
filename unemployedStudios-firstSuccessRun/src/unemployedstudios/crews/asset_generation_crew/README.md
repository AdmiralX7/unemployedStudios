# Asset Generation Crew

This crew handles the asset generation phase of game development, implementing the Asset Generation Phase of the Game Development Flow Architecture.

## Purpose

The Asset Generation Crew is responsible for:

1. **Asset Requirements Analysis** - Analyzing the game concept and style guide to determine all required assets
2. **Visual Asset Specification** - Creating detailed specifications for character and environment assets
3. **UI Asset Specification** - Creating detailed specifications for UI elements and screens
4. **Audio Asset Specification** - Creating detailed specifications for sound effects and music
5. **Asset Specification Compilation** - Compiling all specifications into a structured collection

## Usage

To use the Asset Generation Crew in your flow:

```python
from unemployedstudios.crews.asset_generation_crew import AssetGenerationCrew

# In your flow
@listen(previous_step)
def asset_generation_phase(self):
    """Run the asset generation phase of game development"""
    asset_output = (
        AssetGenerationCrew()
        .crew()
        .kickoff(inputs={
            "game_concept": self.state.game_concept,
            "style_guide": self.state.style_guide,
            "game_design_document": self.state.game_design_document
        })
    )
    
    # Store the output in the flow state
    self.state.asset_specifications = asset_output.compile_asset_specifications
```

## Output Structure

The crew generates a structured `AssetSpecCollection` output containing:

- `image_assets`: A list of `ImageAssetSpec` objects for visual assets
- `audio_assets`: A list of `AudioAssetSpec` objects for audio assets

Each asset specification contains:

- `asset_id`: Unique identifier for the asset
- `asset_type`: Type of asset (character, environment, ui, effect, music, etc.)
- `filename`: Target filename with path for the asset
- Detailed specification information (DALL-E prompts for images, search terms for audio)

## Agents

The crew consists of four specialized agents:

1. **Asset Specification Agent** - Analyzes requirements and compiles final specifications
2. **Visual Asset Agent** - Creates detailed specifications for character and environment assets
3. **UI Asset Agent** - Creates detailed specifications for UI elements
4. **Audio Asset Agent** - Creates detailed specifications for sound effects and music

## Required Input

The required inputs are:

- `game_concept`: The core game concept description
- `style_guide`: The style guide generated in the concept phase
- `game_design_document`: The game design document from the concept phase

## Next Steps

After the Asset Generation Crew completes its work, the asset specifications can be used to generate/download the actual assets using the appropriate tools (DALL-E for images, Freesound for audio). 