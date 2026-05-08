from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


TicketStatus = Literal["open", "pending", "in_progress", "solved", "closed"]
TicketPriority = Literal["low", "medium", "high", "critical"]


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TicketPriority = "medium"
    category: str
    client_name: str


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = None
    client_name: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TicketStatus
    priority: TicketPriority
    category: str
    client_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    attachment_url: Optional[str]
    attachment_name: Optional[str]

    model_config = {"from_attributes": True}


class PaginatedTicketsResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
