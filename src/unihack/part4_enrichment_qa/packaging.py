"""
Part 4 - Final output packaging.
"""

from __future__ import annotations

from typing import Any


def package_product(
    product: dict[str, Any],
    violations: list[dict[str, Any]],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    """
    Create the final Part 4 output.
    """

    output = dict(product)

    output["part4_status"] = (
        "PASS"
        if evaluation.get("passes_qa")
        else "REVIEW"
    )

    output["part4_violations"] = violations

    output["part4_evaluation"] = evaluation

    output["part4_confidence"] = (
        product.get("_part4", {})
        .get("confidence", {})
    )

    output["part4_sources"] = (
        product.get("_part4", {})
        .get("source_records", [])
    )

    return output