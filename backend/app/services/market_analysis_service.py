from sqlalchemy.orm import Session

from app.database.models.analysis import CompanyAnalysis
from app.services.analysis_comparison_service import (
    AnalysisComparisonService,
)
from app.services.article_sentiment_service import (
    ArticleSentimentService,
)
from app.services.company_analysis_service import (
    CompanyAnalysisService,
)
from app.services.company_sentiment_service import (
    CompanySentimentService,
)
from app.services.event_sentiment_service import (
    EventSentimentService,
)
from app.services.market_outlook_service import (
    MarketOutlookService,
)
from app.services.news_pipeline_service import NewsPipelineService
from app.services.signal_summary_service import (
    SignalSummaryService,
)


class MarketAnalysisService:
    def __init__(self) -> None:
        self.news_pipeline = NewsPipelineService()

        self.article_sentiment_service = (
            ArticleSentimentService()
        )

        self.event_sentiment_service = (
            EventSentimentService()
        )

        self.company_sentiment_service = (
            CompanySentimentService()
        )

        self.market_outlook_service = (
            MarketOutlookService()
        )

        self.signal_summary_service = (
            SignalSummaryService()
        )

        self.company_analysis_service = (
            CompanyAnalysisService()
        )

        self.comparison_service = (
            AnalysisComparisonService()
        )

    def run_analysis(
        self,
        database: Session,
        symbol: str,
    ) -> dict:
        normalized_symbol = symbol.upper().strip()

        news_result = (
            self.news_pipeline.collect_filter_and_store(
                database,
                normalized_symbol,
            )
        )

        sentiment_processing = (
            self.article_sentiment_service
            .analyze_articles_for_symbol(
                database,
                normalized_symbol,
            )
        )

        events = (
            self.event_sentiment_service.analyze_events(
                database,
                normalized_symbol,
            )
        )

        company_sentiment = (
            self.company_sentiment_service
            .analyze_from_events(
                normalized_symbol,
                events,
            )
        )

        outlook = (
            self.market_outlook_service
            .build_from_events(
                normalized_symbol,
                events,
            )
        )

        summary = (
            self.signal_summary_service
            .build_from_results(
                normalized_symbol,
                company_sentiment,
                events,
            )
        )

        analysis = (
            self.company_analysis_service
            .create_analysis_from_sentiment(
                database,
                company_sentiment,
            )
        )

        comparison = (
            self.comparison_service.compare_latest(
                database,
                normalized_symbol,
            )
        )

        return {
            "symbol": normalized_symbol,
            "news": news_result,
            "sentiment_processing": sentiment_processing,
            "events_analyzed": len(events),
            "company_sentiment": (
                company_sentiment.model_dump(
                    mode="json"
                )
            ),
            "signal_summary": (
                summary.model_dump(
                    mode="json"
                )
            ),
            "outlook": (
                outlook.model_dump(
                    mode="json"
                )
            ),
            "analysis": self._serialize_analysis(
                analysis
            ),
            "comparison": (
                comparison.model_dump(
                    mode="json"
                )
            ),
        }

    def _serialize_analysis(
        self,
        analysis: CompanyAnalysis,
    ) -> dict:
        return {
            "id": analysis.id,
            "symbol": analysis.symbol,
            "stock_price": analysis.stock_price,
            "signal": analysis.signal,
            "confidence": analysis.confidence,
            "sentiment_score": analysis.sentiment_score,
            "positive_score": analysis.positive_score,
            "neutral_score": analysis.neutral_score,
            "negative_score": analysis.negative_score,
            "articles_analyzed": analysis.articles_analyzed,
            "analyzed_at": (
                analysis.analyzed_at.isoformat()
            ),
        }