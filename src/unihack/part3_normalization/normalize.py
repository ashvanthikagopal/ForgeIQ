from __future__ import annotations

import re
from fractions import Fraction

from .lookup_adapter import (
    find_manufacturer,
    find_brand,
    normalize_unit,
    decimal_to_fraction,
)

from .models import (
    ManufacturerBrandResult,
    NormalizedAttribute,
    NormalizedProduct,
)


# ============================================================
# CLEAN VALUE
# ============================================================

def clean_value(value) -> str:

    if value is None:
        return ""

    text = str(value).strip()

    placeholders = {
        "",
        "nan",
        "none",
        "null",
        "n/a",
        "na",
        "unknown",
        "-- unbranded --",
        "-- no unilog brand --",
        "-- no dib brand --",
    }

    if text.lower() in placeholders:
        return ""

    return text


# ============================================================
# MANUFACTURER / BRAND
# ============================================================

def normalize_manufacturer_brand(
    manufacturer: str,
    brand: str,
    lookup,
) -> ManufacturerBrandResult:

    raw_manufacturer = clean_value(
        manufacturer
    )

    raw_brand = clean_value(
        brand
    )

    # --------------------------------------------------------
    # Lookup unavailable
    # --------------------------------------------------------

    if lookup is None:

        return ManufacturerBrandResult(

            manufacturer=raw_manufacturer,

            brand=raw_brand,

            matched=False,

            needs_review=True,

            review_reason=(
                "Manufacturer/Brand lookup "
                "is unavailable."
            ),
        )

    # --------------------------------------------------------
    # Manufacturer lookup
    # --------------------------------------------------------

    manufacturer_matches = []

    if raw_manufacturer:

        manufacturer_matches = (
            find_manufacturer(
                lookup,
                raw_manufacturer,
            )
        )

    if manufacturer_matches:

        record = manufacturer_matches[0]

        canonical_manufacturer = clean_value(
            getattr(
                record,
                "manufacturer_name",
                raw_manufacturer,
            )
        )

        canonical_brand = clean_value(
            getattr(
                record,
                "brand_name",
                "",
            )
        )

        # Requirement:
        # If brand is missing, manufacturer can be
        # used as the fallback brand.

        if not canonical_brand:

            canonical_brand = (
                canonical_manufacturer
            )

        return ManufacturerBrandResult(

            manufacturer=(
                canonical_manufacturer
            ),

            brand=canonical_brand,

            manufacturer_code=clean_value(
                getattr(
                    record,
                    "manufacturer_code",
                    "",
                )
            ),

            brand_code=clean_value(
                getattr(
                    record,
                    "brand_code",
                    "",
                )
            ),

            matched=True,
        )

    # --------------------------------------------------------
    # Brand lookup
    # --------------------------------------------------------

    brand_matches = []

    if raw_brand:

        brand_matches = (
            find_brand(
                lookup,
                raw_brand,
            )
        )

    if brand_matches:

        record = brand_matches[0]

        canonical_manufacturer = clean_value(
            getattr(
                record,
                "manufacturer_name",
                raw_manufacturer,
            )
        )

        canonical_brand = clean_value(
            getattr(
                record,
                "brand_name",
                raw_brand,
            )
        )

        if not canonical_brand:

            canonical_brand = (
                canonical_manufacturer
            )

        return ManufacturerBrandResult(

            manufacturer=(
                canonical_manufacturer
            ),

            brand=canonical_brand,

            manufacturer_code=clean_value(
                getattr(
                    record,
                    "manufacturer_code",
                    "",
                )
            ),

            brand_code=clean_value(
                getattr(
                    record,
                    "brand_code",
                    "",
                )
            ),

            matched=True,
        )

    # --------------------------------------------------------
    # No match
    # --------------------------------------------------------

    return ManufacturerBrandResult(

        manufacturer=raw_manufacturer,

        brand=raw_brand,

        matched=False,

        needs_review=True,

        review_reason=(
            "Manufacturer/Brand could not "
            "be matched to the canonical lookup."
        ),
    )


# ============================================================
# MEASUREMENT PARSING
# ============================================================

MEASUREMENT_PATTERN = re.compile(
    r"^\s*"
    r"([-+]?\d+(?:\.\d+)?)"
    r"\s*"
    r"([A-Za-zµ°]+(?:\.)?)"
    r"\s*$"
)


def parse_measurement(
    value: str,
):
    match = MEASUREMENT_PATTERN.match(
        value
    )

    if not match:
        return None

    number_text = match.group(1)

    unit_text = match.group(2)

    try:

        number = float(
            number_text
        )

    except ValueError:

        return None

    return (
        number,
        number_text,
        unit_text,
    )


# ============================================================
# DECIMAL → FRACTION FALLBACK
# ============================================================

