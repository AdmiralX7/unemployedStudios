# CrewAI Crew Development Guide

This guide provides instructions for creating well-structured CrewAI crews, including Python file setup, YAML configuration, and best practices.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Quick Start with CLI](#quick-start-with-cli)
3. [Crew Python File](#crew-python-file)
4. [Agents YAML Configuration](#agents-yaml-configuration)
5. [Tasks YAML Configuration](#tasks-yaml-configuration)
6. [Advanced Configuration](#advanced-configuration)
7. [Integration with Flows](#integration-with-flows)
8. [Best Practices](#best-practices)

## Project Structure

A proper CrewAI crew should follow this directory structure:

```
your_crew_name/
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
├── your_crew_name.py
└── __init__.py
```

## Quick Start with CLI

You can use the CrewAI CLI to quickly create a template crew with all necessary files and directory structure:

```bash
crewai flow add-crew crew-name
```

This command automatically creates the necessary directories and template files for your crew. The template will create a content writer crew by default, but you should modify the files according to your specific requirements and the best practices described in this guide.

Using the CLI command makes the crew creation process easier by providing a starting point, but you'll still need to:

1. Define your specific agents in `agents.yaml`
2. Create your custom tasks in `tasks.yaml`
3. Modify the crew Python file to implement your specific logic

The rest of this guide provides detailed instructions on how to properly customize these template files.

## Crew Python File

The crew Python file defines the agents, tasks, and crew configuration. Here's a template with best practices:

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# Import any necessary Pydantic models for structured output
from your_project.types import YourOutputType

@CrewBase
class YourCrewName:
    """Short description of your crew's purpose"""
    
    # Configuration paths - relative to your module
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # LLM Configuration
    llm = LLM(model="openai/gpt-4o")  # Choose appropriate model for your task
    
    # --------------------------------------------------
    # AGENTS
    # --------------------------------------------------

    @agent
    def first_agent(self) -> Agent:
        """Define your first agent"""
        return Agent(
            config=self.agents_config["first_agent"],
            llm=self.llm
        )

    @agent
    def second_agent(self) -> Agent:
        """Define your second agent"""
        return Agent(
            config=self.agents_config["second_agent"],
            llm=self.llm
        )

    # Add more agents as needed...

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------
    
    @task
    def first_task(self) -> Task:
        """Define your first task"""
        return Task(
            config=self.tasks_config["first_task"]
            # Optionally override LLM if needed: llm=self.llm
        )

    @task
    def second_task(self) -> Task:
        """Define your second task"""
        return Task(
            config=self.tasks_config["second_task"],
            # Add context from previous tasks when needed
            context=[self.first_task()]
        )

    @task
    def final_task(self) -> Task:
        """Define your final task that produces structured output"""
        return Task(
            config=self.tasks_config["final_task"],
            context=[self.first_task(), self.second_task()],
            # Use Pydantic models for structured output
            output_pydantic=YourOutputType
        )

    # --------------------------------------------------
    # CREW
    # --------------------------------------------------
    
    @crew
    def crew(self) -> Crew:
        """Create and configure the crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # or Process.hierarchical
            verbose=True
        )
```

## Agents YAML Configuration

The `agents.yaml` file defines the capabilities and personalities of your agents:

```yaml
first_agent:
  role: >
    First Agent Role Title
  goal: >
    Clear, specific goal for this agent. Define what they are trying to accomplish
    and what success looks like for them.
  backstory: >
    Rich backstory that gives the agent a personality and expertise. Explain their
    experience, knowledge areas, and approach to problem-solving.

second_agent:
  role: >
    Second Agent Role Title
  goal: >
    Clear, specific goal that complements but differs from the first agent.
    Make sure goals align with the agent's expertise.
  backstory: >
    Backstory that establishes this agent's unique perspective and skills.
    Ensure the backstory is consistent with their role and goal.

# Add more agents as needed...

finalizing_agent:
  role: >
    Finalizing Agent
  goal: >
    Consolidate all team contributions into a single cohesive output.
    Be specific about the format requirements if using structured output.
  backstory: >
    Expertise in integration, synthesis, and quality control. This agent
    ensures all parts come together correctly and consistently.
```

## Tasks YAML Configuration

The `tasks.yaml` file defines what each agent should do:

```yaml
first_task:
  description: >
    Detailed instructions for the first task. Be specific about:
    • What information the agent should focus on
    • What aspects to prioritize
    • What constraints to consider
    
    Reference input variables using curly braces: {input_variable}
    
    Provide context needed to complete the task effectively.
  expected_output: >
    Clear description of what the output should contain, including:
    - Specific components to include
    - Format requirements
    - Level of detail expected
    - Any constraints or guidelines to follow
  agent: first_agent  # Must match an agent name from your Python file

second_task:
  description: >
    Instructions for the second task that builds upon the first.
    Reference specific outputs from previous tasks that this agent
    should use or expand upon.
  expected_output: >
    Description of expected output format and content.
  agent: second_agent

final_task:
  description: >
    Instructions for the final task that synthesizes all previous work.
    Be explicit about the required format if using a Pydantic model for output.
  expected_output: >
    Detailed specification of the final output format, especially if it needs to
    match a specific Pydantic model structure. Include field names and types.
  agent: finalizing_agent
```

## Advanced Configuration

For more complex scenarios, you can enhance your crew with these additional options:

### LLM Configuration

```python
llm = LLM(
    model="openai/gpt-4o",
    temperature=0.7,        # Higher for more creative outputs
    timeout=120,            # Seconds to wait for response
    max_tokens=4000,        # Maximum length of response
    top_p=0.9,              # Nucleus sampling parameter
    frequency_penalty=0.1,  # Reduce repetition
    presence_penalty=0.1,   # Encourage topic diversity
    response_format={"type": "json"},  # For structured outputs
    seed=42                 # For reproducible results
)
```

### Advanced Crew Options

```python
@crew
def crew(self) -> Crew:
    return Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.hierarchical,  # Use hierarchical for complex tasks
        manager_agent=self.manager_agent(),  # Add a manager for hierarchical process
        manager_llm=self.llm,
        function_calling_llm=self.llm,
        planning=True,  # Enable planning for complex workflows
        planning_llm=self.llm,
        cache=True,  # Cache results for efficiency
        memory=True,  # Enable memory for context preservation
        embedder={
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small"
            }
        },
        verbose=True
    )
```

## Integration with Flows

When integrating your crew with a CrewAI Flow:

```python
@listen(previous_step)
def your_crew_step(self):
    """Run your crew as part of a larger flow"""
    crew_output = (
        YourCrewName()
        .crew()
        .kickoff(inputs={
            "input_variable": self.state.some_value,
            "another_variable": self.state.another_value
        })
    )
    
    # Store the output in the flow state
    self.state.crew_output = crew_output.raw
```

## Best Practices

1. **Single Responsibility Principle**: Each agent should have a clear, focused role
2. **Explicit Task Dependencies**: Use the `context` parameter to make task dependencies clear
3. **Structured Outputs**: Use Pydantic models for complex outputs to ensure consistency
4. **Clear Instructions**: Task descriptions should be explicit and comprehensive
5. **Variable Substitution**: Use `{variable_name}` in YAML for dynamic content
6. **Progressive Complexity**: Order tasks from simple to complex, building upon previous work
7. **Validation Points**: Include validation steps for critical outputs
8. **Appropriate Models**: Choose LLM models based on task complexity
9. **Descriptive Naming**: Use clear, descriptive names for agents and tasks
10. **Complete Documentation**: Document crew purpose, inputs, outputs, and usage

Remember that each agent acts based on its role, goal, and backstory, so make these elements rich and specific to get the best results. 