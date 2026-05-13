from src.modules.agent.nodes.extractor import Extractor
from src.modules.agent.nodes.tech_node import TechNode
from src.modules.agent.nodes.hr_node import HRNode
from src.modules.agent.nodes.general_node import GeneralNode
from src.modules.agent.state import State
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


class AgentGraph:
    def __init__(self):
        self.builder = StateGraph(State)

    def router(self, state: State) -> Literal["tech_support", "billing", "hr", "other"]:
        # 3.1 flash lite
        if state["extract_ticket_data"]["category"].lower() == "technical support":
            return "tech_support"
        # gemma
        if state["extract_ticket_data"]["category"].lower() == "billing":
            return "billing"
        # 3.1 flash lite
        if state["extract_ticket_data"]["category"].lower() == "account":
            return "tech_support"
        # gemma
        if state["extract_ticket_data"]["category"].lower() == "hr":
            return "hr"
        # 2.5 flash lite
        return "other"

    def build(self):
        extractor = Extractor(model="gemma-4-31b-it",
                              api_key=os.getenv("GEMINI_API_KEY"), temperature=0.3)
        tech_llm = TechNode(model="gemini-3.1-flash-lite",
                            api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        hr_llm = HRNode(model="gemma-4-31b-it",
                        api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        general_llm = GeneralNode(model="gemini-2.5-flash-lite",
                                  api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)

        self.builder.add_node("extractor", extractor.extract)
        self.builder.add_node("tech_support_node", tech_llm.generate_response)
        self.builder.add_node("billing_node", hr_llm.generate_response)
        self.builder.add_node("hr_node", hr_llm.generate_response)
        self.builder.add_node("other_node", general_llm.generate_response)

        self.builder.add_edge(START, "extractor")
        self.builder.add_conditional_edges("extractor", self.router, {
            "tech_support": "tech_support_node",
            "billing": "billing_node",
            "account": "tech_support_node",
            "hr": "hr_node",
            "other": "other_node"
        })
        self.builder.add_edge("tech_support_node", END)
        self.builder.add_edge("billing_node", END)
        self.builder.add_edge("hr_node", END)
        self.builder.add_edge("other_node", END)

        graph = self.builder.compile()

        return graph
