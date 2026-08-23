"""
test_harness.py
----------------
Loads the 200-item ground-truth file (Input sheet + Delivery Format sheet)
and exposes a reusable scoring function that Parts 2-4 call directly on
their generated records.

Design goals (per the project rules):
    - Never silently skip a gap in the ground truth itself (blank UNSPSC,
      blank country-of-origin, the known manufacturer/brand mismatch row).
      Surface these as `source_gap`, not as a scoring failure.
    - Field-by-field, not record-by-record: callers need per-field accuracy
      (classification, attribute precision/recall, description compliance)
      to build the Phase I evaluation numbers.
    - No dependency on any specific downstream pipeline shape -- callers pass
      a plain dict of `{field_name: value}` for their generated record and
      get back a structured score they can aggregate however they like.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

import pandas as pd

from .placeholder_utils import clean_value, is_placeholder as is_known_placeholder

# ---------------------------------------------------------------------------
# Config: sheet names / key columns as specified in the pack. Adjust here if
# the actual workbook uses slightly different sheet names -- keep it in one
# place rather than scattered through the codebase.
# ---------------------------------------------------------------------------
DEFAULT_INPUT_SHEET = "Input"
DEFAULT_DELIVERY_SHEET = "Delivery Format"

# Join key between the two sheets. SKU is specified as present on the Input
# sheet; fall back to Mfg_Part_Num if SKU isn't found.
DEFAULT_JOIN_KEYS = ("SKU", "Mfg_Part_Num", "MPN")

# Columns known (per the pack) to sometimes be legitimately blank in the
# ground truth itself -- these should never count as a pipeline error.
KNOWN_SOURCE_GAP_FIELDS = {
    "UNSPSC",
    "Country of Origin",
    "Country_of_Origin",
    "COO",
}


@dataclass
class GroundTruthRecord:
    """One row of ground truth: raw input fields + expected output fields."""

    key: str
    input_fields: dict[str, Any]
    expected_fields: dict[str, Any]
    known_gaps: set[str] = field(default_factory=set)
    known_issues: list[str] = field(default_factory=list)


@dataclass
class FieldScore:
    field: str
    expected: Any
    actual: Any
    match: bool
    is_source_gap: bool = False
    note: str = ""


@dataclass
class RecordScore:
    key: str
    field_scores: list[FieldScore]

    @property
    def scored_fields(self) -> list[FieldScore]:
        """Field scores excluding known source gaps (those don't count for/against)."""
        return [fs for fs in self.field_scores if not fs.is_source_gap]

    @property
    def accuracy(self) -> Optional[float]:
        scored = self.scored_fields
        if not scored:
            return None
        return sum(1 for fs in scored if fs.match) / len(scored)

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "accuracy": self.accuracy,
            "n_fields_scored": len(self.scored_fields),
            "n_source_gaps": len(self.field_scores) - len(self.scored_fields),
            "mismatches": [
                {"field": fs.field, "expected": fs.expected, "actual": fs.actual}
                for fs in self.scored_fields
                if not fs.match
            ],
        }


def _find_sheet(xls: pd.ExcelFile, preferred: str) -> str:
    """Case/whitespace-tolerant sheet-name lookup with a clear error if missing."""
    normalized = {s.strip().lower(): s for s in xls.sheet_names}
    key = preferred.strip().lower()
    if key in normalized:
        return normalized[key]
    # Loose contains-match fallback (e.g. "Delivery Format " or "DeliveryFormat")
    for s in xls.sheet_names:
        if key.replace(" ", "") in s.strip().lower().replace(" ", ""):
            return s
    raise ValueError(
        f"Could not find sheet matching '{preferred}'. "
        f"Available sheets: {xls.sheet_names}"
    )


