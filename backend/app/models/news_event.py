from datetime import datetime

from pydantic import BaseModel


class NewsEventGroup(BaseModel):
    representative_article_id: int
    representative_title: str

    article_ids: list[int]

    earliest_published_at: datetime | None = None
    latest_published_at: datetime | None = None

    average_similarity: float