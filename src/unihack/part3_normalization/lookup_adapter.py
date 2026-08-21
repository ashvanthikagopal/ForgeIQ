from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ============================================================
# PART 3 LOOKUPS
# ============================================================

@dataclass
class Part3Lookups:

    manufacturer_brand: Any = None

    uom: Any = None

    decimal_fraction: Any = None

    lov: Any = None


# ============================================================
# BUILD PART 3 LOOKUPS FROM PART 1
# ============================================================

def build_part3_lookups(
    part1_data,
) -> Part3Lookups:

    if part1_data is None:
        raise ValueError(
            "Part 1 data is required."
        )

    return Part3Lookups(

        manufacturer_brand=getattr(
            part1_data,
            "manufacturer_brand_lookup",
            None,
        ),

        uom=getattr(
            part1_data,
            "uom_lookup",
            None,
        ),

        decimal_fraction=getattr(
            part1_data,
            "decimal_fraction_lookup",
            None,
        ),

        lov=getattr(
            part1_data,
            "lov_lookup",
            None,
        ),
    )


# ============================================================
# MANUFACTURER LOOKUP
# ============================================================

def find_manufacturer(
    lookup,
    value: str,
):

    if lookup is None:
        return []

    method = getattr(
        lookup,
        "find_manufacturer",
        None,
    )

    if callable(method):
        return method(value) or []

    return []


# ============================================================
# BRAND LOOKUP
# ============================================================

def find_brand(
    lookup,
    value: str,
):

    if lookup is None:
        return []

    method = getattr(
        lookup,
        "find_brand",
        None,
    )

    if callable(method):
        return method(value) or []

    return []


# ============================================================
# UNIT NORMALIZATION
# ============================================================

def normalize_unit(
    lookup,
    unit: str,
):

    if lookup is None:
        return None

    # Try the expected Part 1 API.
    method = getattr(
        lookup,
        "normalize_unit",
        None,
    )

    if callable(method):
        return method(unit)

    # Try common alternative API names.
    for method_name in (
        "find_unit",
        "lookup_unit",
        "find",
    ):

        method = getattr(
            lookup,
            method_name,
            None,
        )

        if callable(method):

            try:
                result = method(unit)

                if result:
                    return result

            except (
                TypeError,
                KeyError,
                AttributeError,
            ):
                continue

    return None


# ============================================================
# DECIMAL → FRACTION
# ============================================================

def decimal_to_fraction(
    lookup,
    value: float,
):

    if lookup is None:
        return None

    # Expected API.
    method = getattr(
        lookup,
        "decimal_to_fraction",
        None,
    )

    if callable(method):

        return method(value)

    # Alternative possible API names.
    for method_name in (
        "convert",
        "lookup",
        "find",
    ):

        method = getattr(
            lookup,
            method_name,
            None,
        )

        if callable(method):

            try:

                result = method(value)

                if result is not None:
                    return result

            except (
                TypeError,
                KeyError,
                AttributeError,
            ):
                continue

    return None