from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.watchlist import WatchlistItemResponse
from app.services.watchlist_service import WatchlistService

router = APIRouter(
    prefix="/watchlist",
    tags=["watchlist"],
)

watchlist_service = WatchlistService()


@router.get(
    "",
    response_model=list[WatchlistItemResponse],
)
def get_watchlist(
    database: Session = Depends(get_db),
) -> list[WatchlistItemResponse]:
    return watchlist_service.get_watchlist(database)


@router.post(
    "/{symbol}",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_stock(
    symbol: str,
    database: Session = Depends(get_db),
) -> WatchlistItemResponse:
    try:
        return watchlist_service.add_stock(database, symbol)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    "/{symbol}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_stock(
    symbol: str,
    database: Session = Depends(get_db),
) -> None:
    try:
        watchlist_service.remove_stock(database, symbol)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error