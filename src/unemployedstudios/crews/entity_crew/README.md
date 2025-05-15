# Entity System Crew

This crew handles the entity system development phase of game development, implementing a key component of the Game Development Flow Architecture.

## Purpose

The Entity System Crew is responsible for:

1. **Entity Framework Development** - Creating a flexible, extensible entity system for all game objects
2. **Component System Design** - Implementing a modular component architecture for entity composition
3. **Physics Implementation** - Developing movement, collision detection, and physical interactions
4. **Entity Behavior** - Creating AI and behavior patterns for game entities, especially enemies

## Usage

To use the Entity System Crew in your flow:

```python
from unemployedstudios.crews.entity_crew import EntityCrew

# In your flow
@listen(technical_design_phase)
def entity_crew_generation(self):
    """Run the entity system development phase of game development"""
    entity_output = (
        EntityCrew()
        .crew()
        .kickoff(inputs={
            "core_systems_design": self.state.core_systems_design,
            "component_interfaces": self.state.component_interfaces,
            "concept_expansion": self.state.concept_expansion  # Contains enemy information
        })
    )
    
    # Store the output in the flow state
    self.state.game_entities_file = entity_output.final_integration_task
```

## Output Files

The crew generates the following output file:

- `GameGenerationOutput/game_entities.js` - The entity system implementing the entity framework, component system, physics, and behaviors

## Agents

The crew consists of four specialized agents:

1. **Entity Framework Developer** - Designs and implements the core entity system
2. **Component System Designer** - Creates the modular component architecture
3. **Physics Implementation Expert** - Develops movement and collision systems
4. **Entity Behavior Specialist** - Implements AI and behavior patterns

## Required Inputs

The recommended inputs are:
- `core_systems_design` - Specifications for entity systems from the Technical Design Phase
- `component_interfaces` - Interface definitions for entity components
- `concept_expansion` - Information about enemies and entity types from the Concept Phase

## Next Steps

After the Entity System Crew completes its work, the `game_entities.js` file serves as a key component in the Code Generation Phase of the Game Development Flow. The entity system works with the game engine to create and manage all game objects, enemies, and interactive elements in the game. 