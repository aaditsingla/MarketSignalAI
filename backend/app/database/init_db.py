from app.database.connection import Base, engine
from app.database.models.news import ArticleTicker, NewsArticle
from app.database.models.sentiment import ArticleSentiment
from app.database.models.watchlist import WatchlistItem


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)