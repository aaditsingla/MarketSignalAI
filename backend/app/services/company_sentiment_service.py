from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.company_sentiment import (
    ArticleWeightResult,
    CompanySentimentResult,
)
from app.services.event_sentiment_service import (
    EventSentimentService,
)


class CompanySentimentService:
    RECENCY_HALF_LIFE_HOURS = 72.0

    BULLISH_THRESHOLD = 0.15
    BEARISH_THRESHOLD = -0.15

    def __init__(self) -> None:
        self.event_sentiment_service = (
            EventSentimentService()
        )

    def analyze_company(
        self,
        database: Session,
        symbol: str,
    ) -> CompanySentimentResult:
        normalized_symbol = symbol.upper().strip()

        events = (
            self.event_sentiment_service.analyze_events(
                database,
                normalized_symbol,
            )
        )

        if not events:
            raise ValueError(
                f"No analyzed events available for "
                f"{normalized_symbol}"
            )

        now = datetime.now(timezone.utc)

        event_data = []
        total_weight = 0.0

        for event in events:
            event_time = (
                event.latest_published_at
                or now
            )

            if event_time.tzinfo is None:
                event_time = event_time.replace(
                    tzinfo=timezone.utc
                )

            age_hours = max(
                (
                    now - event_time
                ).total_seconds() / 3600,
                0.0,
            )

            recency_weight = 0.5 ** (
                age_hours
                / self.RECENCY_HALF_LIFE_HOURS
            )

            event_data.append(
                (
                    event,
                    recency_weight,
                )
            )

            total_weight += recency_weight

        weighted_positive = 0.0
        weighted_neutral = 0.0
        weighted_negative = 0.0

        article_weights: list[
            ArticleWeightResult
        ] = []

        for event, raw_weight in event_data:
            event_weight = (
                raw_weight / total_weight
            )

            weighted_positive += (
                event.positive_score
                * event_weight
            )

            weighted_neutral += (
                event.neutral_score
                * event_weight
            )

            weighted_negative += (
                event.negative_score
                * event_weight
            )

            analyzed_count = len(
                event.analyzed_article_ids
            )

            if analyzed_count == 0:
                continue

            article_weight = (
                event_weight
                / analyzed_count
            )

            for article_id in (
                event.analyzed_article_ids
            ):
                article_weights.append(
                    ArticleWeightResult(
                        article_id=article_id,
                        weight=article_weight,
                    )
                )

        sentiment_score = (
            weighted_positive
            - weighted_negative
        )

        signal = self._get_signal(
            sentiment_score=sentiment_score,
            positive_score=weighted_positive,
            neutral_score=weighted_neutral,
            negative_score=weighted_negative,
        )

        confidence = self._get_confidence(
            signal=signal,
            positive_score=weighted_positive,
            neutral_score=weighted_neutral,
            negative_score=weighted_negative,
        )

        return CompanySentimentResult(
            symbol=normalized_symbol,
            signal=signal,
            confidence=confidence,
            sentiment_score=sentiment_score,
            positive_score=weighted_positive,
            neutral_score=weighted_neutral,
            negative_score=weighted_negative,
            articles_analyzed=sum(
                event.articles_analyzed
                for event in events
            ),
            article_weights=article_weights,
        )

    def _get_signal(
        self,
        sentiment_score: float,
        positive_score: float,
        neutral_score: float,
        negative_score: float,
    ) -> str:
        if (
            sentiment_score
            >= self.BULLISH_THRESHOLD
            and positive_score
            > neutral_score
            and positive_score
            > negative_score
        ):
            return "bullish"

        if (
            sentiment_score
            <= self.BEARISH_THRESHOLD
            and negative_score
            > neutral_score
            and negative_score
            > positive_score
        ):
            return "bearish"

        return "neutral"

    def _get_confidence(
        self,
        signal: str,
        positive_score: float,
        neutral_score: float,
        negative_score: float,
    ) -> float:
        if signal == "bullish":
            return positive_score

        if signal == "bearish":
            return negative_score

        return neutral_score