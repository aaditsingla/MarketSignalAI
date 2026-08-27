from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tickers: Mapped[list["ArticleTicker"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )


class ArticleTicker(Base):
    __tablename__ = "article_tickers"

    article_id: Mapped[int] = mapped_column(
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
        index=True,
    )

    article: Mapped[NewsArticle] = relationship(
        back_populates="tickers",
    )