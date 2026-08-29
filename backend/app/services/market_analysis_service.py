from sqlalchemy.orm import Session

from app.database.models.analysis import CompanyAnalysis
from app.services.article_sentiment_service import ArticleSentimentService
from app.services.company_analysis_service import CompanyAnalysisService
from app.services.news_pipeline_service import NewsPipelineService


class MarketAnalysisService:
    def __init__(self) -> None:
        self.news_pipeline = NewsPipelineService()
        self.article_sentiment_service = ArticleSentimentService()
        self.company_analysis_service = CompanyAnalysisService()

    def run_analysis(
        self,
        database: Session,
        symbol: str,
    ) -> dict:
        normalized_symbol = symbol.upper().strip()

        news_result = self.news_pipeline.collect_filter_and_store(
            database,
            normalized_symbol,
        )

        sentiment_result = (
            self.article_sentiment_service.analyze_articles_for_symbol(
                database,
                normalized_symbol,
            )
        )

        analysis = self.company_analysis_service.create_analysis(
            database,
            normalized_symbol,
        )

        return {
            "symbol": normalized_symbol,
            "news": news_result,
            "sentiment_processing": sentiment_result,
            "analysis": self._serialize_analysis(analysis),
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
            "analyzed_at": analysis.analyzed_at.isoformat(),
        }