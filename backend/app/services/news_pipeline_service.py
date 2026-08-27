from sqlalchemy.orm import Session

from app.database.models.news import NewsArticle
from app.services.article_scraper_service import ArticleScraperService
from app.services.market_service import MarketService
from app.services.news_collector_service import NewsCollectorService
from app.services.news_relevance_service import NewsRelevanceService
from app.services.news_storage_service import NewsStorageService


class NewsPipelineService:
    def __init__(self) -> None:
        self.market_service = MarketService()
        self.collector = NewsCollectorService()
        self.relevance_service = NewsRelevanceService()
        self.storage_service = NewsStorageService()
        self.scraper_service = ArticleScraperService()

    def collect_filter_and_store(
        self,
        database: Session,
        symbol: str,
        limit: int = 10,
    ) -> dict[str, int]:
        normalized_symbol = symbol.upper().strip()

        stock = self.market_service.get_stock_quote(
            normalized_symbol
        )

        discovered_articles = self.collector.get_company_news(
            normalized_symbol,
            limit=limit,
        )

        relevant_articles = (
            self.relevance_service.filter_relevant_articles(
                normalized_symbol,
                stock.company_name,
                discovered_articles,
            )
        )

        stored_articles = self.storage_service.save_articles(
            database,
            normalized_symbol,
            relevant_articles,
        )

        scraped_count = self._scrape_missing_content(
            database,
            stored_articles,
        )

        return {
            "discovered": len(discovered_articles),
            "relevant": len(relevant_articles),
            "stored_or_linked": len(stored_articles),
            "content_scraped": scraped_count,
        }

    def _scrape_missing_content(
        self,
        database: Session,
        articles: list[NewsArticle],
    ) -> int:
        scraped_count = 0

        for article in articles:
            if article.content:
                continue

            content = self.scraper_service.extract_article_content(
                article.url
            )

            if not content:
                continue

            article.content = content
            scraped_count += 1

        database.commit()

        return scraped_count