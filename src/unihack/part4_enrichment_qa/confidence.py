"""
Part 4, Phase H (Day 9-10) — Human-in-the-Loop / Confidence Flagging.

For every generated field across Parts 2, 3, and Phase G, attach a
confidence score and a needs_review flag when:
    - Value wasn't found in the LOV
    - Classification confidence was low
    - Manufacturer/brand couldn't be matched to canonical list
    - Source data itself was blank (handle gracefully, don't crash/guess)

This is a strength signal, not a failure — build it out fully.
"""

from __future__ import annotations
import logging

from unihack.schemas import NormalizedRecord, EnrichedRecord, AttributeValue

log = logging.getLogger(__name__)

LOW_CONFIDENCE_THRESHOLD = 0.5


def flag_attribute(attr: AttributeValue) -> AttributeValue:
    if attr.value is None or attr.normalized_value is None:
        attr.needs_review = True
        attr.review_reason = attr.review_reason or "value_not_found_or_unnormalized"
    elif attr.confidence < LOW_CONFIDENCE_THRESHOLD:
        attr.needs_review = True
        attr.review_reason = attr.review_reason or "low_confidence"
    return attr


def compute_overall_confidence(record: NormalizedRecord, enriched_attrs: list[AttributeValue]) -> float:
    """Simple average across classification confidence + all attribute
    confidences (Part 2's, Part 3's normalized ones, and Phase G's
    enrichment). Deliberately simple and explainable for the demo —
    judges should be able to see exactly why a score is what it is."""
    scores = [record.classified_record.classification.confidence]
    scores += [a.confidence for a in record.normalized_attributes]
    scores += [a.confidence for a in enriched_attrs]
    scores = [s for s in scores if s is not None]
    return sum(scores) / len(scores) if scores else 0.0


def build_enriched_record(
    record: NormalizedRecord,
    enriched_attrs: list[AttributeValue] | None = None,
) -> EnrichedRecord:
    enriched_attrs = enriched_attrs or []

    flagged_normalized = [flag_attribute(a) for a in record.normalized_attributes]
    flagged_enriched = [flag_attribute(a) for a in enriched_attrs]

    if record.classified_record.classification.confidence < LOW_CONFIDENCE_THRESHOLD:
        classification_needs_review = True
    else:
        classification_needs_review = False

    if record.normalized_manufacturer is None:
        manufacturer_needs_review = True
    else:
        manufacturer_needs_review = False

    any_attr_needs_review = any(a.needs_review for a in flagged_normalized + flagged_enriched)

    needs_review = classification_needs_review or manufacturer_needs_review or any_attr_needs_review
    overall_confidence = compute_overall_confidence(record, flagged_enriched)

    return EnrichedRecord(
        normalized_record=record,
        enriched_attributes=flagged_enriched,
        overall_confidence=overall_confidence,
        needs_review=needs_review,
    )


def review_queue(records: list[EnrichedRecord]) -> list[EnrichedRecord]:
    """Sorted lowest-confidence-first — feeds the review view (Streamlit
    table or filtered spreadsheet)."""
    flagged = [r for r in records if r.needs_review]
    return sorted(flagged, key=lambda r: (r.overall_confidence if r.overall_confidence is not None else 0.0))