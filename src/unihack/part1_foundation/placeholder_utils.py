"""
Part 1 placeholder utilities.

Handles:
- known placeholders
- generic empty tokens
- placeholder-shaped strings
- dataframe cleaning
- record-level cleaning
- placeholder scanning/reporting
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Known placeholders
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

_PLACEHOLDER_PATTERN = re.compile(
    r"^\s*--.*--\s*$"
)

_DEFAULT_CLEAN_COLUMNS = {
    "unilog_brand",
    "dib_brand",
    "brand",
    "manufacturer",
    "part_manuf",
    "part_manufacturer",
}


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def _is_nan(value: Any) -> bool:
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _normalize(value: Any) -> Optional[str]:
    if value is None or _is_nan(value):
        return None

    if not isinstance(value, str):
        return None

    value = value.strip()

    if value == "":
        return ""

    return value.lower()


# ---------------------------------------------------------------------------
# Placeholder detection
# ---------------------------------------------------------------------------

def is_known_placeholder(value: Any) -> bool:
    """
    True only for known/canonical placeholder strings.

    Non-string values such as None, NaN and numbers are NOT considered
    known placeholders.
    """

    normalized = _normalize(value)

    if normalized is None or normalized == "":
        return False

    return normalized in KNOWN_PLACEHOLDERS


def is_placeholder_shaped(value: Any) -> bool:
    """
    Detect an unlisted '-- ... --' placeholder shape.

    Known placeholders are deliberately excluded so they are not counted
    twice.
    """

    if is_known_placeholder(value):
        return False

    normalized = _normalize(value)

    if normalized is None or normalized == "":
        return False

    return bool(
        _PLACEHOLDER_PATTERN.match(normalized)
    )


def is_generic_empty_token(value: Any) -> bool:
    """
    Detect generic empty/null tokens.

    Examples:
        "", "N/A", "NA", "None", "null", "-", "--", "TBD",
        "unknown", "#N/A", None, NaN
    """

    if value is None or _is_nan(value):
        return True

    if not isinstance(value, str):
        return False

    normalized = value.strip().lower()

    return normalized in {
        "",
        "n/a",
        "na",
        "none",
        "null",
        "-",
        "--",
        "tbd",
        "unknown",
        "#n/a",
    }


def is_placeholder(value: Any) -> bool:
    """
    Broad placeholder check.

    Used by downstream code when it wants to know whether something
    represents missing/fake data.
    """

    return (
        is_generic_empty_token(value)
        or is_known_placeholder(value)
        or is_placeholder_shaped(value)
    )


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_value(
    value: Any,
    treat_unlisted_shape_as_placeholder: bool = False,
):
    """
    Clean a single value.

    Known placeholders and generic empty tokens become None.

    Unlisted '-- ... --' values are preserved by default so that they can
    be reviewed rather than silently discarded.
    """

    if (
        is_generic_empty_token(value)
        or is_known_placeholder(value)
    ):
        return None

    if (
        treat_unlisted_shape_as_placeholder
        and is_placeholder_shaped(value)
    ):
        return None

    if isinstance(value, str):
        return value.strip()

    return value


def _should_clean_column(column: str) -> bool:
    normalized = column.strip().lower()
    return normalized in _DEFAULT_CLEAN_COLUMNS


def strip_placeholders(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
    report: bool = True,
    treat_unlisted_shape_as_placeholder: bool = False,
    add_flag_columns: bool = True,
) -> pd.DataFrame:
    """
    Return a cleaned copy of the dataframe.

    By default only brand/manufacturer-like columns are processed.
    """

    out = df.copy()

    if columns is None:
        cols = [
            col
            for col in out.columns
            if _should_clean_column(str(col))
        ]
    else:
        cols = list(columns)

    summary = {}

    for col in cols:
        if col not in out.columns:
            continue

        original = out[col]

        placeholder_mask = original.apply(
            lambda x: (
                is_known_placeholder(x)
                or is_generic_empty_token(x)
                or (
                    treat_unlisted_shape_as_placeholder
                    and is_placeholder_shaped(x)
                )
            )
        )

        count = int(placeholder_mask.sum())

        if count:
            summary[col] = count

        if add_flag_columns:
            out[f"{col}__was_placeholder"] = placeholder_mask

        out.loc[placeholder_mask, col] = pd.NA

    if report and summary:
        print(
            "[placeholder_utils] "
            "Stripped placeholder values:"
        )

        for col, count in sorted(
            summary.items(),
            key=lambda item: -item[1],
        ):
            print(
                f"  - {col}: {count} cell(s)"
            )

    return out


def strip_placeholders_from_record(
    record: dict[str, Any],
    fields: Optional[Iterable[str]] = None,
    treat_unlisted_shape_as_placeholder: bool = False,
) -> dict[str, Any]:
    """
    Clean a dictionary without mutating the original.
    """

    out = dict(record)

    if fields is None:
        target_fields = [
            key
            for key in out
            if _should_clean_column(str(key))
        ]
    else:
        target_fields = list(fields)

    for field in target_fields:
        if field not in out:
            continue

        out[field] = clean_value(
            out[field],
            treat_unlisted_shape_as_placeholder=(
                treat_unlisted_shape_as_placeholder
            ),
        )

    return out


# ---------------------------------------------------------------------------
# Scanning / reporting
# ---------------------------------------------------------------------------

@dataclass
class PlaceholderScan:
    column: str
    total_rows: int
    known_placeholder_count: int
    unlisted_placeholder_shape_count: int
    generic_empty_count: int
    unlisted_examples: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "total_rows": self.total_rows,
            "known_placeholder_count": (
                self.known_placeholder_count
            ),
            "unlisted_placeholder_shape_count": (
                self.unlisted_placeholder_shape_count
            ),
            "generic_empty_count": (
                self.generic_empty_count
            ),
            "unlisted_examples": (
                self.unlisted_examples
            ),
        }


def scan_column(
    series: pd.Series,
    column: str,
) -> PlaceholderScan:
    """
    Scan a column and classify values into three categories:

    1. Known '-- ... --' placeholders
    2. Unlisted '-- ... --' placeholder shapes
    3. Generic empty/null tokens

    Important:
    Bare values such as "N/A", "NA", "None", and "unknown"
    are counted as generic empty tokens during scanning, even though
    is_known_placeholder() intentionally recognizes some of them as
    known placeholders.
    """

    known_count = 0
    shape_count = 0
    generic_count = 0
    examples: list[str] = []

    for value in series:

        # ---------------------------------------------------------------
        # Generic empty values get priority during reporting.
        #
        # This means:
        #     "N/A"  -> generic
        #     None   -> generic
        #
        # while:
        #     "-- N/A --" -> known
        # ---------------------------------------------------------------
        if is_generic_empty_token(value):

            # A "-- ... --" value should not be treated as generic
            # when it is a known/unlisted placeholder-shaped value.
            if (
                isinstance(value, str)
                and is_placeholder_shaped(value)
            ):
                if is_known_placeholder(value):
                    known_count += 1
                else:
                    shape_count += 1

                    if value not in examples:
                        examples.append(value)

            else:
                generic_count += 1

            continue

        # ---------------------------------------------------------------
        # Known placeholder
        # ---------------------------------------------------------------
        if is_known_placeholder(value):
            known_count += 1
            continue

        # ---------------------------------------------------------------
        # Unlisted placeholder shape
        # ---------------------------------------------------------------
        if is_placeholder_shaped(value):
            shape_count += 1

            if (
                isinstance(value, str)
                and value not in examples
            ):
                examples.append(value)

            continue

    return PlaceholderScan(
        column=column,
        total_rows=len(series),
        known_placeholder_count=known_count,
        unlisted_placeholder_shape_count=shape_count,
        generic_empty_count=generic_count,
        unlisted_examples=examples,
    )


def summarize_placeholders(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Return a dataframe summarizing placeholder counts by column.
    """

    if columns is None:
        cols = [
            col
            for col in df.columns
            if _should_clean_column(str(col))
        ]
    else:
        cols = list(columns)

    rows = []

    for col in cols:

        if col not in df.columns:
            continue

        report = scan_column(
            df[col],
            str(col),
        )

        rows.append(
            {
                "column": report.column,
                "known_placeholder_count": (
                    report.known_placeholder_count
                ),
                "unlisted_placeholder_shape_count": (
                    report.unlisted_placeholder_shape_count
                ),
                "generic_empty_count": (
                    report.generic_empty_count
                ),
                "total_rows": report.total_rows,
            }
        )

    return pd.DataFrame(rows)


def placeholder_report(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Backward-compatible reporting function.
    """

    summary = summarize_placeholders(
        df,
        columns=columns,
    )

    if summary.empty:
        return summary

    summary = summary.copy()

    summary["placeholder_count"] = (
        summary["known_placeholder_count"]
        + summary["unlisted_placeholder_shape_count"]
        + summary["generic_empty_count"]
    )

    summary["pct_of_rows"] = summary.apply(
        lambda row: (
            100.0
            * row["placeholder_count"]
            / row["total_rows"]
            if row["total_rows"]
            else 0.0
        ),
        axis=1,
    )

    return summary.sort_values(
        "placeholder_count",
        ascending=False,
    ).reset_index(drop=True)