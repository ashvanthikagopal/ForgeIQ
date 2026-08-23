"""
Part 4 - Confidence scoring.

Calculates confidence for values produced during enrichment
and determines whether human review is required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConfidenceResult:
    score: float
    needs_review: bool
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "confidence": self.score,
            "needs_review": self.needs_review,
            "reason": self.reason,
        }


def calculate_confidence(
    value: Any,
    *,
    source: str = "part3",
    lov_valid: bool = True,
    manufacturer_matched: bool = True,
    classification_confidence: float = 1.0,
) -> ConfidenceResult:

    # Missing value
    if value is None or str(value).strip() == "":
        return ConfidenceResult(
            score=0.0,
            needs_review=True,
            reason="value_missing",
        )

    score = 1.0

    # Part 3 direct/normalized value
    if source == "part3":
        score = 0.95

    # Manufacturer source enrichment is lower confidence
    elif source == "manufacturer":
        score = 0.80

    elif source == "manual":
        score = 0.70

    # LOV mismatch
    if not lov_valid:
        score -= 0.25

    # Manufacturer could not be matched
    if not manufacturer_matched:
        score -= 0.20

    # Classification confidence affects final confidence
    score *= max(0.0, min(1.0, classification_confidence))

    score = max(0.0, min(1.0, score))

    needs_review = score < 0.80 or not lov_valid or not manufacturer_matched

    if needs_review:
        reason = "low_confidence_or_validation_issue"
    else:
        reason = "high_confidence"

    return ConfidenceResult(
        score=round(score, 4),
        needs_review=needs_review,
        reason=reason,
    )