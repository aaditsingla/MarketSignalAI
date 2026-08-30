from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.analysis import CompanyAnalysis
from app.models.analysis_comparison import (
    AnalysisComparisonResult,
    AnalysisSnapshotSummary,
)


class AnalysisComparisonService:
    SLIGHT_DIRECTION_THRESHOLD = 0.10
    STRONG_DIRECTION_THRESHOLD = 0.30

    TREND_CHANGE_THRESHOLD = 0.05

    def compare_latest(
        self,
        database: Session,
        symbol: str,
    ) -> AnalysisComparisonResult:
        normalized_symbol = symbol.upper().strip()

        statement = (
            select(CompanyAnalysis)
            .where(
                CompanyAnalysis.symbol == normalized_symbol
            )
            .order_by(
                CompanyAnalysis.analyzed_at.desc()
            )
            .limit(2)
        )

        analyses = list(
            database.scalars(statement).all()
        )

        if not analyses:
            raise ValueError(
                f"No historical analyses available for "
                f"{normalized_symbol}"
            )

        current_analysis = analyses[0]

        current = self._build_summary(
            current_analysis
        )

        if len(analyses) == 1:
            return AnalysisComparisonResult(
                symbol=normalized_symbol,
                current=current,
                previous=None,
                score_change=None,
                price_change_percent=None,
                trend="no_previous_analysis",
            )

        previous_analysis = analyses[1]

        previous = self._build_summary(
            previous_analysis
        )

        score_change = (
            current.directional_score
            - previous.directional_score
        )

        price_change_percent = self._calculate_price_change(
            previous_price=previous.stock_price,
            current_price=current.stock_price,
        )

        trend = self._get_trend(
            score_change
        )

        return AnalysisComparisonResult(
            symbol=normalized_symbol,
            current=current,
            previous=previous,
            score_change=score_change,
            price_change_percent=price_change_percent,
            trend=trend,
        )

    def _build_summary(
        self,
        analysis: CompanyAnalysis,
    ) -> AnalysisSnapshotSummary:
        return AnalysisSnapshotSummary(
            analysis_id=analysis.id,
            analyzed_at=analysis.analyzed_at,
            stock_price=analysis.stock_price,
            direction=self._get_direction(
                analysis.sentiment_score
            ),
            directional_score=analysis.sentiment_score,
        )

    def _get_direction(
        self,
        score: float,
    ) -> str:
        if score >= self.STRONG_DIRECTION_THRESHOLD:
            return "bullish"

        if score >= self.SLIGHT_DIRECTION_THRESHOLD:
            return "slightly_bullish"

        if score <= -self.STRONG_DIRECTION_THRESHOLD:
            return "bearish"

        if score <= -self.SLIGHT_DIRECTION_THRESHOLD:
            return "slightly_bearish"

        return "neutral"

    def _calculate_price_change(
        self,
        previous_price: float,
        current_price: float,
    ) -> float | None:
        if previous_price == 0:
            return None

        return (
            (
                current_price - previous_price
            )
            / previous_price
        ) * 100

    def _get_trend(
        self,
        score_change: float,
    ) -> str:
        if score_change >= self.TREND_CHANGE_THRESHOLD:
            return "improving"

        if score_change <= -self.TREND_CHANGE_THRESHOLD:
            return "weakening"

        return "stable"