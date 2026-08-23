from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# NORMALIZED ATTRIBUTE
# ============================================================

@dataclass
class NormalizedAttribute:
    attribute: str
    raw_value: str
    normalized_value: str
    confidence: float

    needs_review: bool = False
    review_reason: Optional[str] = None


# ============================================================
# MANUFACTURER / BRAND RESULT
# ============================================================

@dataclass
class ManufacturerBrandResult:
    manufacturer: str
    brand: str

    manufacturer_code: str = ""
    brand_code: str = ""

    matched: bool = False

    needs_review: bool = False
    review_reason: Optional[str] = None


# ============================================================
# DESCRIPTION FIELD
# ============================================================

@dataclass
class DescriptionField:
    value: str
    char_count: int

    within_limit: bool = True
    casing_valid: bool = True

    needs_review: bool = False
    review_reason: Optional[str] = None


# ============================================================
# NORMALIZED PRODUCT
# ============================================================

@dataclass
class NormalizedProduct:
    product_index: Optional[int]

    mpn: str
    manufacturer: str
    brand: str
    classpath: str

    classification_confidence: float

    attributes: list[NormalizedAttribute] = field(
        default_factory=list
    )

    needs_review: bool = False

    review_reasons: list[str] = field(
        default_factory=list
    )


# ============================================================
# COMPLETE PART 3 RESULT
# ============================================================

@dataclass
class ProductEnrichmentPart3:
    product: NormalizedProduct

    invoice_desc: DescriptionField
    mobile_desc: DescriptionField
    product_title: DescriptionField
    long_description: DescriptionField

    marketing_copy: Optional[DescriptionField] = None

    needs_review: bool = False

    review_reasons: list[str] = field(
        default_factory=list
    )