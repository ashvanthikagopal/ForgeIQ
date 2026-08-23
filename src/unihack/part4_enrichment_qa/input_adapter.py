"""
Part 4 - Input adapter.

Converts the object produced by Part 3 (`ProductEnrichmentPart3`) into the
flat dict shape that `enrichment.py`, `validation.py`, `evaluation.py`, and
`packaging.py` already expect (e.g. `product["invoice_desc"]`,
`product.get("Mount Type")`, `product.items()` for placeholder scanning).

This mirrors the pattern Part 3 uses for its own Part 2 handoff
(`part3_normalization/input_adapter.py::adapt_part2_product`) -- same idea,
one stage later in the pipeline.

Part 3's fields are NOT flat dict values by default:
  - `product` is a `NormalizedProduct` (mpn/manufacturer/brand/classpath/attributes)
  - `invoice_desc`, `mobile_desc`, `product_title`, `long_description`,
    `marketing_copy` are each a `DescriptionField` (.value/.char_count/...)
  - `attributes` is a list of `NormalizedAttribute`, not a flat mapping

This adapter flattens all of that into one dict:
  - Content fields Part 4's validators actually check sit at the top level
    (`mpn`, `manufacturer`, `brand`, `classpath`, `invoice_desc`, `mobile_desc`,
    `product_title`, `long_description`, `marketing_copy`, and one key per
    normalized attribute name) so `char_limits`/`casing_rules`/`lov_values`/
    `required_attributes` can be keyed directly by those names, matching how
    Part 4 was already written.
  - Everything else (index, per-field confidence, Part 3's own review reasons,
    the un-flattened attribute detail) is preserved under `_part3_*` keys so
    nothing is lost, without polluting Part 4's placeholder/LOV/char-limit
    scans, which skip any field starting with `_`.

Accepts either a real `ProductEnrichmentPart3` object or an already-flat
dict (passed through unchanged) so existing callers of `run_part4` that
build their own dict keep working.
"""

from __future__ import annotations

from typing import Any


def _description_value(field: Any) -> str:
    """A DescriptionField's .value, or the field itself if it's already
    a plain string (covers dict-shaped or hand-built Part 3 output)."""

    if field is None:
        return ""

    value = getattr(field, "value", None)

    if value is not None:
        return value

    return str(field)


def _description_meta(field: Any) -> dict[str, Any]:
    if field is None:
        return {}

    return {
        "char_count": getattr(field, "char_count", None),
        "within_limit": getattr(field, "within_limit", None),
        "casing_valid": getattr(field, "casing_valid", None),
        "needs_review": getattr(field, "needs_review", None),
        "review_reason": getattr(field, "review_reason", None),
    }


def _flatten_attributes(attributes: Any) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """
    Returns (flat_values, detail) where:
      - flat_values:  {attribute_name: normalized_value}, used directly by
        `find_missing_attributes` / `validate_product`'s LOV check, since
        both key straight off attribute name (`product.get(attribute)`).
      - detail: the full per-attribute record (raw value, confidence,
        review flags) preserved for `_part3_attribute_detail`.
    """

    flat_values: dict[str, str] = {}
    detail: list[dict[str, Any]] = []

    for attribute in attributes or []:
        name = getattr(attribute, "attribute", None)
        normalized_value = getattr(attribute, "normalized_value", None)

        if name is None and isinstance(attribute, dict):
            name = attribute.get("attribute")
            normalized_value = attribute.get("normalized_value")

        if name is not None:
            flat_values[name] = normalized_value

        detail.append({
            "attribute": name,
            "raw_value": getattr(attribute, "raw_value", None),
            "normalized_value": normalized_value,
            "confidence": getattr(attribute, "confidence", None),
            "needs_review": getattr(attribute, "needs_review", False),
            "review_reason": getattr(attribute, "review_reason", None),
        })

    return flat_values, detail


def adapt_part3_output(part3_result: Any) -> dict[str, Any]:
    """
    Convert a Part 3 `ProductEnrichmentPart3` object into a flat dict
    Part 4 can consume.

    If `part3_result` is already a plain dict, it is returned unchanged --
    this keeps `run_part4` backward compatible with any caller that already
    builds the dict shape by hand.
    """

    if part3_result is None:
        raise ValueError("Part 3 output is required.")

    if isinstance(part3_result, dict):
        return part3_result

    normalized_product = getattr(part3_result, "product", None)

    flat_attributes, attribute_detail = _flatten_attributes(
        getattr(normalized_product, "attributes", []) if normalized_product is not None else []
    )

    adapted: dict[str, Any] = {
        # --- identity / classification fields Part 4 validates directly ---
        "mpn": getattr(normalized_product, "mpn", ""),
        "manufacturer": getattr(normalized_product, "manufacturer", ""),
        "brand": getattr(normalized_product, "brand", "") or getattr(normalized_product, "manufacturer", ""),
        "classpath": getattr(normalized_product, "classpath", ""),

        # --- description fields, unwrapped to plain strings ---
        "invoice_desc": _description_value(getattr(part3_result, "invoice_desc", None)),
        "mobile_desc": _description_value(getattr(part3_result, "mobile_desc", None)),
        "product_title": _description_value(getattr(part3_result, "product_title", None)),
        "long_description": _description_value(getattr(part3_result, "long_description", None)),
    }

    # marketing_copy is optional in Part 3 -- only add it if Part 3 actually
    # produced one, so an unrequested field doesn't get flagged as a
    # placeholder violation for being blank.
    marketing_copy = getattr(part3_result, "marketing_copy", None)
    if marketing_copy is not None:
        adapted["marketing_copy"] = _description_value(marketing_copy)

    # --- one top-level key per normalized attribute, e.g. "Mount Type" ---
    # This is what lets `required_attributes` / `lov_values` / char_limits
    # be keyed by attribute name, matching how enrichment.py/validation.py
    # already look things up (`product.get(attribute)`).
    adapted.update(flat_attributes)

    # --- bookkeeping, preserved but excluded from placeholder/LOV/char-limit
    # scans (validate_product skips any field starting with "_") ---
    adapted["_part3_product_index"] = getattr(normalized_product, "product_index", None)
    adapted["_part3_classification_confidence"] = getattr(normalized_product, "classification_confidence", None)
    adapted["_part3_needs_review"] = getattr(part3_result, "needs_review", False)
    adapted["_part3_review_reasons"] = list(getattr(part3_result, "review_reasons", []) or [])
    adapted["_part3_attribute_detail"] = attribute_detail
    adapted["_part3_description_meta"] = {
        "invoice_desc": _description_meta(getattr(part3_result, "invoice_desc", None)),
        "mobile_desc": _description_meta(getattr(part3_result, "mobile_desc", None)),
        "product_title": _description_meta(getattr(part3_result, "product_title", None)),
        "long_description": _description_meta(getattr(part3_result, "long_description", None)),
        "marketing_copy": _description_meta(marketing_copy),
    }

    return adapted
