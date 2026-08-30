from datetime import datetime, timezone

import numpy as np

from app.database.models.news import NewsArticle
from app.models.news_event import NewsEventGroup
from app.services.model_registry import (
    get_event_embedding_model,
)


class NewsEventService:
    STRONG_TITLE_THRESHOLD = 0.76

    MODERATE_TITLE_THRESHOLD = 0.64
    STRONG_LEAD_THRESHOLD = 0.74

    MAX_EVENT_SPAN_HOURS = 48.0
    LEAD_LENGTH = 350

    @property
    def model(self):
        return get_event_embedding_model()

    def group_articles(
        self,
        articles: list[NewsArticle],
    ) -> list[NewsEventGroup]:
        if not articles:
            return []

        sorted_articles = sorted(
            articles,
            key=self._article_time,
        )

        titles = [
            article.title
            for article in sorted_articles
        ]

        leads = [
            self._build_lead(article)
            for article in sorted_articles
        ]

        title_embeddings = self.model.encode(
            titles,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        lead_embeddings = self.model.encode(
            leads,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        clusters: list[dict] = []

        for article, title_embedding, lead_embedding in zip(
            sorted_articles,
            title_embeddings,
            lead_embeddings,
        ):
            best_cluster = None
            best_score = -1.0

            for cluster in clusters:
                if not self._within_time_window(
                    article,
                    cluster,
                ):
                    continue

                if not self._matches_cluster_members(
                    title_embedding,
                    lead_embedding,
                    cluster,
                ):
                    continue

                title_similarity = float(
                    np.dot(
                        title_embedding,
                        cluster["title_centroid"],
                    )
                )

                lead_similarity = float(
                    np.dot(
                        lead_embedding,
                        cluster["lead_centroid"],
                    )
                )

                score = self._combined_score(
                    title_similarity,
                    lead_similarity,
                )

                if score > best_score:
                    best_score = score
                    best_cluster = cluster

            if best_cluster is None:
                clusters.append(
                    self._create_cluster(
                        article=article,
                        title_embedding=title_embedding,
                        lead_embedding=lead_embedding,
                    )
                )
            else:
                self._add_to_cluster(
                    cluster=best_cluster,
                    article=article,
                    title_embedding=title_embedding,
                    lead_embedding=lead_embedding,
                    similarity=best_score,
                )

        return [
            self._convert_cluster(cluster)
            for cluster in clusters
        ]

    def _matches_cluster_members(
        self,
        title_embedding: np.ndarray,
        lead_embedding: np.ndarray,
        cluster: dict,
    ) -> bool:
        for member_title, member_lead in zip(
            cluster["title_embeddings"],
            cluster["lead_embeddings"],
        ):
            title_similarity = float(
                np.dot(
                    title_embedding,
                    member_title,
                )
            )

            lead_similarity = float(
                np.dot(
                    lead_embedding,
                    member_lead,
                )
            )

            if self._is_event_match(
                title_similarity,
                lead_similarity,
            ):
                return True

        return False

    def _is_event_match(
        self,
        title_similarity: float,
        lead_similarity: float,
    ) -> bool:
        if (
            title_similarity
            >= self.STRONG_TITLE_THRESHOLD
        ):
            return True

        return (
            title_similarity
            >= self.MODERATE_TITLE_THRESHOLD
            and lead_similarity
            >= self.STRONG_LEAD_THRESHOLD
        )

    def _combined_score(
        self,
        title_similarity: float,
        lead_similarity: float,
    ) -> float:
        return (
            title_similarity * 0.65
            + lead_similarity * 0.35
        )

    def _build_lead(
        self,
        article: NewsArticle,
    ) -> str:
        if not article.content:
            return article.title

        lead = article.content[
            :self.LEAD_LENGTH
        ]

        return f"{article.title}\n{lead}"

    def _create_cluster(
        self,
        article: NewsArticle,
        title_embedding: np.ndarray,
        lead_embedding: np.ndarray,
    ) -> dict:
        article_time = self._article_time(article)

        return {
            "articles": [article],
            "title_embeddings": [title_embedding],
            "lead_embeddings": [lead_embedding],
            "title_centroid": title_embedding.copy(),
            "lead_centroid": lead_embedding.copy(),
            "similarities": [1.0],
            "earliest": article_time,
            "latest": article_time,
        }

    def _add_to_cluster(
        self,
        cluster: dict,
        article: NewsArticle,
        title_embedding: np.ndarray,
        lead_embedding: np.ndarray,
        similarity: float,
    ) -> None:
        cluster["articles"].append(article)

        cluster["title_embeddings"].append(
            title_embedding
        )

        cluster["lead_embeddings"].append(
            lead_embedding
        )

        cluster["similarities"].append(
            similarity
        )

        cluster["title_centroid"] = (
            self._normalized_centroid(
                cluster["title_embeddings"]
            )
        )

        cluster["lead_centroid"] = (
            self._normalized_centroid(
                cluster["lead_embeddings"]
            )
        )

        article_time = self._article_time(article)

        if article_time < cluster["earliest"]:
            cluster["earliest"] = article_time

        if article_time > cluster["latest"]:
            cluster["latest"] = article_time

    def _normalized_centroid(
        self,
        embeddings: list[np.ndarray],
    ) -> np.ndarray:
        stacked = np.stack(embeddings)

        centroid = stacked.mean(axis=0)

        norm = np.linalg.norm(centroid)

        if norm > 0:
            centroid = centroid / norm

        return centroid

    def _within_time_window(
        self,
        article: NewsArticle,
        cluster: dict,
    ) -> bool:
        article_time = self._article_time(article)

        earliest = min(
            cluster["earliest"],
            article_time,
        )

        latest = max(
            cluster["latest"],
            article_time,
        )

        span_hours = (
            latest - earliest
        ).total_seconds() / 3600

        return (
            span_hours
            <= self.MAX_EVENT_SPAN_HOURS
        )

    def _convert_cluster(
        self,
        cluster: dict,
    ) -> NewsEventGroup:
        articles: list[NewsArticle] = (
            cluster["articles"]
        )

        representative = (
            self._find_representative_article(
                cluster
            )
        )

        similarities: list[float] = (
            cluster["similarities"]
        )

        return NewsEventGroup(
            representative_article_id=(
                representative.id
            ),
            representative_title=(
                representative.title
            ),
            article_ids=[
                article.id
                for article in articles
            ],
            earliest_published_at=(
                cluster["earliest"]
            ),
            latest_published_at=(
                cluster["latest"]
            ),
            average_similarity=(
                sum(similarities)
                / len(similarities)
            ),
        )

    def _find_representative_article(
        self,
        cluster: dict,
    ) -> NewsArticle:
        articles: list[NewsArticle] = (
            cluster["articles"]
        )

        title_embeddings = (
            cluster["title_embeddings"]
        )

        centroid = cluster["title_centroid"]

        similarities = [
            float(
                np.dot(
                    embedding,
                    centroid,
                )
            )
            for embedding in title_embeddings
        ]

        best_index = int(
            np.argmax(similarities)
        )

        return articles[best_index]

    def _article_time(
        self,
        article: NewsArticle,
    ) -> datetime:
        article_time = (
            article.published_at
            or article.fetched_at
            or datetime.now(timezone.utc)
        )

        if article_time.tzinfo is None:
            article_time = article_time.replace(
                tzinfo=timezone.utc
            )

        return article_time