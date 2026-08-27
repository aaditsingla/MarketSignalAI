import re

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


class ArticleScraperService:
    REQUEST_TIMEOUT = 15.0
    PLAYWRIGHT_TIMEOUT = 15000

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    }

    def extract_article_content(
        self,
        url: str,
    ) -> str | None:
        content = self._extract_with_httpx(url)

        if content:
            return content

        return self._extract_with_playwright(url)

    def _extract_with_httpx(
        self,
        url: str,
    ) -> str | None:
        try:
            response = httpx.get(
                url,
                headers=self.HEADERS,
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True,
            )

            response.raise_for_status()

        except httpx.HTTPError:
            return None

        return self._extract_text(response.text)

    def _extract_with_playwright(
        self,
        url: str,
    ) -> str | None:
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True
                )

                page = browser.new_page(
                    user_agent=self.HEADERS["User-Agent"]
                )

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.PLAYWRIGHT_TIMEOUT,
                )

                page.wait_for_timeout(2000)

                html = page.content()

                browser.close()

                return self._extract_text(html)

        except PlaywrightError:
            return None

    def _extract_text(
        self,
        html: str,
    ) -> str | None:
        soup = BeautifulSoup(html, "lxml")

        self._remove_noise(soup)

        article = soup.find("article")

        if article is not None:
            text = self._extract_paragraphs(article)

            if self._is_valid_content(text):
                return text

        selectors = [
            "[class*='article-body']",
            "[class*='articleBody']",
            "[class*='story-body']",
            "[class*='storyBody']",
            "[class*='article-content']",
            "[class*='articleContent']",
            "[class*='post-content']",
            "main",
        ]

        for selector in selectors:
            container = soup.select_one(selector)

            if container is None:
                continue

            text = self._extract_paragraphs(container)

            if self._is_valid_content(text):
                return text

        return None

    def _extract_paragraphs(
        self,
        container,
    ) -> str:
        paragraphs = [
            paragraph.get_text(
                " ",
                strip=True,
            )
            for paragraph in container.find_all("p")
        ]

        paragraphs = [
            paragraph
            for paragraph in paragraphs
            if len(paragraph) >= 30
        ]

        text = "\n".join(paragraphs)

        return self._clean_text(text)

    def _remove_noise(
        self,
        soup: BeautifulSoup,
    ) -> None:
        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "noscript",
            ]
        ):
            tag.decompose()

    def _clean_text(
        self,
        text: str,
    ) -> str:
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def _is_valid_content(
        self,
        text: str,
    ) -> bool:
        return len(text) >= 300