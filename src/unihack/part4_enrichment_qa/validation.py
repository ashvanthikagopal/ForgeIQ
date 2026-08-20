"""
Part 4's QA pass — the last line of defense (rule #1). Checks a generated
record against Unilog's content rules before it is scored or shipped.
Runs both a programmatic pass (fast, deterministic, always run) and an
optional LLM-assisted pass (for judgment calls like casing nuance).
"""

from __future__ import annotations
import json
import logging

from unihack.schemas import EnrichedRecord, QAViolation
from unihack.config import PLACEHOLDER_STRINGS
from unihack.part4_enrichment_qa.prompts import (
    VALIDATION_SYSTEM_PROMPT,
    VALIDATION_USER_PROMPT,
)

log = logging.getLogger(__name__)


def check_placeholders(record: EnrichedRecord) -> list[QAViolation]:
    violations = []
    all_attrs = record.normalized_record.normalized_attributes + record.enriched_attributes
    for attr in all_attrs:
        if attr.value in PLACEHOLDER_STRINGS:
            violations.append(QAViolation(
                field=attr.attribute, issue=f"Placeholder value slipped through: {attr.value!r}",
                severity="high", type="placeholder_detected",
            ))
    return violations


def check_char_limits(record: EnrichedRecord) -> list[QAViolation]:
    violations = []
    for desc in record.normalized_record.descriptions:
        if not desc.within_limit:
            violations.append(QAViolation(
                field=desc.field, issue=f"{desc.char_count} chars exceeds limit",
                severity="high", type="char_limit_exceeded",
            ))
    return violations


def check_lov_compliance(record: EnrichedRecord, lov_lookup) -> list[QAViolation]:
    """`lov_lookup` is Part 1's Lookups instance — checks every attribute
    value is verbatim in that classpath's permitted values."""
    violations = []
    classpath = record.normalized_record.classified_record.classification.classpath
    permitted_df = lov_lookup.lov_for_classpath(classpath)
    all_attrs = record.normalized_record.normalized_attributes + record.enriched_attributes
    for attr in all_attrs:
        rows = permitted_df[permitted_df["Attribute Label"] == attr.attribute]
        if rows.empty:
            continue  # attribute not in LOV for this classpath — separate concern
        permitted_values = set(rows["Normalized Values"].dropna().tolist())
        value_to_check = attr.normalized_value or attr.value
        if permitted_values and value_to_check not in permitted_values:
            violations.append(QAViolation(
                field=attr.attribute, issue=f"Value {value_to_check!r} not in LOV permitted values",
                severity="high", type="lov_mismatch",
            ))
    return violations


def check_source_gaps(record: EnrichedRecord) -> list[QAViolation]:
    """Blank source data (UNSPSC, country-of-origin, etc.) is expected
    even in ground truth — flag as source_gap/low, not as an error."""
    violations = []
    if record.normalized_record.normalized_manufacturer is None:
        violations.append(QAViolation(
            field="manufacturer", issue="No manufacturer could be matched",
            severity="low", type="source_gap",
        ))
    return violations


def run_programmatic_qa(record: EnrichedRecord, lov_lookup) -> list[QAViolation]:
    violations = []
    violations += check_placeholders(record)
    violations += check_char_limits(record)
    violations += check_lov_compliance(record, lov_lookup)
    violations += check_source_gaps(record)
    return violations


def build_validation_prompt(record: EnrichedRecord, lookups) -> tuple[str, str]:
    """Optional LLM-assisted second pass for nuance the programmatic
    checks miss (e.g. casing edge cases). Programmatic checks above are
    the real gate — this is a supplement, not a replacement."""
    full_record_json = json.dumps({
        "classpath": record.normalized_record.classified_record.classification.classpath,
        "manufacturer": record.normalized_record.normalized_manufacturer,
        "brand": record.normalized_record.normalized_brand,
        "attributes": {a.attribute: (a.normalized_value or a.value)
                       for a in record.normalized_record.normalized_attributes},
        "descriptions": {d.field: d.value for d in record.normalized_record.descriptions},
    }, indent=2)

    user = VALIDATION_USER_PROMPT.format(
        full_generated_record_json=full_record_json,
        permitted_values_lookup="(see lov_lookup)",
        uom_rules="(see uom_lookup house-style rules)",
        manufacturer_brand_lookup="(see manufacturer_brand_lookup)",
        char_limits_per_field="Invoice<=40, Mobile=60-80, Title/Long=no hard limit",
        casing_rules_per_field="Invoice=ALL CAPS, Title=Title Case, Long=Sentence case",
    )
    return VALIDATION_SYSTEM_PROMPT, user


def parse_validation_response(raw_json: str) -> list[QAViolation]:
    data = json.loads(raw_json)
    return [QAViolation(**item) for item in data]