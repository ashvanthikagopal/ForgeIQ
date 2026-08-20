"""
Part 4, Phase I (Day 10-11) — Evaluation.

Collects metrics from Parts 2 and 3, plus Part 4's own, into one summary
table. Report both precision AND recall, report coverage as processed vs
flagged (not just the processed %), and never cherry-pick a single
favorable number.
"""

from __future__ import annotations
import time
from dataclasses import asdict

from unihack.schemas import EvaluationMetrics, EnrichedRecord


def classification_accuracy(records: list[EnrichedRecord], ground_truth_classpaths: list[str]) -> float:
    assert len(records) == len(ground_truth_classpaths)
    correct = sum(
        r.normalized_record.classified_record.classification.classpath == gt
        for r, gt in zip(records, ground_truth_classpaths)
    )
    return correct / len(records) if records else 0.0


def attribute_precision_recall(
    records: list[EnrichedRecord],
    ground_truth_attrs: list[dict[str, str]],
) -> tuple[float, float]:
    """ground_truth_attrs[i] = {attribute_name: expected_value} for row i."""
    tp = fp = fn = 0
    for record, gt in zip(records, ground_truth_attrs):
        predicted = {
            a.attribute: (a.normalized_value or a.value)
            for a in record.normalized_record.normalized_attributes
        }
        for attr, expected in gt.items():
            if attr in predicted:
                if predicted[attr] == expected:
                    tp += 1
                else:
                    fp += 1
                    fn += 1
            else:
                fn += 1
        for attr in predicted:
            if attr not in gt:
                fp += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return precision, recall


def lov_compliance_rate(records: list[EnrichedRecord]) -> float:
    total = flagged_mismatch = 0
    for r in records:
        for v in r.violations:
            total += 1
            if v.type == "lov_mismatch":
                flagged_mismatch += 1
    if total == 0:
        return 1.0
    return 1 - (flagged_mismatch / total)


def manufacturer_match_rate(records: list[EnrichedRecord]) -> float:
    known_brand_rows = [r for r in records if r.normalized_record.classified_record.input_row.part_manuf]
    if not known_brand_rows:
        return 1.0
    matched = sum(1 for r in known_brand_rows if r.normalized_record.normalized_manufacturer is not None)
    return matched / len(known_brand_rows)


def char_limit_compliance(records: list[EnrichedRecord]) -> float:
    all_descs = [d for r in records for d in r.normalized_record.descriptions]
    if not all_descs:
        return 1.0
    return sum(d.within_limit for d in all_descs) / len(all_descs)


def coverage(records: list[EnrichedRecord], total_input_rows: int) -> tuple[float, float]:
    processed_pct = len(records) / total_input_rows if total_input_rows else 0.0
    flagged_pct = sum(r.needs_review for r in records) / len(records) if records else 0.0
    return processed_pct, flagged_pct


class Timer:
    """Wrap the per-item pipeline call with this to get avg_time_per_item_sec
    for the scalability story ("1,000 rows in X minutes")."""
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self._start


def build_summary_table(metrics: EvaluationMetrics) -> str:
    """Markdown table for the demo/pitch slide."""
    rows = asdict(metrics)
    lines = ["| Metric | Value |", "|---|---|"]
    for k, v in rows.items():
        display = f"{v:.1%}" if isinstance(v, float) and "pct" in k or "rate" in k or "accuracy" in k or "compliance" in k or "recall" in k or "precision" in k else v
        lines.append(f"| {k} | {display} |")
    return "\n".join(lines)