from pydantic import BaseModel
from typing import Optional

class ExtractorSchema(BaseModel):
    related_problem: str
    user_actions: Optional[list[str]] = None