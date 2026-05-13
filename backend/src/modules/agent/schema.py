from pydantic import BaseModel
from typing import Optional


class ExtractorSchema(BaseModel):
    title: str
    category: str
    description: str
    interaction_history: Optional[str]
    current_status: Optional[str]


class NodeResponse(BaseModel):
    response: str
    reclassified_category: Optional[str] = None
