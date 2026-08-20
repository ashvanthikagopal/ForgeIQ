"""
Part 4, Phase J (Day 11-12) — Packaging.

Helpers for the demo: walk one row end-to-end, narrating each stage, and
render the final evaluation summary. The actual demo script lives in
demo/run_demo.py — this module just holds reusable formatting helpers.
"""

from __future__ import annotations
from unihack.schemas import EnrichedRecord


def narrate_record(record: EnrichedRecord) -> str:
    """Produces the human-readable walkthrough: raw string -> classpath ->
    attributes -> normalization -> descriptions -> confidence flags."""
    r = record.normalized_record
    c = r.classified_record
    lines = [
        f"RAW INPUT:        {c.input_row.part_desc!r}",
        f"CLASSPATH:        {c.classification.classpath}  (confidence={c.classification.confidence:.2f})",
        f"MANUFACTURER:     {r.normalized_manufacturer or 'UNMATCHED'}",
        f"BRAND:            {r.normalized_brand or 'UNMATCHED'}",
        "ATTRIBUTES:",
    ]
    for a in r.normalized_attributes:
        flag = "  [NEEDS REVIEW]" if a.needs_review else ""
        lines.append(f"  - {a.attribute}: {a.normalized_value or a.value}{flag}")
    if record.enriched_attributes:
        lines.append("ENRICHED (Phase G, manufacturer-sourced):")
        for a in record.enriched_attributes:
            lines.append(f"  - {a.attribute}: {a.value}  (source: {a.source_url})")
    lines.append("DESCRIPTIONS:")
    for d in r.descriptions:
        ok = "OK" if d.within_limit else "OVER LIMIT"
        lines.append(f"  - {d.field} [{d.char_count} chars, {ok}]: {d.value}")
    lines.append(f"OVERALL CONFIDENCE: {record.overall_confidence:.2f}" if record.overall_confidence is not None else "OVERALL CONFIDENCE: n/a")
    lines.append(f"NEEDS REVIEW: {record.needs_review}")
    if record.violations:
        lines.append("QA VIOLATIONS:")
        for v in record.violations:
            lines.append(f"  - [{v.severity}] {v.type}: {v.field} — {v.issue}")
    return "\n".join(lines)


def scope_pitch_notes() -> str:
    """Boilerplate reminder for the pitch — fill in the specifics on the
    day, but keep this framing front and center."""
    return (
        "We scoped this to 2-3 pipeline stages, done convincingly, on one "
        "category (Faucets), rather than a shallow pass across all 8 stages "
        "and every category. What we did: classification + attribute "
        "extraction (Part 2), normalization + 5-format description building "
        "(Part 3), manufacturer-source enrichment as a proof-of-concept + "
        "confidence flagging + QA (Part 4). What we deliberately skipped: "
        "[fill in — e.g. digital assets, full de-dup at scale, live "
        "manufacturer-site retrieval] — and why."
    )