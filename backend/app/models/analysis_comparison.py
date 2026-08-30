from datetime import datetime

from pydantic import BaseModel


class AnalysisSnapshotSummary(BaseModel):
    analysis_id: int
    analyzed_at: datetime

    stock_price: float

    direction: str
    directional_score: float


class AnalysisComparisonResult(BaseModel):
    symbol: str

    current: AnalysisSnapshotSummary
    previous: AnalysisSnapshotSummary | None

    score_change: float | None
    price_change_percent: float | None

    trend: str