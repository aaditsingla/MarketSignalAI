from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.company_sentiment import CompanySentimentResult
from app.models.event_sentiment import EventSentimentResult
from app.models.signal_summary import SignalSummaryResult
from app.services.company_sentiment_service import (
    CompanySentimentService,
)
from app.services.event_sentiment_service import (
    EventSentimentService,
)


class SignalSummaryService:
    RECENCY_HALF_LIFE_HOURS = 72.0

    NEUTRAL_DIRECTION_THRESHOLD = 0.10
    STRONG_DIRECTION_THRESHOLD = 0.30

    def __init__(self) -> None:
        self.company_service = CompanySentimentService()
        self.event_service = EventSentimentService()

    def build_summary(
        self,
        database: Session,
        symbol: str,
    ) -> SignalSummaryResult:
        normalized_symbol = symbol.upper().strip()

        events = self.event_service.analyze_events(
            database,
            normalized_symbol,
        )

        company = (
            self.company_service.analyze_from_events(
                normalized_symbol,
                events,
            )
        )

        return self.build_from_results(
            normalized_symbol,
            company,
            events,
        )

    def build_from_results(
        self,
        symbol: str,
        company: CompanySentimentResult,
        events: list[EventSentimentResult],
    ) -> SignalSummaryResult:
        normalized_symbol = symbol.upper().strip()

        agreement_score = self._calculate_agreement(
            events
        )

        direction = self._get_direction(
            company.sentiment_score
        )

        conviction = self._get_conviction(
            directional_score=company.sentiment_score,
            neutral_score=company.neutral_score,
            agreement_score=agreement_score,
        )

        news_agreement = self._get_news_agreement(
            agreement_score
        )

        return SignalSummaryResult(
            symbol=normalized_symbol,
            direction=direction,
            conviction=conviction,
            news_agreement=news_agreement,
            directional_score=company.sentiment_score,
            agreement_score=agreement_score,
            positive_score=company.positive_score,
            neutral_score=company.neutral_score,
            negative_score=company.negative_score,
            events_analyzed=len(events),
        )

    def _calculate_agreement(
        self,
        events: list[EventSentimentResult],
    ) -> float:
        if not events:
            return 0.0

        now = datetime.now(timezone.utc)

        weighted_direction = 0.0
        weighted_magnitude = 0.0

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
                ).total_seconds()
                / 3600,
                0.0,
            )

            weight = 0.5 ** (
                age_hours
                / self.RECENCY_HALF_LIFE_HOURS
            )

            weighted_direction += (
                event.directional_score
                * weight
            )

            weighted_magnitude += (
                abs(event.directional_score)
                * weight
            )

        if weighted_magnitude == 0:
            return 0.0

        return min(
            abs(weighted_direction)
            / weighted_magnitude,
            1.0,
        )

    def _get_direction(
        self,
        score: float,
    ) -> str:
        if score >= self.STRONG_DIRECTION_THRESHOLD:
            return "bullish"

        if score >= self.NEUTRAL_DIRECTION_THRESHOLD:
            return "slightly_bullish"

        if score <= -self.STRONG_DIRECTION_THRESHOLD:
            return "bearish"

        if score <= -self.NEUTRAL_DIRECTION_THRESHOLD:
            return "slightly_bearish"

        return "neutral"

    def _get_conviction(
        self,
        directional_score: float,
        neutral_score: float,
        agreement_score: float,
    ) -> str:
        magnitude = abs(directional_score)

        if (
            magnitude >= 0.30
            and agreement_score >= 0.70
            and neutral_score <= 0.35
        ):
            return "high"

        if (
            magnitude >= 0.18
            and agreement_score >= 0.55
            and neutral_score <= 0.50
        ):
            return "moderate"

        return "low"

    def _get_news_agreement(
        self,
        agreement_score: float,
    ) -> str:
        if agreement_score >= 0.70:
            return "consistent"

        if agreement_score >= 0.40:
            return "mixed"

        return "conflicting"