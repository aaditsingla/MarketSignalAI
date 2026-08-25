from pydantic import BaseModel


class StockQuote(BaseModel):
    symbol: str
    company_name: str
    price: float
    previous_close: float
    change: float
    change_percent: float
    market_cap: int | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None
    currency: str