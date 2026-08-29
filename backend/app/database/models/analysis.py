from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class CompanyAnalysis(Base):
    __tablename__ = "company_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    stock_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    signal: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sentiment_score: Mapped[float] = mapped_column(
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

    articles_analyzed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    articles: Mapped[list["AnalysisArticle"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class AnalysisArticle(Base):
    __tablename__ = "analysis_articles"

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey(
            "company_analyses.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news_articles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    analysis: Mapped[CompanyAnalysis] = relationship(
        back_populates="articles",
    )

    article = relationship("NewsArticle")