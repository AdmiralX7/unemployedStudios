# Technical Design Crew

This crew handles the technical design phase of game development, implementing the second stage of the Game Development Flow Architecture.

## Purpose

The Technical Design Crew is responsible for:

1. **Core Systems Design** - Creating detailed technical specifications for all core game systems
2. **Component Interface Definition** - Defining clear interfaces between all major game components
3. **Design Validation** - Thoroughly evaluating the technical design for completeness and feasibility
4. **Design Refinement** - Iteratively improving the design based on validation feedback

## Usage

To use the Technical Design Crew in your flow:

```python
from unemployedstudios.crews.technical_design_crew import TechnicalDesignCrew

# In your flow
@listen(concept_phase)
def technical_design_phase(self):
    """Run the technical design phase of game development"""
    tech_design_output = (
        TechnicalDesignCrew()
        .crew()
        .kickoff(inputs={
            "game_concept": self.state.game_concept,
            "technical_architecture": self.state.technical_architecture,
            "game_design_document": self.state.game_design_document  # Optional
        })
    )
    
    # Store the output in the flow state
    self.state.core_systems_design = tech_design_output.core_systems_design_task
    self.state.component_interfaces = tech_design_output.interface_definition_task
    self.state.design_validation = tech_design_output.design_validation_task
    self.state.refined_technical_design = tech_design_output.design_refinement_task
```

## Output Files

The crew generates the following output files:

- `core_systems_design.md` - Detailed specifications for all core game systems
- `component_interfaces.md` - Interface definitions for all major game components
- `design_validation.md` - Validation report assessing the technical design
- `refined_technical_design.md` - Final technical design with improvements based on validation

## Agents

The crew consists of four specialized agents:

1. **Core Systems Designer** - Technical architect who designs the core game systems
2. **Interface Designer** - API specialist who defines component interfaces
3. **Design Validator** - Technical reviewer who evaluates the design's completeness and feasibility
4. **Design Refiner** - System architect who improves the design based on validation feedback

## Required Inputs

The required inputs are:
- `game_concept` - The initial game concept
- `technical_architecture` - The high-level technical architecture from the Concept Phase

Optional input:
- `game_design_document` - The GDD from the Concept Phase

## Next Steps

After the Technical Design Crew completes its work, the outputs serve as inputs for the Code Generation Phase of the Game Development Flow. 