from datetime import datetime

from pydantic import BaseModel


class HistoricalPricePoint(BaseModel):
    timestamp: datetime
    close: float


class StockHistory(BaseModel):
    symbol: str
    period: str
    prices: list[HistoricalPricePoint]