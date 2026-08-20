import pandas as pd

from unihack.schemas import (
    RawInputRow, ClassificationResult, AttributeValue, ClassifiedRecord,
    NormalizedRecord, DescriptionField,
)
from unihack.part1_foundation.lookups import Lookups
from unihack.part4_enrichment_qa.confidence import build_enriched_record, review_queue
from unihack.part4_enrichment_qa.validation import (
    check_placeholders, check_char_limits, check_source_gaps,
)
from unihack.part4_enrichment_qa.evaluation import (
    classification_accuracy, char_limit_compliance, coverage,
)
from unihack.config import PLACEHOLDER_STRINGS


def _make_normalized_record(confidence=0.9, manufacturer="Frigidaire", desc_within_limit=True):
    row = RawInputRow(mfg_part_num="ABC", part_desc="test desc", part_manuf="frigidaire")
    classification = ClassificationResult(classpath="Faucets > Kitchen", confidence=confidence)
    attrs = [AttributeValue(attribute="Finish", value="Chrome", confidence=confidence, normalized_value="Chrome")]
    classified = ClassifiedRecord(input_row=row, classification=classification, attributes=attrs)
    normalized = NormalizedRecord(
        classified_record=classified,
        normalized_manufacturer=manufacturer,
        normalized_attributes=attrs,
        descriptions=[DescriptionField(field="Invoice Desc", value="X", char_count=1, within_limit=desc_within_limit)],
    )
    return normalized


def test_high_confidence_record_not_flagged():
    normalized = _make_normalized_record(confidence=0.9)
    enriched = build_enriched_record(normalized)
    assert enriched.needs_review is False


def test_low_confidence_record_flagged():
    normalized = _make_normalized_record(confidence=0.2)
    enriched = build_enriched_record(normalized)
    assert enriched.needs_review is True


def test_unmatched_manufacturer_flagged():
    normalized = _make_normalized_record(confidence=0.9, manufacturer=None)
    enriched = build_enriched_record(normalized)
    assert enriched.needs_review is True


def test_review_queue_sorted_lowest_first():
    low = build_enriched_record(_make_normalized_record(confidence=0.1))
    high = build_enriched_record(_make_normalized_record(confidence=0.9, manufacturer=None))
    # both need review (low conf, and no manufacturer) but should sort ascending
    queue = review_queue([high, low])
    assert queue[0].overall_confidence <= queue[1].overall_confidence


def test_check_placeholders_flags_slipped_through_value():
    normalized = _make_normalized_record()
    normalized.normalized_attributes[0].value = next(iter(PLACEHOLDER_STRINGS))
    enriched = build_enriched_record(normalized)
    violations = check_placeholders(enriched)
    assert any(v.type == "placeholder_detected" for v in violations)


def test_check_char_limits_flags_over_limit():
    normalized = _make_normalized_record(desc_within_limit=False)
    enriched = build_enriched_record(normalized)
    violations = check_char_limits(enriched)
    assert any(v.type == "char_limit_exceeded" for v in violations)


def test_check_source_gaps_flags_missing_manufacturer():
    normalized = _make_normalized_record(manufacturer=None)
    enriched = build_enriched_record(normalized)
    violations = check_source_gaps(enriched)
    assert any(v.type == "source_gap" and v.severity == "low" for v in violations)


def test_classification_accuracy():
    normalized = _make_normalized_record()
    enriched = build_enriched_record(normalized)
    acc = classification_accuracy([enriched], ["Faucets > Kitchen"])
    assert acc == 1.0
    acc_wrong = classification_accuracy([enriched], ["Faucets > Bath"])
    assert acc_wrong == 0.0


def test_char_limit_compliance_metric():
    good = build_enriched_record(_make_normalized_record(desc_within_limit=True))
    bad = build_enriched_record(_make_normalized_record(desc_within_limit=False))
    rate = char_limit_compliance([good, bad])
    assert rate == 0.5


def test_coverage_reports_both_numbers():
    r1 = build_enriched_record(_make_normalized_record(confidence=0.9))
    r2 = build_enriched_record(_make_normalized_record(confidence=0.1))
    processed_pct, flagged_pct = coverage([r1, r2], total_input_rows=4)
    assert processed_pct == 0.5
    assert flagged_pct == 0.5