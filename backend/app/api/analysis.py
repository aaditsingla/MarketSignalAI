from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models.analysis import CompanyAnalysis
from app.services.market_analysis_service import MarketAnalysisService


router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


@router.post("/{symbol}")
def run_market_analysis(
    symbol: str,
) -> dict:
    database = SessionLocal()

    try:
        service = MarketAnalysisService()

        return service.run_analysis(
            database,
            symbol,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Market analysis failed: {exc}",
        ) from exc

    finally:
        database.close()


@router.get("/{symbol}/latest")
def get_latest_analysis(
    symbol: str,
) -> dict:
    database = SessionLocal()

    try:
        normalized_symbol = symbol.upper().strip()

        statement = (
            select(CompanyAnalysis)
            .where(
                CompanyAnalysis.symbol
                == normalized_symbol
            )
            .order_by(
                CompanyAnalysis.analyzed_at.desc()
            )
            .limit(1)
        )

        analysis = database.scalar(
            statement
        )

        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No analysis available for "
                    f"{normalized_symbol}"
                ),
            )

        return {
            "id": analysis.id,
            "symbol": analysis.symbol,
            "stock_price": analysis.stock_price,
            "signal": analysis.signal,
            "confidence": analysis.confidence,
            "sentiment_score": (
                analysis.sentiment_score
            ),
            "positive_score": (
                analysis.positive_score
            ),
            "neutral_score": (
                analysis.neutral_score
            ),
            "negative_score": (
                analysis.negative_score
            ),
            "articles_analyzed": (
                analysis.articles_analyzed
            ),
            "analyzed_at": (
                analysis.analyzed_at.isoformat()
            ),
        }

    finally:
        database.close()