def _find_join_column(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    cols_lower = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.strip().lower() in cols_lower:
            return cols_lower[cand.strip().lower()]
    raise ValueError(
        f"None of the candidate join keys {list(candidates)} found in columns: "
        f"{list(df.columns)}"
    )


def _row_known_gaps(row: pd.Series) -> set[str]:
    """
    Identify which known-gap fields are actually blank in this row, e.g. a
    blank UNSPSC or country-of-origin cell that's an accepted gap in the
    ground truth itself (per the pack notes), not a pipeline error.
    """
    gaps: set[str] = set()
    for col in row.index:
        if col in KNOWN_SOURCE_GAP_FIELDS:
            val = row[col]
            if pd.isna(val) or (isinstance(val, str) and not val.strip()):
                gaps.add(col)
    return gaps


def load_ground_truth(
    path: str | Path,
    input_sheet: str = DEFAULT_INPUT_SHEET,
    delivery_sheet: str = DEFAULT_DELIVERY_SHEET,
    join_keys: Iterable[str] = DEFAULT_JOIN_KEYS,
    strip_placeholders_in_fields: bool = True,
) -> list[GroundTruthRecord]:
    """
    Load the 200-item Input-vs-Output workbook into a list of
    GroundTruthRecord, one per row, joined on SKU/MPN.

    Does NOT assume row 1 is a clean header blindly -- pandas' default header
    inference is used but the result is sanity-checked (unnamed columns are
    flagged via a printed warning) since this pack is known to contain messy
    sheets elsewhere; the 200-item file itself is one of the cleaner ones but
    we don't special-case that assumption silently.
    """
    path = Path(path)
    xls = pd.ExcelFile(path)

    in_sheet_name = _find_sheet(xls, input_sheet)
    out_sheet_name = _find_sheet(xls, delivery_sheet)

    input_df = pd.read_excel(xls, sheet_name=in_sheet_name)
    output_df = pd.read_excel(xls, sheet_name=out_sheet_name)

    for name, df in (("Input", input_df), ("Delivery Format", output_df)):
        unnamed = [c for c in df.columns if str(c).lower().startswith("unnamed")]
        if unnamed:
            print(
                f"[test_harness] WARNING: sheet '{name}' has {len(unnamed)} "
                f"unnamed column(s) -- possible header/merged-cell issue: {unnamed}"
            )

    in_key_col = _find_join_column(input_df, join_keys)
    out_key_col = _find_join_column(output_df, join_keys)

    input_df = input_df.set_index(input_df[in_key_col].astype(str))
    output_df = output_df.set_index(output_df[out_key_col].astype(str))

    records: list[GroundTruthRecord] = []
    missing_in_output = []
    for key, in_row in input_df.iterrows():
        if key not in output_df.index:
            missing_in_output.append(key)
            continue
        out_row = output_df.loc[key]
        # .loc can return a DataFrame if the key isn't unique -- guard it.
        if isinstance(out_row, pd.DataFrame):
            out_row = out_row.iloc[0]

        input_fields = in_row.to_dict()
        expected_fields = out_row.to_dict()

        if strip_placeholders_in_fields:
            for fields_dict in (input_fields, expected_fields):
                for k, v in list(fields_dict.items()):
                    if isinstance(v, str) and is_known_placeholder(v):
                        fields_dict[k] = clean_value(v)

        known_issues = []
        gaps = _row_known_gaps(out_row)
        if gaps:
            known_issues.append(f"source_gap in: {sorted(gaps)}")

        records.append(
            GroundTruthRecord(
                key=str(key),
                input_fields=input_fields,
                expected_fields=expected_fields,
                known_gaps=gaps,
                known_issues=known_issues,
            )
        )

    if missing_in_output:
        print(
            f"[test_harness] WARNING: {len(missing_in_output)} key(s) present in "
            f"Input but not found in Delivery Format: {missing_in_output[:10]}"
            f"{'...' if len(missing_in_output) > 10 else ''}"
        )

    return records


def _default_field_comparator(expected: Any, actual: Any) -> bool:
    """
    Exact-match comparator, normalized for whitespace/case-insensitivity on
    strings and NaN-safe on missing values. Callers needing fuzzy/numeric
    tolerance (e.g. char-limit compliance, not exact string match) should
    pass their own `field_comparators` into TestHarness.score_record.
    """
    if pd.isna(expected) and pd.isna(actual):
        return True
    if pd.isna(expected) or pd.isna(actual):
        return False
    if isinstance(expected, str) and isinstance(actual, str):
        return expected.strip().lower() == actual.strip().lower()
    return expected == actual


class TestHarness:
    """
    Reusable scorer, built once from the 200-item ground truth, called
    repeatedly by Parts 2-4 on their generated records.

    Usage
    -----
        harness = TestHarness(load_ground_truth("Unilog-Sample_200_Items-Input-vs-Output.xlsx"))

        generated = {"Classpath": "...", "Product Title": "...", ...}
        score = harness.score_record(key="12345", generated_fields=generated)
        print(score.accuracy, score.as_dict())

        # Aggregate across all records a stage has processed:
        summary = harness.aggregate(all_scores)
    """

    def __init__(self, records: list[GroundTruthRecord]):
        self._by_key: dict[str, GroundTruthRecord] = {r.key: r for r in records}

    def __len__(self) -> int:
        return len(self._by_key)

    def get(self, key: str) -> Optional[GroundTruthRecord]:
        return self._by_key.get(str(key))

    def keys(self) -> list[str]:
        return list(self._by_key.keys())

    def score_record(
        self,
        key: str,
        generated_fields: dict[str, Any],
        fields_to_score: Optional[Iterable[str]] = None,
        field_comparators: Optional[dict[str, Callable[[Any, Any], bool]]] = None,
    ) -> RecordScore:
        """
        Compare a generated record's fields against ground truth for `key`.

        Parameters
        ----------
        key:
            SKU / MPN identifying the ground-truth row.
        generated_fields:
            The pipeline's output for this record, e.g.
            {"Classpath": "...", "Product Title": "...", "Attribute:Series": "..."}.
        fields_to_score:
            Restrict scoring to these field names (e.g. just "Classpath" for
            Part 2's classification-only scoring). Defaults to the
            intersection of generated_fields keys and expected_fields keys.
        field_comparators:
            Optional per-field custom comparator, e.g.
            {"Product Title": my_char_limit_aware_comparator}. Falls back to
            `_default_field_comparator` for any field not listed here.
        """
        record = self._by_key.get(str(key))
        if record is None:
            raise KeyError(f"No ground-truth record for key={key!r}")

        comparators = field_comparators or {}
        target_fields = (
            list(fields_to_score)
            if fields_to_score is not None
            else [f for f in generated_fields.keys() if f in record.expected_fields]
        )

        field_scores: list[FieldScore] = []
        for f in target_fields:
            expected = record.expected_fields.get(f)
            actual = generated_fields.get(f)
            is_gap = f in record.known_gaps

            if is_gap:
                field_scores.append(
                    FieldScore(
                        field=f,
                        expected=expected,
                        actual=actual,
                        match=True,  # doesn't count against the score
                        is_source_gap=True,
                        note="source_gap: blank in ground truth itself",
                    )
                )
                continue

            comparator = comparators.get(f, _default_field_comparator)
            match = comparator(expected, actual)
            field_scores.append(
                FieldScore(field=f, expected=expected, actual=actual, match=match)
            )

        return RecordScore(key=str(key), field_scores=field_scores)

    def score_batch(
        self,
        generated_by_key: dict[str, dict[str, Any]],
        fields_to_score: Optional[Iterable[str]] = None,
        field_comparators: Optional[dict[str, Callable[[Any, Any], bool]]] = None,
    ) -> list[RecordScore]:
        """Score many records at once. Keys not found in ground truth are skipped with a warning."""
        scores = []
        for key, generated_fields in generated_by_key.items():
            if str(key) not in self._by_key:
                print(f"[test_harness] WARNING: skipping unknown key={key!r} (not in ground truth)")
                continue
            scores.append(
                self.score_record(key, generated_fields, fields_to_score, field_comparators)
            )
        return scores

    @staticmethod
    def aggregate(scores: list[RecordScore]) -> dict[str, Any]:
        """
        Roll up a list of RecordScore into the headline numbers for Phase I
        evaluation: overall accuracy, per-field accuracy, coverage, and a
        list of the worst-scoring records for manual inspection.
        """
        if not scores:
            return {
                "n_records": 0,
                "overall_accuracy": None,
                "per_field_accuracy": {},
                "worst_records": [],
            }

        per_field_hits: dict[str, list[bool]] = {}
        record_accuracies: list[float] = []

        for rs in scores:
            acc = rs.accuracy
            if acc is not None:
                record_accuracies.append(acc)
            for fs in rs.scored_fields:
                per_field_hits.setdefault(fs.field, []).append(fs.match)

        per_field_accuracy = {
            field_name: (sum(hits) / len(hits) if hits else None)
            for field_name, hits in per_field_hits.items()
        }

        worst = sorted(
            (rs for rs in scores if rs.accuracy is not None),
            key=lambda rs: rs.accuracy,
        )[:10]

        return {
            "n_records": len(scores),
            "overall_accuracy": (
                sum(record_accuracies) / len(record_accuracies)
                if record_accuracies
                else None
            ),
            "per_field_accuracy": per_field_accuracy,
            "worst_records": [rs.as_dict() for rs in worst],
        }

    def known_issues_report(self) -> pd.DataFrame:
        """
        Surface the ground truth's own imperfections (blank UNSPSC/COO,
        flagged mismatches) as a dataframe -- for the "say when data is
        imperfect, don't hide it" deliverable, and to sanity-check that the
        harness itself found the expected known gaps.
        """
        rows = [
            {"key": r.key, "known_gaps": sorted(r.known_gaps), "issues": r.known_issues}
            for r in self._by_key.values()
            if r.known_gaps or r.known_issues
        ]
        return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_harness.py <path_to_200_item_workbook.xlsx>")
        sys.exit(1)

    gt_records = load_ground_truth(sys.argv[1])
    harness = TestHarness(gt_records)
    print(f"Loaded {len(harness)} ground-truth records.")
    print("\nKnown gaps / issues sample:")
    print(harness.known_issues_report().head(10))
