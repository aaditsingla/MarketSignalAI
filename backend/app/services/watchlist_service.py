from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.watchlist import WatchlistItem


class WatchlistService:
    def get_watchlist(self, database: Session) -> list[WatchlistItem]:
        statement = select(WatchlistItem).order_by(WatchlistItem.added_at.desc())

        return list(database.scalars(statement).all())

    def add_stock(self, database: Session, symbol: str) -> WatchlistItem:
        normalized_symbol = symbol.upper().strip()

        existing_item = database.scalar(
            select(WatchlistItem).where(
                WatchlistItem.symbol == normalized_symbol
            )
        )

        if existing_item is not None:
            raise ValueError(
                f"{normalized_symbol} is already in the watchlist"
            )

        watchlist_item = WatchlistItem(symbol=normalized_symbol)

        database.add(watchlist_item)
        database.commit()
        database.refresh(watchlist_item)

        return watchlist_item

    def remove_stock(self, database: Session, symbol: str) -> None:
        normalized_symbol = symbol.upper().strip()

        watchlist_item = database.scalar(
            select(WatchlistItem).where(
                WatchlistItem.symbol == normalized_symbol
            )
        )

        if watchlist_item is None:
            raise ValueError(
                f"{normalized_symbol} is not in the watchlist"
            )

        database.delete(watchlist_item)
        database.commit()