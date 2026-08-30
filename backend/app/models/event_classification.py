from pydantic import BaseModel


class EventClassificationResult(BaseModel):
    category: str
    score: float