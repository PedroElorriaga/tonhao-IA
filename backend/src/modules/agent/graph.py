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
        db_path = os.getenv(
            "CHECKPOINT_DB_PATH",
            os.path.join(os.path.dirname(__file__), "..",
                         "..", "..", "checkpoint.db"),
        )
        conn = sqlite3.connect(db_path, check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
        _graph_instance = Graph().build(_checkpointer)
    return _graph_instance


class Graph:
    def __init__(self):
        self.workflow = StateGraph(State)
        self.retriever = RetrieverNode()
        self.extractor = Extractor(model="gemma-4-31b-it",
                                   api_key=os.getenv("GEMINI_API_KEY"), temperature=0.3)
        self.tech_node = TechNode(model="gemini-3.1-flash-lite",
                                  api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        self.hr_node = HRNode(model="gemma-4-31b-it",
                              api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        self.billing_node = BillingNode(model="gemma-4-31b-it",
                                        api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)
        self.general_node = GeneralNode(model="gemini-2.5-flash-lite",
                                        api_key=os.getenv("GEMINI_API_KEY"), temperature=0.5)

    def router(self, state: State) -> Literal["tech_support", "billing", "hr", "other"]:
        if state["extract_ticket_data"]["category"].lower() == "technical support" \
                or state["extract_ticket_data"]["category"].lower() == "account":
            return "tech_support"
        if state["extract_ticket_data"]["category"].lower() == "billing":
            return "billing"
        if state["extract_ticket_data"]["category"].lower() == "hr":
            return "hr"
        return "other"

    def build(self, checkpointer: SqliteSaver | None = None):
        self.workflow.add_node("extractor", self.extractor.extract)
        self.workflow.add_node("retriever", self.retriever.retrieve)
        self.workflow.add_node("tech_support_node",
                               self.tech_node.generate_response)
        self.workflow.add_node(
            "billing_node", self.billing_node.generate_response)
        self.workflow.add_node("hr_node", self.hr_node.generate_response)
        self.workflow.add_node(
            "other_node", self.general_node.generate_response)

        self.workflow.set_entry_point("extractor")

        self.workflow.add_edge("extractor", "retriever")

        self.workflow.add_conditional_edges("retriever", self.router, {
            "tech_support": "tech_support_node",
            "billing": "billing_node",
            "hr": "hr_node",
            "other": "other_node"
        })

        self.workflow.add_edge("tech_support_node", END)
        self.workflow.add_edge("billing_node", END)
        self.workflow.add_edge("hr_node", END)
        self.workflow.add_edge("other_node", END)

        graph = self.workflow.compile(checkpointer=checkpointer)

        return graph
