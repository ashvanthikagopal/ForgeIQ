from __future__ import annotations

import re

import pandas as pd


# ============================================================
# PLACEHOLDER VALUES
# ============================================================

PLACEHOLDER_VALUES = {
    "",
    "-",
    "--",
    "na",
    "n/a",
    "none",
    "null",
    "unknown",
    "not available",

    "-- unbranded --",
    "-- no unilog brand --",
    "-- no dib brand --",
}


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(value) -> str:
    """
    Convert a value to normalized text.

    NaN / None values become an empty string.
    """

    # Handle None
    if value is None:
        return ""

    # Handle pandas NaN / NaT
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    text = str(value)

    # Replace non-breaking spaces
    text = text.replace(
        "\u00a0",
        " ",
    )

    # Collapse multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# PLACEHOLDER CHECK
# ============================================================

def is_placeholder(value) -> bool:
    """
    Return True when the value is blank or
    represents a known placeholder.
    """

    text = clean_text(
        value
    )

    return (
        text.lower()
        in PLACEHOLDER_VALUES
    )


# ============================================================
# CLEAN VALUE
# ============================================================

def clean_value(value) -> str | None:
    """
    Convert blank/placeholder/NaN values to None.

    Real values are returned as cleaned strings.
    """

    text = clean_text(
        value
    )

    if not text:
        return None

    if is_placeholder(
        text
    ):
        return None

    return text