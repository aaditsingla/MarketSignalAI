from datetime import datetime, timezone

import yfinance as yf

from app.models.news_data import CollectedNewsArticle


class NewsCollectorService:
    def get_company_news(
        self,
        symbol: str,
        limit: int = 10,
    ) -> list[CollectedNewsArticle]:
        normalized_symbol = symbol.upper().strip()

        raw_news = self._fetch_news(
            symbol=normalized_symbol,
            limit=limit,
        )

        articles: list[CollectedNewsArticle] = []

        for item in raw_news:
            article = self._parse_news_item(item)

            if article is not None:
                articles.append(article)

        return articles[:limit]

    def _fetch_news(
        self,
        symbol: str,
        limit: int,
    ) -> list[dict]:
        ticker = yf.Ticker(symbol)

        try:
            ticker_news = ticker.get_news(
                count=limit,
                tab="news",
            )

            if ticker_news:
                return ticker_news

        except Exception:
            pass

        try:
            search = yf.Search(
                symbol,
                max_results=1,
                news_count=limit,
            )

            if search.news:
                return search.news

        except Exception:
            pass

        return []

    def _parse_news_item(
        self,
        item: dict,
    ) -> CollectedNewsArticle | None:
        content = item.get("content")

        if not isinstance(content, dict):
            content = {}

        title = (
            content.get("title")
            or item.get("title")
        )

        source = self._get_source(
            content,
            item,
        )

        url = self._get_url(
            content,
            item,
        )

        published_at = self._parse_publish_time(
            content.get("pubDate")
            or item.get("providerPublishTime")
        )

        summary = (
            content.get("summary")
            or content.get("description")
            or item.get("summary")
        )

        if not title or not url:
            return None

        return CollectedNewsArticle(
            title=title,
            url=url,
            source=source,
            published_at=published_at,
            summary=summary,
        )

    def _get_source(
        self,
        content: dict,
        item: dict,
    ) -> str | None:
        provider = content.get("provider")

        if isinstance(provider, dict):
            provider_name = provider.get(
                "displayName"
            )

            if provider_name:
                return provider_name

        return item.get("publisher")

    def _get_url(
        self,
        content: dict,
        item: dict,
    ) -> str | None:
        for key in (
            "canonicalUrl",
            "clickThroughUrl",
            "previewUrl",
        ):
            url_data = content.get(key)

            if isinstance(url_data, dict):
                url = url_data.get("url")

                if url:
                    return url

            if isinstance(url_data, str):
                return url_data

        return item.get("link")

    def _parse_publish_time(
        self,
        value: str | int | float | None,
    ) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(
                value,
                tz=timezone.utc,
            )

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00",
                    )
                )
            except ValueError:
                return None

        return None