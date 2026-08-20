"""
Shared data contract for the whole pipeline.

Every part reads and writes these shapes. If you need to change one,
say so in the team channel first — Part 3 and Part 4 both import
`ClassifiedRecord`, and Part 4 imports everything.

Ownership doesn't mean "only I touch this file" — it means "I own this
folder's logic." This file belongs to everyone equally.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Part 1 — foundation / lookups
# ---------------------------------------------------------------------------

@dataclass
class ManufacturerBrand:
    manufacturer_name: str
    manufacturer_code: str
    brand_name: str
    brand_code: str


@dataclass
class UomRule:
    measurement_type: str
    raw_forms: list[str]          # e.g. ["inches", "IN.", "inch"]
    approved_form: str            # e.g. "in"
    space_before_unit: bool = True


@dataclass
class DecimalFractionEntry:
    decimal: float
    fraction: str                 # e.g. "1/4"


@dataclass
class LovEntry:
    classpath: str
    leaf_node: str
    filtering: bool
    attribute_label: str
    attribute_values: list[str]
    normalized_label: str
    normalized_values: list[str]
    guidelines: Optional[str] = None
    remarks: Optional[str] = None


@dataclass
class RawInputRow:
    """One row from Sample-1000_Items.xlsx or the 200-item Input sheet."""
    mfg_part_num: str
    part_desc: str
    e1_brand: Optional[str] = None
    unilog_brand: Optional[str] = None
    dib_brand: Optional[str] = None
    part_manuf: Optional[str] = None


# ---------------------------------------------------------------------------
# Part 2 — classification + attribute extraction
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    classpath: str                # must be verbatim from the allowed LOV list
    confidence: float              # 0-1
    alternative_candidates: list[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class AttributeValue:
    attribute: str
    value: str
    confidence: float
    needs_unit_normalization: bool = False
    raw_text_span: Optional[str] = None
    # filled in later by Part 3/4 — leave None when you hand this off
    normalized_value: Optional[str] = None
    source_url: Optional[str] = None
    method: str = "extracted"      # extracted | inferred_manufacturer_source | manual
    needs_review: bool = False
    review_reason: Optional[str] = None


@dataclass
class ClassifiedRecord:
    """Part 2's handoff to Part 3 and Part 4."""
    input_row: RawInputRow
    classification: ClassificationResult
    attributes: list[AttributeValue] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Part 3 — normalization + description building
# ---------------------------------------------------------------------------

@dataclass
class DescriptionField:
    field: str                     # "Invoice Desc" | "Mobile Desc" | "Product Title" | "Long Description"
    value: str
    char_count: int
    within_limit: bool


@dataclass
class NormalizedRecord:
    """Part 3's handoff to Part 4."""
    classified_record: ClassifiedRecord
    normalized_manufacturer: Optional[str] = None
    normalized_brand: Optional[str] = None
    normalized_attributes: list[AttributeValue] = field(default_factory=list)
    descriptions: list[DescriptionField] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Part 4 — enrichment / QA / evaluation
# ---------------------------------------------------------------------------

@dataclass
class QAViolation:
    field: str
    issue: str
    severity: str                  # "low" | "medium" | "high"
    type: str                      # lov_mismatch | uom_violation | manufacturer_mismatch |
                                    # char_limit_exceeded | casing_violation |
                                    # placeholder_detected | source_gap


@dataclass
class EnrichedRecord:
    """The final, merged, deliverable record. Part 4 owns assembling this."""
    normalized_record: NormalizedRecord
    enriched_attributes: list[AttributeValue] = field(default_factory=list)   # Phase G fills
    violations: list[QAViolation] = field(default_factory=list)
    overall_confidence: Optional[float] = None
    needs_review: bool = False


@dataclass
class EvaluationMetrics:
    """One row of the Phase I summary table."""
    classification_accuracy: Optional[float] = None
    attribute_precision: Optional[float] = None
    attribute_recall: Optional[float] = None
    lov_compliance_rate: Optional[float] = None
    manufacturer_match_rate: Optional[float] = None
    char_limit_compliance: Optional[float] = None
    unit_conversion_accuracy: Optional[float] = None
    coverage_processed_pct: Optional[float] = None
    coverage_flagged_pct: Optional[float] = None
    avg_time_per_item_sec: Optional[float] = None