from pydantic import BaseModel


class SignalSummaryResult(BaseModel):
    symbol: str

    direction: str
    conviction: str
    news_agreement: str

    directional_score: float
    agreement_score: float

    positive_score: float
    neutral_score: float
    negative_score: float

    events_analyzed: int