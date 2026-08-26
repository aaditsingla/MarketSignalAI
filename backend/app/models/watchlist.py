from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WatchlistItemResponse(BaseModel):
    id: int
    symbol: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)