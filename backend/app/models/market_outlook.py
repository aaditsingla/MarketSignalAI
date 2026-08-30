from pydantic import BaseModel


class OutlookEvent(BaseModel):
    title: str
    category: str

    directional_score: float

    unique_sources: int
    article_ids: list[int]


class MarketOutlookResult(BaseModel):
    symbol: str

    positive_catalysts: list[OutlookEvent]
    negative_risks: list[OutlookEvent]

    positive_signals: list[OutlookEvent]
    negative_signals: list[OutlookEvent]

    events_analyzed: int