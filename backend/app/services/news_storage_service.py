import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.news import ArticleTicker, NewsArticle
from app.models.news_data import CollectedNewsArticle


class NewsStorageService:
    def save_articles(
        self,
        database: Session,
        symbol: str,
        articles: list[CollectedNewsArticle],
    ) -> list[NewsArticle]:
        normalized_symbol = symbol.upper().strip()
        stored_articles: list[NewsArticle] = []

        for collected_article in articles:
            content_hash = self._create_content_hash(collected_article)

            existing_article = database.scalar(
                select(NewsArticle).where(
                    NewsArticle.url == collected_article.url
                )
            )

            if existing_article is None:
                existing_article = database.scalar(
                    select(NewsArticle).where(
                        NewsArticle.content_hash == content_hash
                    )
                )

            if existing_article is None:
                existing_article = NewsArticle(
                    url=collected_article.url,
                    title=collected_article.title,
                    source=collected_article.source,
                    published_at=collected_article.published_at,
                    content_hash=content_hash,
                )

                database.add(existing_article)
                database.flush()

            ticker_exists = database.scalar(
                select(ArticleTicker).where(
                    ArticleTicker.article_id == existing_article.id,
                    ArticleTicker.symbol == normalized_symbol,
                )
            )

            if ticker_exists is None:
                database.add(
                    ArticleTicker(
                        article_id=existing_article.id,
                        symbol=normalized_symbol,
                    )
                )

            stored_articles.append(existing_article)

        database.commit()

        return stored_articles

    def _create_content_hash(
        self,
        article: CollectedNewsArticle,
    ) -> str:
        normalized_title = " ".join(
            article.title.lower().split()
        )

        return hashlib.sha256(
            normalized_title.encode("utf-8")
        ).hexdigest()