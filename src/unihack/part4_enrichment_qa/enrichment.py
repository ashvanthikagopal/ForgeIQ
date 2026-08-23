"""
Part 4 - Product enrichment.

Consumes a normalized Part 3 product and enriches only missing
attributes.

Manufacturer-source data must come from official manufacturer
content. Marketplace/distributor data must not be accepted.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional

from .confidence import calculate_confidence


OFFICIAL_SOURCE_TYPES = {
    "manufacturer_official",
    "manufacturer_documentation",
}


def _is_missing(value: Any) -> bool:
    if value is None:
        return True

    if isinstance(value, str):
        return value.strip() == ""

    return False


def _is_valid_source(source: dict[str, Any]) -> bool:
    source_type = str(
        source.get("source_type", "")
    ).strip().lower()

    return source_type in OFFICIAL_SOURCE_TYPES


def find_missing_attributes(
    product: dict[str, Any],
    required_attributes: Iterable[str],
) -> list[str]:
    """
    Find attributes that are still missing after Part 3.
    """

    missing = []

    for attribute in required_attributes:
        if _is_missing(product.get(attribute)):
            missing.append(attribute)

    return missing


def enrich_missing_attributes(
    product: dict[str, Any],
    required_attributes: Iterable[str],
    retrieved_sources: Optional[list[dict[str, Any]]] = None,
    llm_call: Optional[
        Callable[[str], dict[str, Any]]
    ] = None,
) -> dict[str, Any]:
    """
    Enrich missing fields in a Part 3 product.

    Parameters
    ----------
    product:
        Dictionary produced by Part 3.

    required_attributes:
        Attributes expected for this product/classpath.

    retrieved_sources:
        Manufacturer-source documents/chunks.

    llm_call:
        Optional LLM function.

    Returns
    -------
    dict
        Enriched product.
    """

    result = dict(product)

    required_attributes = list(required_attributes)

    missing = find_missing_attributes(
        result,
        required_attributes,
    )

    result["_part4"] = {
        "enriched_fields": [],
        "source_records": [],
        "confidence": {},
        "needs_review": False,
    }

    # Nothing missing
    if not missing:
        result["_part4"]["status"] = "no_enrichment_required"
        return result

    result["_part4"]["missing_before_enrichment"] = list(missing)

    # ---------------------------------------------------------
    # Filter only official manufacturer sources
    # ---------------------------------------------------------

    valid_sources = []

    for source in retrieved_sources or []:
        if _is_valid_source(source):
            valid_sources.append(source)

    # ---------------------------------------------------------
    # Build enrichment context
    # ---------------------------------------------------------

    if not valid_sources:
        result["_part4"]["status"] = "no_official_source_available"
        result["_part4"]["needs_review"] = True

        for field in missing:
            result["_part4"]["confidence"][field] = {
                "score": 0.0,
                "needs_review": True,
                "reason": "no_official_manufacturer_source",
            }

        return result

    source_text = "\n\n".join(
        str(source.get("content", ""))
        for source in valid_sources
    )

    # ---------------------------------------------------------
    # Optional LLM enrichment
    # ---------------------------------------------------------

    if llm_call is not None:

        prompt = f"""
You are enriching an industrial product record.

PRODUCT:
{result}

MISSING ATTRIBUTES:
{missing}

SOURCE CONTENT:
{source_text}

Rules:
1. Use ONLY the supplied manufacturer official source.
2. Do not invent values.
3. Do not use marketplace or distributor information.
4. If an attribute cannot be supported, omit it.
5. Return JSON only.

Expected format:
{{
    "attributes": [
        {{
            "attribute": "...",
            "value": "...",
            "source_url": "...",
            "confidence": 0.0
        }}
    ]
}}
"""

        generated = llm_call(prompt)

        attributes = generated.get(
            "attributes",
            [],
        )

        for item in attributes:

            field = item.get("attribute")
            value = item.get("value")

            if field not in missing:
                continue

            if _is_missing(value):
                continue

            result[field] = value

            confidence = calculate_confidence(
                value,
                source="manufacturer",
                lov_valid=True,
                manufacturer_matched=True,
            )

            result["_part4"]["confidence"][field] = (
                confidence.as_dict()
            )

            result["_part4"]["enriched_fields"].append(field)

            source_url = item.get("source_url")

            if source_url:
                result["_part4"]["source_records"].append(
                    {
                        "field": field,
                        "source_url": source_url,
                        "source_type": "manufacturer_official",
                    }
                )

    # ---------------------------------------------------------
    # Determine remaining missing fields
    # ---------------------------------------------------------

    remaining = find_missing_attributes(
        result,
        required_attributes,
    )

    result["_part4"]["missing_after_enrichment"] = remaining

    if remaining:
        result["_part4"]["needs_review"] = True

    result["_part4"]["status"] = (
        "enriched"
        if result["_part4"]["enriched_fields"]
        else "no_fields_enriched"
    )

    return result