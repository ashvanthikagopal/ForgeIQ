"""
Part 4 - Evaluation and quality metrics.
"""

from __future__ import annotations

from typing import Any


def evaluate_product(
    product: dict[str, Any],
    violations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate simple quality metrics for one product.
    """

    confidence_data = product.get(
        "_part4",
        {},
    ).get(
        "confidence",
        {},
    )

    confidence_scores = [
        float(item.get("score", 0.0))
        for item in confidence_data.values()
    ]

    average_confidence = (
        sum(confidence_scores) / len(confidence_scores)
        if confidence_scores
        else 1.0
    )

    high_severity = sum(
        1
        for violation in violations
        if violation.get("severity") == "high"
    )

    medium_severity = sum(
        1
        for violation in violations
        if violation.get("severity") == "medium"
    )

    return {
        "average_confidence": round(
            average_confidence,
            4,
        ),
        "violation_count": len(violations),
        "high_severity_violations": high_severity,
        "medium_severity_violations": medium_severity,
        "passes_qa": len(violations) == 0,
        "needs_review": (
            product.get("_part4", {})
            .get("needs_review", False)
            or len(violations) > 0
        ),
    }


def evaluate_batch(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Aggregate Part 4 results across multiple products.
    """

    if not results:
        return {
            "total_products": 0,
            "passed": 0,
            "failed": 0,
            "review_required": 0,
        }

    passed = sum(
        1
        for item in results
        if item.get("evaluation", {}).get("passes_qa")
    )

    review = sum(
        1
        for item in results
        if item.get("evaluation", {}).get("needs_review")
    )

    return {
        "total_products": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "review_required": review,
        "pass_rate": round(
            passed / len(results),
            4,
        ),
    }