import os
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from src.modules.agent.state import State
from src.modules.agent.nodes.extractor import Extractor

class AgentGraph:
    def __init__(self):
        self.builder = StateGraph(State)

    def build(self):
        extractor = Extractor(model="gemini-3.1-flash-lite-preview", api_key=os.getenv("GEMINI_API_KEY"), temperature=0.3)

        self.builder.add_node("extractor", extractor.extract)

        self.builder.add_edge(START, "extractor")
        self.builder.add_edge("extractor", END)

        graph = self.builder.compile()

        return graph