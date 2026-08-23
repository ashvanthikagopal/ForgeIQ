"""
Part 4 - Programmatic validation and QA.
"""

from __future__ import annotations

from typing import Any, Iterable

from unihack.part1_foundation.placeholder_utils import (
    is_placeholder,
)


def validate_product(
    product: dict[str, Any],
    *,
    lov_values: dict[str, Iterable[str]] | None = None,
    char_limits: dict[str, int] | None = None,
    casing_rules: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """
    Validate a completed/enriched product.

    Returns a list of violations.
    """

    violations: list[dict[str, Any]] = []

    lov_values = lov_values or {}
    char_limits = char_limits or {}
    casing_rules = casing_rules or {}

    # ---------------------------------------------------------
    # Placeholder validation
    # ---------------------------------------------------------

    for field, value in product.items():

        if field.startswith("_") or isinstance(value, (dict, list)):
            continue

        if value is None or str(value).strip() == "":
            continue

        if is_placeholder(value):

            violations.append(
                {
                    "field": field,
                    "issue": "Placeholder value detected",
                    "severity": "high",
                    "type": "placeholder_detected",
                }
            )

    # ---------------------------------------------------------
    # LOV validation
    # ---------------------------------------------------------

    for field, allowed_values in lov_values.items():

        if field not in product:
            continue

        value = product[field]

        if value is None or str(value).strip() == "":
            continue

        allowed = {
            str(v).strip().lower()
            for v in allowed_values
        }

        if str(value).strip().lower() not in allowed:

            violations.append(
                {
                    "field": field,
                    "issue": "Value is not present in LOV",
                    "severity": "high",
                    "type": "lov_mismatch",
                    "value": value,
                }
            )

    # ---------------------------------------------------------
    # Character limits
    # ---------------------------------------------------------

    for field, limit in char_limits.items():

        if field not in product:
            continue

        value = product[field]

        if value is None:
            continue

        value = str(value)

        if len(value) > limit:

            violations.append(
                {
                    "field": field,
                    "issue": f"Character limit exceeded: {len(value)} > {limit}",
                    "severity": "high",
                    "type": "char_limit_exceeded",
                }
            )

    # ---------------------------------------------------------
    # Casing rules
    # ---------------------------------------------------------

    for field, rule in casing_rules.items():

        if field not in product:
            continue

        value = product[field]

        if not isinstance(value, str):
            continue

        if rule.lower() == "upper" and value != value.upper():

            violations.append(
                {
                    "field": field,
                    "issue": "Expected uppercase value",
                    "severity": "medium",
                    "type": "casing_violation",
                }
            )

        elif rule.lower() == "lower" and value != value.lower():

            violations.append(
                {
                    "field": field,
                    "issue": "Expected lowercase value",
                    "severity": "medium",
                    "type": "casing_violation",
                }
            )

    return violations