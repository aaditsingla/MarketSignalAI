from pydantic import BaseModel


class ArticleWeightResult(BaseModel):
    article_id: int
    weight: float


class CompanySentimentResult(BaseModel):
    symbol: str
    signal: str
    confidence: float
    sentiment_score: float

    positive_score: float
    neutral_score: float
    negative_score: float

    articles_analyzed: int
    article_weights: list[ArticleWeightResult]