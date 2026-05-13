from pydantic import BaseModel
from typing import Optional


class ExtractorSchema(BaseModel):
    title: str
    category: str
    description: str
    interaction_history: Optional[str]
    current_status: Optional[str]
