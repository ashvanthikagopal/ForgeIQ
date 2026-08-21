from __future__ import annotations

from typing import Any


def safe_text(value: Any) -> str:
    """
    Convert a value into a clean string.
    """

    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in {
        "",
        "nan",
        "none",
        "null",
    }:
        return ""

    return text


def adapt_part2_product(product):
    """
    Convert a Part 2 ProductEnrichmentPart2 object
    into a simple dictionary that Part 3 can consume.

    Part 3 receives its product information from Part 2.
    """

    if product is None:
        raise ValueError(
            "Part 2 product cannot be None."
        )

    return {
        "product_index": getattr(
            product,
            "product_index",
            None,
        ),

        "part_desc": safe_text(
            getattr(
                product,
                "part_desc",
                "",
            )
        ),

        "mpn": safe_text(
            getattr(
                product,
                "mpn",
                "",
            )
        ),

        "manufacturer": safe_text(
            getattr(
                product,
                "manufacturer",
                "",
            )
        ),

        "brand": safe_text(
            getattr(
                product,
                "brand",
                "",
            )
        ),

        "classpath": safe_text(
            getattr(
                product,
                "classpath",
                "",
            )
        ),

        "classification_confidence": float(
            getattr(
                product,
                "classification_confidence",
                0.0,
            )
            or 0.0
        ),

        "attributes": list(
            getattr(
                product,
                "attributes",
                []
            )
            or []
        ),

        "needs_review": bool(
            getattr(
                product,
                "needs_review",
                False,
            )
        ),

        "review_reasons": list(
            getattr(
                product,
                "review_reasons",
                []
            )
            or []
        ),
    }