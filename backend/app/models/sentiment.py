from pydantic import BaseModel


class SentimentResult(BaseModel):
    label: str
    confidence: float
    positive_score: float
    neutral_score: float
    negative_score: float
    chunks_analyzed: int