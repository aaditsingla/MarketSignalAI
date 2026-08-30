from datetime import datetime

from pydantic import BaseModel


class EventSentimentResult(BaseModel):
    representative_article_id: int
    representative_title: str

    article_ids: list[int]
    analyzed_article_ids: list[int]

    category: str
    category_score: float

    positive_score: float
    neutral_score: float
    negative_score: float

    directional_score: float

    articles_analyzed: int
    unique_sources: int

    source_names: list[str]

    earliest_published_at: datetime | None = None
    latest_published_at: datetime | None = None