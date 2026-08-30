from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.market_outlook import (
    MarketOutlookResult,
    OutlookEvent,
)
from app.services.event_sentiment_service import (
    EventSentimentService,
)


class MarketOutlookService:
    RECENCY_HALF_LIFE_HOURS = 72.0

    MAX_ITEMS_PER_GROUP = 3

    MIN_DIRECTIONAL_STRENGTH = 0.10

    FUNDAMENTAL_CATEGORIES = {
        "earnings",
        "guidance",
        "product_technology",
        "partnership_deal",
        "financing_capital",
        "competition_demand",
        "regulation_legal",
    }

    SUPPORTING_SIGNAL_CATEGORIES = {
        "analyst_valuation",
        "insider_activity",
        "market_movement",
    }

    def __init__(self) -> None:
        self.event_service = EventSentimentService()

    def build_outlook(
        self,
        database: Session,
        symbol: str,
    ) -> MarketOutlookResult:
        normalized_symbol = symbol.upper().strip()

        events = self.event_service.analyze_events(
            database,
            normalized_symbol,
        )

        now = datetime.now(timezone.utc)

        positive_catalysts = []
        negative_risks = []

        positive_signals = []
        negative_signals = []

        for event in events:
            if (
                abs(event.directional_score)
                < self.MIN_DIRECTIONAL_STRENGTH
            ):
                continue

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

            recency_weight = 0.5 ** (
                age_hours
                / self.RECENCY_HALF_LIFE_HOURS
            )

            ranking_score = (
                abs(event.directional_score)
                * recency_weight
            )

            outlook_event = OutlookEvent(
                title=event.representative_title,
                category=event.category,
                directional_score=event.directional_score,
                unique_sources=event.unique_sources,
                article_ids=event.article_ids,
            )

            if (
                event.category
                in self.FUNDAMENTAL_CATEGORIES
            ):
                if event.directional_score > 0:
                    positive_catalysts.append(
                        (
                            ranking_score,
                            outlook_event,
                        )
                    )

                else:
                    negative_risks.append(
                        (
                            ranking_score,
                            outlook_event,
                        )
                    )

            elif (
                event.category
                in self.SUPPORTING_SIGNAL_CATEGORIES
            ):
                if event.directional_score > 0:
                    positive_signals.append(
                        (
                            ranking_score,
                            outlook_event,
                        )
                    )

                else:
                    negative_signals.append(
                        (
                            ranking_score,
                            outlook_event,
                        )
                    )

        positive_catalysts = self._top_events(
            positive_catalysts
        )

        negative_risks = self._top_events(
            negative_risks
        )

        positive_signals = self._top_events(
            positive_signals
        )

        negative_signals = self._top_events(
            negative_signals
        )

        return MarketOutlookResult(
            symbol=normalized_symbol,
            positive_catalysts=positive_catalysts,
            negative_risks=negative_risks,
            positive_signals=positive_signals,
            negative_signals=negative_signals,
            events_analyzed=len(events),
        )

    def _top_events(
        self,
        ranked_events: list[
            tuple[float, OutlookEvent]
        ],
    ) -> list[OutlookEvent]:
        ranked_events.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            event
            for _, event
            in ranked_events[
                :self.MAX_ITEMS_PER_GROUP
            ]
        ]