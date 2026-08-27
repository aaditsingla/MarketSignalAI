import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.models.sentiment import SentimentResult
from app.services.news_text_service import NewsTextService


class SentimentService:
    MODEL_NAME = "ProsusAI/finbert"

    TARGET_CHUNK_TOKENS = 420
    MAX_MODEL_TOKENS = 512

    def __init__(self) -> None:
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_NAME
        )

        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.MODEL_NAME
        )

        self.model.to(self.device)
        self.model.eval()

        self.text_service = NewsTextService()

    def analyze(
        self,
        text: str,
    ) -> SentimentResult:
        if not text.strip():
            raise ValueError("Cannot analyze empty article text")

        sentences = self.text_service.split_into_sentences(text)

        chunks = self._build_chunks(sentences)

        if not chunks:
            raise ValueError("Could not create sentiment chunks")

        chunk_texts = [
            chunk_text
            for chunk_text, _ in chunks
        ]

        chunk_weights = torch.tensor(
            [
                token_count
                for _, token_count in chunks
            ],
            dtype=torch.float32,
            device=self.device,
        )

        inputs = self.tokenizer(
            chunk_texts,
            padding=True,
            truncation=True,
            max_length=self.MAX_MODEL_TOKENS,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1,
        )

        weighted_probabilities = (
            probabilities * chunk_weights.unsqueeze(1)
        )

        article_probabilities = (
            weighted_probabilities.sum(dim=0)
            / chunk_weights.sum()
        )

        scores: dict[str, float] = {}

        for index, probability in enumerate(
            article_probabilities
        ):
            label = self.model.config.id2label[index].lower()

            scores[label] = probability.item()

        positive_score = scores.get("positive", 0.0)
        neutral_score = scores.get("neutral", 0.0)
        negative_score = scores.get("negative", 0.0)

        final_scores = {
            "positive": positive_score,
            "neutral": neutral_score,
            "negative": negative_score,
        }

        label = max(
            final_scores,
            key=final_scores.get,
        )

        confidence = final_scores[label]

        return SentimentResult(
            label=label,
            confidence=confidence,
            positive_score=positive_score,
            neutral_score=neutral_score,
            negative_score=negative_score,
            chunks_analyzed=len(chunks),
        )

    def _build_chunks(
        self,
        sentences: list[str],
    ) -> list[tuple[str, int]]:
        chunks: list[tuple[str, int]] = []

        current_sentences: list[str] = []
        current_token_count = 0

        for sentence in sentences:
            sentence_token_count = self._count_tokens(sentence)

            would_exceed_target = (
                current_sentences
                and (
                    current_token_count + sentence_token_count
                    > self.TARGET_CHUNK_TOKENS
                )
            )

            if would_exceed_target:
                chunks.append(
                    (
                        " ".join(current_sentences),
                        current_token_count,
                    )
                )

                current_sentences = []
                current_token_count = 0

            current_sentences.append(sentence)
            current_token_count += sentence_token_count

        if current_sentences:
            chunks.append(
                (
                    " ".join(current_sentences),
                    current_token_count,
                )
            )

        return chunks

    def _count_tokens(
        self,
        text: str,
    ) -> int:
        return len(
            self.tokenizer.encode(
                text,
                add_special_tokens=False,
            )
        )