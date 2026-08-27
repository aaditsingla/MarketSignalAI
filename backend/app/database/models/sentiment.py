from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class ArticleSentiment(Base):
    __tablename__ = "article_sentiments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news_articles.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    positive_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    neutral_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    negative_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    chunks_analyzed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )