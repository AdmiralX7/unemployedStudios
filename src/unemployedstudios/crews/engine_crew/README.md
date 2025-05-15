# Engine Crew

This crew handles the core game engine development phase of game development, implementing a key component of the Game Development Flow Architecture.

## Purpose

The Engine Crew is responsible for:

1. **Game Loop Development** - Creating a robust game loop with consistent framerate and state updates
2. **Rendering Pipeline** - Implementing visual rendering for game elements using HTML5 Canvas
3. **Input Handling** - Developing cross-platform input management for keyboard, mouse, touch, and gamepad
4. **Performance Optimization** - Ensuring the engine runs smoothly across various devices and browsers

## Usage

To use the Engine Crew in your flow:

```python
from unemployedstudios.crews.engine_crew import EngineCrew

# In your flow
@listen(technical_design_phase)
def engine_crew_generation(self):
    """Run the core engine development phase of game development"""
    engine_output = (
        EngineCrew()
        .crew()
        .kickoff(inputs={
            "core_systems_design": self.state.core_systems_design,
            "component_interfaces": self.state.component_interfaces,
            "refined_technical_design": self.state.refined_technical_design
        })
    )
    
    # Store the output in the flow state
    self.state.game_engine_file = engine_output.final_integration_task
```

## Output Files

The crew generates the following output file:

- `GameGenerationOutput/game_engine.js` - The core game engine implementing the game loop, rendering pipeline, and input handling

## Agents

The crew consists of four specialized agents:

1. **Game Loop Architect** - Designs and implements the core game loop
2. **Rendering Engine Developer** - Creates the visual rendering pipeline
3. **Input System Specialist** - Develops cross-platform input handling
4. **Performance Optimizer** - Ensures efficient performance across devices

## Required Inputs

The recommended inputs are:
- `core_systems_design` - Specifications for game systems from the Technical Design Phase
- `component_interfaces` - Interface definitions for game components
- `refined_technical_design` - Final technical specifications from the Technical Design Phase

## Next Steps

After the Engine Crew completes its work, the `game_engine.js` file serves as a core dependency for other systems in the Code Generation Phase of the Game Development Flow. The engine provides the foundation that other systems (Entity, Level, UI, Asset, Audio) will build upon to complete the game. 