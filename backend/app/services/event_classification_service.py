from app.models.event_classification import (
    EventClassificationResult,
)
from app.services.model_registry import (
    get_event_classifier,
)


class EventClassificationService:
    MIN_CLASSIFICATION_SCORE = 0.40

    CATEGORY_LABELS = {
        "earnings": (
            "quarterly earnings and financial results"
        ),
        "guidance": (
            "future company guidance and financial outlook"
        ),
        "product_technology": (
            "product launch or technology development"
        ),
        "partnership_deal": (
            "business partnership, collaboration or corporate deal"
        ),
        "financing_capital": (
            "financing, investment or capital allocation"
        ),
        "competition_demand": (
            "competition, market share or customer demand"
        ),
        "regulation_legal": (
            "regulation, government action or legal dispute"
        ),
        "analyst_valuation": (
            "analyst rating, price target or company valuation"
        ),
        "insider_activity": (
            "insider or major shareholder buying or selling shares"
        ),
        "market_movement": (
            "stock price or general market movement"
        ),
    }

    @property
    def classifier(self):
        return get_event_classifier()

    def classify(
        self,
        event_text: str,
    ) -> EventClassificationResult:
        if not event_text.strip():
            raise ValueError(
                "Cannot classify an empty event"
            )

        candidate_labels = list(
            self.CATEGORY_LABELS.values()
        )

        result = self.classifier(
            event_text,
            candidate_labels=candidate_labels,
            multi_label=False,
        )

        best_label = result["labels"][0]

        best_score = float(
            result["scores"][0]
        )

        if (
            best_score
            < self.MIN_CLASSIFICATION_SCORE
        ):
            return EventClassificationResult(
                category="other",
                score=best_score,
            )

        category_lookup = {
            description: category
            for category, description
            in self.CATEGORY_LABELS.items()
        }

        return EventClassificationResult(
            category=category_lookup[
                best_label
            ],
            score=best_score,
        )