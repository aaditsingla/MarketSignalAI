from functools import lru_cache

from sentence_transformers import SentenceTransformer
from transformers import pipeline


@lru_cache(maxsize=1)
def get_event_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


@lru_cache(maxsize=1)
def get_event_classifier():
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
    )