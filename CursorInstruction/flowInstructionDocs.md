# CrewAI Flow Development Guide

This guide provides comprehensive instructions for creating effective CrewAI Flows, including setup, architecture, state management, and best practices.

## Table of Contents

1. [Introduction to Flows](#introduction-to-flows)
2. [Flow Project Structure](#flow-project-structure)
3. [Quick Start with CLI](#quick-start-with-cli)
4. [Flow State Management](#flow-state-management)
5. [Event-Driven Architecture](#event-driven-architecture)
6. [Direct LLM Integration](#direct-llm-integration)
7. [Crew Integration](#crew-integration)
8. [Advanced Flow Patterns](#advanced-flow-patterns)
9. [Best Practices](#best-practices)

## Introduction to Flows

CrewAI Flows represent the next level in AI orchestration - combining the collaborative power of AI agent crews with the precision and flexibility of procedural programming. While crews excel at agent collaboration, flows give you fine-grained control over exactly how and when different components of your AI system interact.

Flows enable you to:

1. **Combine different AI interaction patterns** - Use crews for complex collaborative tasks, direct LLM calls for simpler operations, and regular code for procedural logic
2. **Build event-driven systems** - Define how components respond to specific events and data changes
3. **Maintain state across components** - Share and transform data between different parts of your application
4. **Integrate with external systems** - Seamlessly connect your AI workflow with databases, APIs, and user interfaces
5. **Create complex execution paths** - Design conditional branches, parallel processing, and dynamic workflows

## Flow Project Structure

A proper CrewAI Flow project should follow this directory structure:

```
your_flow_project/
├── .gitignore
├── pyproject.toml
├── README.md
├── .env
├── main.py
├── crews/
│   ├── first_crew/
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── first_crew.py
│   └── second_crew/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── second_crew.py
└── tools/
    └── custom_tool.py
```

This structure provides a clear separation between different components:
- The main flow logic in the `main.py` file
- Specialized crews in the `crews` directory
- Custom tools in the `tools` directory

## Quick Start with CLI

You can use the CrewAI CLI to quickly create a template flow project:

```bash
# Create a new flow project
crewai create flow your_flow_name
cd your_flow_name

# Add a specialized crew to your flow
crewai flow add-crew crew_name
```

These commands generate the basic structure and template files needed to get started.

## Flow State Management

Flow state management is handled through Pydantic models, providing type safety and validation:

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class YourFlowState(BaseModel):
    # Input fields
    input_variable: str = ""
    another_input: int = 0
    
    # Intermediate processing fields
    processed_data: Dict[str, str] = Field(default_factory=dict)
    
    # Output fields
    results: List[str] = Field(default_factory=list)
    final_output: Optional[str] = None
    completion_status: bool = False
```

The state object is available throughout your flow, allowing you to share data between steps:

```python
@listen(previous_step)
def process_data(self):
    # Access data from previous steps
    input_data = self.state.input_variable
    
    # Process the data
    result = process_function(input_data)
    
    # Update the state for future steps
    self.state.processed_data["key"] = result
```

## Event-Driven Architecture

Flows use decorators to establish relationships between components, creating a clear, declarative structure:

```python
from crewai.flow import Flow, start, listen

class YourFlow(Flow[YourFlowState]):
    @start()
    def first_step(self):
        """Entry point for the flow"""
        # Initialize or collect input data
        self.state.input_variable = "Initial value"
    
    @listen(first_step)
    def second_step(self):
        """Runs after first_step completes"""
        # Process data from first step
        processed = do_something(self.state.input_variable)
        self.state.processed_data = processed
    
    @listen(second_step)
    def third_step(self):
        """Runs after second_step completes"""
        # Further processing
        self.state.final_output = final_process(self.state.processed_data)
```

## Direct LLM Integration

For simpler, structured tasks, flows allow direct LLM calls without creating a full crew:

```python
from crewai import LLM
from pydantic import BaseModel

class StructuredOutput(BaseModel):
    title: str
    summary: str
    key_points: List[str]

@listen(previous_step)
def generate_structured_content(self):
    """Generate structured content with a direct LLM call"""
    
    # Create an LLM instance
    llm = LLM(
        model="openai/gpt-4o", 
        response_format=StructuredOutput
    )
    
    # Define the prompt
    messages = [
        {
            "role": "system", 
            "content": "Generate structured content based on the topic"
        },
        {
            "role": "user", 
            "content": f"Create a summary about: {self.state.topic}"
        }
    ]
    
    # Make the call and get structured output
    response = llm.call(messages=messages)
    
    # Store the structured response in the state
    self.state.structured_content = response
```

## Crew Integration

Flows can seamlessly integrate with crews for complex collaborative tasks:

```python
@listen(previous_step)
def run_specialized_crew(self):
    """Use a specialized crew for a complex task"""
    
    # Initialize and run the crew with inputs from the flow state
    crew_result = (
        SpecializedCrew()
        .crew()
        .kickoff(inputs={
            "input_variable": self.state.some_value,
            "another_variable": self.state.another_value
        })
    )
    
    # Store the crew's output in the flow state
    self.state.crew_output = crew_result.raw
```

## Advanced Flow Patterns

### Conditional Branching

Use `@router()` to create conditional branches in your flows:

```python
from crewai.flow import router

@router()
def route_based_on_analysis(self):
    """Route to different steps based on analysis"""
    if self.state.complexity_score > 7:
        return self.handle_complex_case
    else:
        return self.handle_simple_case

@listen(route_based_on_analysis)
def handle_complex_case(self):
    """Handle complex cases"""
    # Complex case handling logic

@listen(route_based_on_analysis)
def handle_simple_case(self):
    """Handle simple cases"""
    # Simple case handling logic
```

### Parallel Execution

Use `and_` and `or_` functions for parallel execution:

```python
from crewai.flow import and_, or_

@listen(and_(first_step, second_step))
def after_both_complete(self):
    """Runs only after both first_step AND second_step complete"""
    # Logic that depends on both previous steps

@listen(or_(first_option, second_option))
def after_either_completes(self):
    """Runs after EITHER first_option OR second_option completes"""
    # Logic that can proceed after either path
```

## Best Practices

1. **Clear State Design**: Design your state model carefully to ensure all steps have access to the data they need
2. **Explicit Dependencies**: Use `@listen` decorators to make the flow of data and control explicit
3. **Appropriate Task Allocation**: 
   - Use direct LLM calls for simple, structured tasks
   - Use crews for complex, collaborative tasks
   - Use regular Python code for procedural logic
4. **Error Handling**: Add error handling and validation between critical steps
5. **State Validation**: Use Pydantic validators to ensure data consistency
6. **Modular Design**: Break complex flows into smaller, reusable components
7. **Clear Naming**: Use descriptive names for steps that indicate their purpose
8. **Progress Tracking**: Add logging or progress tracking for long-running flows
9. **Testing**: Create unit tests for individual flow components
10. **Documentation**: Document the purpose, inputs, and outputs of each step

## Running Your Flow

To run your flow, use the following code in your main script:

```python
# main.py
from your_flow_module import YourFlow

def main():
    flow = YourFlow()
    flow.start()
    # Optionally, access final state
    final_state = flow.state
    print(f"Final output: {final_state.final_output}")

if __name__ == "__main__":
    main()
```

Or run it using the CLI:

```bash
crewai run
```

## Visualizing Your Flow

To visualize your flow and better understand its structure:

```bash
crewai plot
```

This will generate a visual representation of your flow, showing the relationships between different steps and components.

## Example Applications

Flows are ideal for complex AI systems such as:

- Interactive AI assistants that combine multiple specialized subsystems
- Complex data processing pipelines with AI-enhanced transformations
- Autonomous agents that integrate with external services and APIs
- Multi-stage decision-making systems with human-in-the-loop processes
- Content generation systems with planning, creation, and review stages 