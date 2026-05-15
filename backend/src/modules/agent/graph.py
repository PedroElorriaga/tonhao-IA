from src.modules.agent.nodes.extractor import Extractor
from src.modules.agent.nodes.tech_node import TechNode
from src.modules.agent.nodes.hr_node import HRNode
from src.modules.agent.nodes.general_node import GeneralNode
from src.modules.agent.nodes.billing_node import BillingNode
from src.modules.agent.rag.retriever import RetrieverNode
from src.modules.agent.state import State
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

_graph_instance = None
_checkpointer: SqliteSaver | None = None


def get_graph():
    global _graph_instance, _checkpointer
    if _graph_instance is None:
        db_path = os.path.join(os.path.dirname(
            __file__), "..", "..", "..", "checkpoint.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
        _graph_instance = Graph().build(_checkpointer)
    return _graph_instance


class Graph:
    def __init__(self):
        self.workflow = StateGraph(State)

    def router(self, state: State) -> Literal["tech_support", "billing", "hr", "other"]:
        if state["extract_ticket_data"]["category"].lower() == "technical support" \
                or state["extract_ticket_data"]["category"].lower() == "account":
            return "tech_support"
        if state["extract_ticket_data"]["category"].lower() == "billing":
            return "billing"
        if state["extract_ticket_data"]["category"].lower() == "hr":
            return "hr"
        return "other"

    def rerouter(self, state: State) -> Literal["tech_support", "billing", "hr", "other", "end"]:
        reroute_count = state["reroute_count"] or 0
        if state["reclassified_category"] and reroute_count < 2:
            return state["reclassified_category"]
        return "end"

    def build(self, checkpointer: SqliteSaver | None = None):
        reroute_map = {
            "tech_support": "tech_support_node",
            "billing": "billing_node",
            "hr": "hr_node",
            "other": "other_node",
            "end": END
        }

        retriever = RetrieverNode()

        extractor = Extractor(model="gemma-4-31b-it",
                              api_key=os.getenv("GEMINI_API_KEY"), temperature=0.3)
        tech_llm = TechNode(model="gemini-3.1-flash-lite",
                            api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        hr_llm = HRNode(model="gemma-4-31b-it",
                        api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        billing_llm = BillingNode(model="gemma-4-31b-it",
                                  api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        general_llm = GeneralNode(model="gemini-2.5-flash-lite",
                                  api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)

        self.workflow.add_node("extractor", extractor.extract)
        self.workflow.add_node("retriever", retriever.retrieve)
        self.workflow.add_node("tech_support_node", tech_llm.generate_response)
        self.workflow.add_node("billing_node", billing_llm.generate_response)
        self.workflow.add_node("hr_node", hr_llm.generate_response)
        self.workflow.add_node("other_node", general_llm.generate_response)

        self.workflow.set_entry_point("extractor")

        self.workflow.add_edge("extractor", "retriever")

        self.workflow.add_conditional_edges("retriever", self.router, {
            "tech_support": "tech_support_node",
            "billing": "billing_node",
            "hr": "hr_node",
            "other": "other_node"
        })

        self.workflow.add_conditional_edges(
            "tech_support_node", self.rerouter, reroute_map)
        self.workflow.add_conditional_edges(
            "billing_node", self.rerouter, reroute_map)
        self.workflow.add_conditional_edges(
            "hr_node", self.rerouter, reroute_map)
        self.workflow.add_conditional_edges(
            "other_node", self.rerouter, reroute_map)

        graph = self.workflow.compile(checkpointer=checkpointer)

        return graph
