from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    extract_ticket_data: Optional[dict]
    reclassified_category: Optional[str]
    reroute_count: Optional[int]
    retrieved_context: Optional[str]
