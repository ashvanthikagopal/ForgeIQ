"""
placeholder_utils.py
Part 1 — Setup & Data Foundation

Utilities for detecting and stripping "fake data" placeholder strings that
appear throughout the Unilog source files (e.g. "-- Unbranded --"). These
values are NOT real data — they mean the field is empty — and must never
reach downstream matching, classification, or generation logic.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Canonical placeholder strings observed in the pack, plus a couple of
# defensive variants (case/whitespace) that tend to sneak into messy exports.
# ---------------------------------------------------------------------------
KNOWN_PLACEHOLDERS = {
    "-- unbranded --",
    "-- no unilog brand --",
    "-- no dib brand --",
    "-- no brand --",
    "-- none --",
    "-- n/a --",
    "n/a",
    "na",
    "none",
    "unknown",
    "unbranded",
    "not applicable",
}

# Generic pattern: anything that looks like "-- ... --" is treated as a
# placeholder even if we haven't seen the exact string before. This is
# deliberately broad because new placeholder variants show up in raw
# supplier feeds that aren't in the 9 reference files.
_PLACEHOLDER_PATTERN = re.compile(r"^\s*--.*--\s*$")


def _normalize_for_check(value: Any) -> Optional[str]:
    """Lowercase/trim a value for placeholder comparison. Returns None if
    the value isn't a comparable string (e.g. actual NaN, None, numbers)."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    if s == "":
        return None
    return s.lower()


def is_placeholder(value: Any) -> bool:
    """Return True if `value` is empty, NaN, or a known/likely placeholder
    string like '-- Unbranded --'."""
    normalized = _normalize_for_check(value)
    if normalized is None:
        return True  # empty / NaN counts as "not real data"
    if normalized in KNOWN_PLACEHOLDERS:
        return True
    if _PLACEHOLDER_PATTERN.match(normalized):
        return True
    return False


def clean_value(value: Any) -> Optional[str]:
    """Return the stripped string value, or None if it's a placeholder."""
    if is_placeholder(value):
        return None
    return str(value).strip()


def strip_placeholders(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
    report: bool = True,
) -> pd.DataFrame:
    """
    Replace placeholder values with real NaN across `columns` (default: all
    object/string columns). Returns a NEW dataframe — never mutates in
    place, so callers can compare before/after for the "say when data is
    imperfect" reporting requirement.

    If report=True, prints a short per-column summary of how many
    placeholder cells were found — useful evidence for judges (Phase H).
    """
    out = df.copy()
    cols = list(columns) if columns is not None else list(
        out.select_dtypes(include=["object"]).columns
    )

    summary = {}
    for col in cols:
        if col not in out.columns:
            continue
        mask = out[col].apply(is_placeholder)
        # Don't blow away genuinely-empty cells that were already NaN;
        # we only care about reporting the *string* placeholders here.
        was_string_placeholder = mask & out[col].apply(
            lambda v: isinstance(v, str) and v.strip() != ""
        )
        n = int(was_string_placeholder.sum())
        if n:
            summary[col] = n
        out.loc[mask, col] = pd.NA

    if report and summary:
        print("[placeholder_utils] Stripped placeholder values:")
        for col, n in sorted(summary.items(), key=lambda kv: -kv[1]):
            print(f"  - {col}: {n} cell(s)")

    return out


def placeholder_report(
    df: pd.DataFrame, columns: Optional[Iterable[str]] = None
) -> pd.DataFrame:
    """
    Non-destructive audit: returns a small dataframe of
    [column, placeholder_count, pct_of_rows] WITHOUT modifying `df`.
    Use this in the test harness / evaluation stage (Phase I) to show
    coverage gaps honestly rather than silently dropping rows.
    """
    cols = list(columns) if columns is not None else list(
        df.select_dtypes(include=["object"]).columns
    )
    rows = []
    n_rows = len(df)
    for col in cols:
        if col not in df.columns:
            continue
        n_placeholder = int(df[col].apply(is_placeholder).sum())
        rows.append(
            {
                "column": col,
                "placeholder_count": n_placeholder,
                "pct_of_rows": round(100 * n_placeholder / n_rows, 1) if n_rows else 0.0,
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values("placeholder_count", ascending=False)
        .reset_index(drop=True)
    )
