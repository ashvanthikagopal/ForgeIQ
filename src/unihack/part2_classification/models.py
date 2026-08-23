from __future__ import annotations

from dataclasses import dataclass, field


# ============================================================
# CLASSIFICATION RESULT
# ============================================================

@dataclass
class ClassificationResult:

    classpath: str

    confidence: float

    alternative_candidates: list[str] = field(
        default_factory=list
    )

    reasoning: str = ""

    needs_review: bool = False

    review_reason: str | None = None


# ============================================================
# ATTRIBUTE RESULT
# ============================================================

@dataclass
class AttributeResult:

    attribute: str

    value: str

    confidence: float

    needs_unit_normalization: bool = False

    raw_text_span: str = ""

    needs_review: bool = False

    validation_error: str | None = None


# ============================================================
# COMPLETE PART 2 RESULT
# ============================================================

@dataclass
class ProductEnrichmentPart2:

    product_index: int | None

    part_desc: str

    mpn: str

    manufacturer: str

    brand: str

    classpath: str

    classification_confidence: float

    attributes: list[
        AttributeResult
    ] = field(
        default_factory=list
    )

    needs_review: bool = False

    review_reasons: list[str] = field(
        default_factory=list
    )