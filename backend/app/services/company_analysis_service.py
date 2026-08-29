from sqlalchemy.orm import Session

from app.database.models.analysis import (
    AnalysisArticle,
    CompanyAnalysis,
)
from app.services.company_sentiment_service import (
    CompanySentimentService,
)
from app.services.market_service import MarketService


class CompanyAnalysisService:
    def __init__(self) -> None:
        self.sentiment_service = CompanySentimentService()
        self.market_service = MarketService()

    def create_analysis(
        self,
        database: Session,
        symbol: str,
    ) -> CompanyAnalysis:
        normalized_symbol = symbol.upper().strip()

        sentiment = self.sentiment_service.analyze_company(
            database,
            normalized_symbol,
        )

        stock = self.market_service.get_stock_quote(
            normalized_symbol
        )

        analysis = CompanyAnalysis(
            symbol=normalized_symbol,
            stock_price=stock.price,
            signal=sentiment.signal,
            confidence=sentiment.confidence,
            sentiment_score=sentiment.sentiment_score,
            positive_score=sentiment.positive_score,
            neutral_score=sentiment.neutral_score,
            negative_score=sentiment.negative_score,
            articles_analyzed=sentiment.articles_analyzed,
        )

        database.add(analysis)
        database.flush()

        for article_weight in sentiment.article_weights:
            database.add(
                AnalysisArticle(
                    analysis_id=analysis.id,
                    article_id=article_weight.article_id,
                    weight=article_weight.weight,
                )
            )

        database.commit()
        database.refresh(analysis)

        return analysis