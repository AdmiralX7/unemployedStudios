# Concept Crew

This crew handles the initial concept phase of game development, implementing the first stage of the Game Development Flow Architecture.

## Purpose

The Concept Crew is responsible for:

1. **Concept Expansion** - Taking an initial game concept and expanding it into a comprehensive, creative, and marketable game idea
2. **Game Design Document Creation** - Creating a detailed GDD that serves as the blueprint for development
3. **Architecture Planning** - Designing the technical architecture for the HTML5 game
4. **Style Guide Definition** - Establishing consistent visual, audio, and interactive design standards

## Usage

To use the Concept Crew in your flow:

```python
from unemployedstudios.crews.concept_crew import ConceptCrew

# In your flow
@listen(previous_step)
def concept_phase(self):
    """Run the concept phase of game development"""
    concept_output = (
        ConceptCrew()
        .crew()
        .kickoff(inputs={
            "game_concept": "Brief description of your initial game concept"
        })
    )
    
    # Store the output in the flow state
    self.state.concept_expansion = concept_output.concept_expansion_task
    self.state.gdd = concept_output.gdd_creation_task
    self.state.architecture = concept_output.architecture_planning_task
    self.state.style_guide = concept_output.style_guide_task
```

## Output Files

The crew generates the following output files:

- `concept_expansion.md` - Detailed expansion of the initial game concept
- `game_design_document.md` - Comprehensive Game Design Document
- `technical_architecture.md` - Technical architecture specification
- `style_guide.md` - Style guide for visual, audio, and interactive elements

## Agents

The crew consists of four specialized agents:

1. **Concept Expander** - Game design specialist who expands initial concepts
2. **GDD Writer** - Documentation expert who creates comprehensive design documents
3. **Architecture Planner** - Technical architect who designs game systems
4. **Style Guide Creator** - Art director who establishes visual and audio standards

## Required Input

The only required input is `game_concept` - a brief description of the initial game concept.

## Next Steps

After the Concept Crew completes its work, the outputs serve as inputs for the Technical Design Phase of the Game Development Flow. 