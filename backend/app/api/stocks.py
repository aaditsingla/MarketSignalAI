from fastapi import APIRouter, HTTPException, Query

from app.models.stock import StockQuote
from app.models.stock_history import StockHistory
from app.services.market_service import MarketService

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
)

market_service = MarketService()


@router.get("/{symbol}", response_model=StockQuote)
def get_stock(symbol: str) -> StockQuote:
    try:
        return market_service.get_stock_quote(symbol)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{symbol}/history", response_model=StockHistory)
def get_stock_history(
    symbol: str,
    period: str = Query(default="1mo"),
) -> StockHistory:
    try:
        return market_service.get_stock_history(symbol, period)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error