from datetime import datetime

from pydantic import BaseModel


class CollectedNewsArticle(BaseModel):
    title: str
    url: str
    source: str | None = None
    published_at: datetime | None = None
    summary: str | None = None