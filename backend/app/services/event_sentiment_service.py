from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models.news import ArticleTicker, NewsArticle
from app.database.models.sentiment import ArticleSentiment
from app.models.event_sentiment import EventSentimentResult
from app.services.news_event_service import NewsEventService


class EventSentimentService:
    LOOKBACK_HOURS = 168.0

    def __init__(self) -> None:
        self.event_service = NewsEventService()

    def analyze_events(
        self,
        database: Session,
        symbol: str,
    ) -> list[EventSentimentResult]:
        normalized_symbol = symbol.upper().strip()

        now = datetime.now(timezone.utc)

        cutoff_time = now - timedelta(
            hours=self.LOOKBACK_HOURS
        )

        article_timestamp = func.coalesce(
            NewsArticle.published_at,
            NewsArticle.fetched_at,
        )

        article_statement = (
            select(NewsArticle)
            .join(
                ArticleTicker,
                ArticleTicker.article_id == NewsArticle.id,
            )
            .where(
                ArticleTicker.symbol == normalized_symbol,
                article_timestamp >= cutoff_time,
            )
        )

        articles = list(
            database.scalars(article_statement).all()
        )

        groups = self.event_service.group_articles(
            articles
        )

        article_lookup = {
            article.id: article
            for article in articles
        }

        article_ids = list(article_lookup.keys())

        if not article_ids:
            return []

        sentiment_statement = (
            select(ArticleSentiment)
            .where(
                ArticleSentiment.article_id.in_(
                    article_ids
                )
            )
        )

        sentiments = list(
            database.scalars(sentiment_statement).all()
        )

        sentiment_lookup = {
            sentiment.article_id: sentiment
            for sentiment in sentiments
        }

        results: list[EventSentimentResult] = []

        for group in groups:
            event_sentiments = []
            analyzed_article_ids: list[int] = []

            sources: set[str] = set()

            for article_id in group.article_ids:
                article = article_lookup[article_id]

                if article.source:
                    sources.add(article.source)

                sentiment = sentiment_lookup.get(
                    article_id
                )

                if sentiment is None:
                    continue

                event_sentiments.append(sentiment)
                analyzed_article_ids.append(article_id)

            if not event_sentiments:
                continue

            sentiment_count = len(event_sentiments)

            positive_score = (
                sum(
                    sentiment.positive_score
                    for sentiment in event_sentiments
                )
                / sentiment_count
            )

            neutral_score = (
                sum(
                    sentiment.neutral_score
                    for sentiment in event_sentiments
                )
                / sentiment_count
            )

            negative_score = (
                sum(
                    sentiment.negative_score
                    for sentiment in event_sentiments
                )
                / sentiment_count
            )

            directional_score = (
                positive_score - negative_score
            )

            results.append(
                EventSentimentResult(
                    representative_article_id=(
                        group.representative_article_id
                    ),
                    representative_title=(
                        group.representative_title
                    ),
                    article_ids=group.article_ids,
                    analyzed_article_ids=(
                        analyzed_article_ids
                    ),
                    positive_score=positive_score,
                    neutral_score=neutral_score,
                    negative_score=negative_score,
                    directional_score=directional_score,
                    articles_analyzed=sentiment_count,
                    unique_sources=len(sources),
                    source_names=sorted(sources),
                    earliest_published_at=(
                        group.earliest_published_at
                    ),
                    latest_published_at=(
                        group.latest_published_at
                    ),
                )
            )

        return results