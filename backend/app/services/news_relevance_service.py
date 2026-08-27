import re

from app.models.news_data import CollectedNewsArticle


class NewsRelevanceService:
    COMPANY_SUFFIXES = {
        "inc",
        "incorporated",
        "corp",
        "corporation",
        "company",
        "co",
        "ltd",
        "limited",
        "plc",
        "holdings",
        "group",
    }

    def filter_relevant_articles(
        self,
        symbol: str,
        company_name: str,
        articles: list[CollectedNewsArticle],
    ) -> list[CollectedNewsArticle]:
        return [
            article
            for article in articles
            if self.is_relevant(
                symbol,
                company_name,
                article,
            )
        ]

    def is_relevant(
        self,
        symbol: str,
        company_name: str,
        article: CollectedNewsArticle,
    ) -> bool:
        combined_text = " ".join(
            part
            for part in [
                article.title,
                article.summary or "",
            ]
            if part
        )

        if self._contains_symbol(
            combined_text,
            symbol,
        ):
            return True

        normalized_text = self._normalize_text(combined_text)

        company_tokens = self._get_company_tokens(company_name)

        if not company_tokens:
            return False

        token_matches = sum(
            token in normalized_text.split()
            for token in company_tokens
        )

        required_matches = (
            1
            if len(company_tokens) == 1
            else 2
        )

        return token_matches >= required_matches

    def _contains_symbol(
        self,
        text: str,
        symbol: str,
    ) -> bool:
        pattern = rf"\b{re.escape(symbol)}\b"

        return (
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            is not None
        )

    def _get_company_tokens(
        self,
        company_name: str,
    ) -> list[str]:
        normalized_name = self._normalize_text(company_name)

        return [
            token
            for token in normalized_name.split()
            if token not in self.COMPANY_SUFFIXES
        ]

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        normalized = re.sub(
            r"[^a-zA-Z0-9\s]",
            " ",
            text.lower(),
        )

        return " ".join(normalized.split())