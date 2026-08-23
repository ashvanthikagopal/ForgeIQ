from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ProductRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    part_desc: str = ""
    mpn: str = ""
    manufacturer: str = ""
    brand: str = ""


class ClassificationResult(BaseModel):
    classpath: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    alternative_candidates: List[str] = Field(default_factory=list)
    reasoning: str = ""
    needs_review: bool = False
    validation_error: Optional[str] = None


class AttributeResult(BaseModel):
    attribute: str
    value: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    needs_unit_normalization: bool = False
    raw_text_span: str = ""
    needs_review: bool = False
    validation_error: Optional[str] = None


class ProductEnrichmentPart2(BaseModel):
    product_index: Optional[int] = None

    part_desc: str
    mpn: str = ""
    manufacturer: str = ""
    brand: str = ""

    classpath: str
    classification_confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    alternative_candidates: List[str] = Field(
        default_factory=list
    )

    classification_reasoning: str = ""

    attributes: List[AttributeResult] = Field(
        default_factory=list
    )

    needs_review: bool = False

    review_reasons: List[str] = Field(
        default_factory=list
    )