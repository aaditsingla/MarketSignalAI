from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.news import ArticleTicker, NewsArticle
from app.database.models.sentiment import ArticleSentiment
from app.services.news_text_service import NewsTextService
from app.services.sentiment_service import SentimentService


class ArticleSentimentService:
    def __init__(self) -> None:
        self.text_service = NewsTextService()
        self._sentiment_service: SentimentService | None = None

    @property
    def sentiment_service(self) -> SentimentService:
        if self._sentiment_service is None:
            self._sentiment_service = SentimentService()

        return self._sentiment_service

    def analyze_articles_for_symbol(
        self,
        database: Session,
        symbol: str,
    ) -> dict[str, int]:
        normalized_symbol = symbol.upper().strip()

        statement = (
            select(NewsArticle)
            .join(
                ArticleTicker,
                ArticleTicker.article_id == NewsArticle.id,
            )
            .where(
                ArticleTicker.symbol == normalized_symbol,
                NewsArticle.content.is_not(None),
            )
            .order_by(NewsArticle.published_at.desc())
        )

        articles = list(
            database.scalars(statement).all()
        )

        analyzed_count = 0
        reused_count = 0
        failed_count = 0

        for article in articles:
            existing_sentiment = database.scalar(
                select(ArticleSentiment).where(
                    ArticleSentiment.article_id == article.id
                )
            )

            if existing_sentiment is not None:
                reused_count += 1
                continue

            if not article.content:
                failed_count += 1
                continue

            cleaned_content = self.text_service.clean_article_text(
                article.content
            )

            if not cleaned_content:
                failed_count += 1
                continue

            try:
                result = self.sentiment_service.analyze(
                    cleaned_content
                )
            except ValueError:
                failed_count += 1
                continue

            sentiment = ArticleSentiment(
                article_id=article.id,
                label=result.label,
                confidence=result.confidence,
                positive_score=result.positive_score,
                neutral_score=result.neutral_score,
                negative_score=result.negative_score,
                chunks_analyzed=result.chunks_analyzed,
            )

            database.add(sentiment)
            analyzed_count += 1

        database.commit()

        return {
            "articles_with_content": len(articles),
            "newly_analyzed": analyzed_count,
            "reused_existing": reused_count,
            "failed": failed_count,
        }