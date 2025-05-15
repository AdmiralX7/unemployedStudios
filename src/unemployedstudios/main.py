#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

class AppState(BaseModel):
    # Define your application state here
    pass

class AppFlow(Flow[AppState]):
    
    @start()
    def initialize(self):
        print("Starting flow")
        # Initialize your flow here
        return "Initialized"

def kickoff():
    app_flow = AppFlow()
    app_flow.kickoff()

def plot():
    app_flow = AppFlow()
    app_flow.plot()

if __name__ == "__main__":
    kickoff()
