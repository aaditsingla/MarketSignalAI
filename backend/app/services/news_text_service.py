import re


class NewsTextService:
    MIN_PARAGRAPH_LENGTH = 40

    def clean_article_text(
        self,
        content: str,
    ) -> str:
        paragraphs = content.splitlines()

        cleaned_paragraphs: list[str] = []
        seen_paragraphs: set[str] = set()

        for paragraph in paragraphs:
            cleaned = self._clean_paragraph(paragraph)

            if len(cleaned) < self.MIN_PARAGRAPH_LENGTH:
                continue

            normalized = cleaned.lower()

            if normalized in seen_paragraphs:
                continue

            seen_paragraphs.add(normalized)
            cleaned_paragraphs.append(cleaned)

        return "\n".join(cleaned_paragraphs)

    def split_into_sentences(
        self,
        content: str,
    ) -> list[str]:
        normalized = re.sub(
            r"\s+",
            " ",
            content,
        ).strip()

        if not normalized:
            return []

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            normalized,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def _clean_paragraph(
        self,
        paragraph: str,
    ) -> str:
        paragraph = re.sub(
            r"\s+",
            " ",
            paragraph,
        )

        return paragraph.strip()