def fallback_decimal_to_fraction(
    number: float,
) -> str:

    if number.is_integer():

        return str(
            int(number)
        )

    fraction = Fraction(
        number
    ).limit_denominator(
        64
    )

    whole = (
        int(fraction.numerator // fraction.denominator)
    )

    remainder = (
        fraction.numerator
        % fraction.denominator
    )

    if whole > 0 and remainder > 0:

        return (
            f"{whole}-"
            f"{remainder}/"
            f"{fraction.denominator}"
        )

    if remainder == 0:

        return str(whole)

    return (
        f"{remainder}/"
        f"{fraction.denominator}"
    )


# ============================================================
# NORMALIZE UNIT VALUE
# ============================================================

def normalize_unit_value(
    raw_value: str,
    uom_lookup,
    decimal_fraction_lookup,
):
    value = clean_value(
        raw_value
    )

    if not value:

        return (
            "",
            False,
            None,
        )

    parsed = parse_measurement(
        value
    )

    if parsed is None:

        return (
            value,
            False,
            None,
        )

    number, number_text, unit_text = (
        parsed
    )

    # --------------------------------------------------------
    # UOM lookup unavailable
    # --------------------------------------------------------

    if uom_lookup is None:

        return (
            value,
            True,
            "UOM lookup is unavailable.",
        )

    # --------------------------------------------------------
    # Normalize unit
    # --------------------------------------------------------

    abbreviation = normalize_unit(
        uom_lookup,
        unit_text,
    )

    if not abbreviation:

        return (
            value,
            True,
            f"Unknown unit: {unit_text}",
        )

    abbreviation = str(
        abbreviation
    ).strip()

    # --------------------------------------------------------
    # Decimal → fraction
    #
    # The project specifically expects decimal/fraction
    # handling for applicable dimensions.
    # --------------------------------------------------------

    normalized_number = number_text

    inch_units = {
        "in",
        "inch",
        "inches",
        "in.",
        '"',
    }

    if (
        abbreviation.lower()
        in inch_units
    ):

        fraction = None

        if decimal_fraction_lookup is not None:

            fraction = decimal_to_fraction(
                decimal_fraction_lookup,
                number,
            )

        if fraction is None:

            fraction = (
                fallback_decimal_to_fraction(
                    number
                )
            )

        fraction = str(
            fraction
        ).strip()

        normalized_number = fraction

    # --------------------------------------------------------
    # Final value
    # --------------------------------------------------------

    normalized = (
        f"{normalized_number} "
        f"{abbreviation}"
    )

    return (
        normalized,
        False,
        None,
    )


# ============================================================
# NORMALIZE ATTRIBUTES
# ============================================================

def normalize_attributes(
    attributes,
    lookups,
):
    results = []

    for attribute in (
        attributes or []
    ):

        attribute_name = clean_value(
            getattr(
                attribute,
                "attribute",
                "",
            )
        )

        raw_value = clean_value(
            getattr(
                attribute,
                "value",
                "",
            )
        )

        confidence = float(
            getattr(
                attribute,
                "confidence",
                0.0,
            )
            or 0.0
        )

        needs_unit = bool(
            getattr(
                attribute,
                "needs_unit_normalization",
                False,
            )
        )

        # ----------------------------------------------------
        # Measurement
        # ----------------------------------------------------

        if needs_unit:

            (
                normalized_value,
                needs_review,
                review_reason,
            ) = normalize_unit_value(

                raw_value,

                lookups.uom,

                lookups.decimal_fraction,
            )

        # ----------------------------------------------------
        # Regular attribute
        # ----------------------------------------------------

        else:

            normalized_value = (
                raw_value
            )

            needs_review = False

            review_reason = None

        results.append(
            NormalizedAttribute(

                attribute=attribute_name,

                raw_value=raw_value,

                normalized_value=(
                    normalized_value
                ),

                confidence=confidence,

                needs_review=needs_review,

                review_reason=review_reason,
            )
        )

    return results


# ============================================================
# NORMALIZE COMPLETE PRODUCT
# ============================================================

def normalize_product(
    product,
    lookups,
) -> NormalizedProduct:

    manufacturer_result = (
        normalize_manufacturer_brand(

            manufacturer=getattr(
                product,
                "manufacturer",
                "",
            ),

            brand=getattr(
                product,
                "brand",
                "",
            ),

            lookup=(
                lookups.manufacturer_brand
            ),
        )
    )

    attributes = (
        normalize_attributes(
            getattr(
                product,
                "attributes",
                [],
            ),
            lookups,
        )
    )

    review_reasons = []

    # --------------------------------------------------------
    # Part 2 review flags
    # --------------------------------------------------------

    if getattr(
        product,
        "needs_review",
        False,
    ):

        review_reasons.extend(
            getattr(
                product,
                "review_reasons",
                [],
            )
            or []
        )

    # --------------------------------------------------------
    # Manufacturer / Brand
    # --------------------------------------------------------

    if manufacturer_result.needs_review:

        review_reasons.append(
            manufacturer_result.review_reason
            or
            "Manufacturer/Brand requires review."
        )

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    for attribute in attributes:

        if attribute.needs_review:

            review_reasons.append(
                f"{attribute.attribute}: "
                f"{attribute.review_reason}"
            )

    return NormalizedProduct(

        product_index=getattr(
            product,
            "product_index",
            None,
        ),

        mpn=clean_value(
            getattr(
                product,
                "mpn",
                "",
            )
        ),

        manufacturer=(
            manufacturer_result.manufacturer
        ),

        brand=(
            manufacturer_result.brand
        ),

        classpath=clean_value(
            getattr(
                product,
                "classpath",
                "",
            )
        ),

        classification_confidence=float(
            getattr(
                product,
                "classification_confidence",
                0.0,
            )
            or 0.0
        ),

        attributes=attributes,

        needs_review=(
            len(review_reasons) > 0
        ),

        review_reasons=review_reasons,
    )