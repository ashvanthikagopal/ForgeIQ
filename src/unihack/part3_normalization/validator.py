from __future__ import annotations

from dataclasses import dataclass

from .models import (
    DescriptionField,
    NormalizedProduct,
)


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class ValidationResult:

    field: str

    passed: bool

    message: str


# ============================================================
# DESCRIPTION VALIDATION
# ============================================================

def validate_description(
    field_name: str,
    field: DescriptionField,
) -> ValidationResult:

    if not field.within_limit:

        return ValidationResult(

            field=field_name,

            passed=False,

            message=(
                f"Character limit failed. "
                f"Count={field.char_count}"
            ),
        )

    if not field.casing_valid:

        return ValidationResult(

            field=field_name,

            passed=False,

            message=(
                "Casing validation failed."
            ),
        )

    return ValidationResult(

        field=field_name,

        passed=True,

        message="Valid",
    )


# ============================================================
# PRODUCT VALIDATION
# ============================================================

def validate_product(
    product: NormalizedProduct,
):

    results = []

    # --------------------------------------------------------
    # Attributes
    # --------------------------------------------------------

    for attribute in (
        product.attributes
    ):

        if attribute.needs_review:

            results.append(
                ValidationResult(

                    field=(
                        attribute.attribute
                    ),

                    passed=False,

                    message=(
                        attribute.review_reason
                        or
                        "Attribute requires review."
                    ),
                )
            )

    # --------------------------------------------------------
    # Existing review reasons
    # --------------------------------------------------------

    for reason in (
        product.review_reasons
    ):

        results.append(
            ValidationResult(

                field="product",

                passed=False,

                message=reason,
            )
        )

    return results


# ============================================================
# DESCRIPTION VALIDATION
# ============================================================

def validate_descriptions(
    descriptions: dict,
):

    results = []

    for name, field in (
        descriptions.items()
    ):

        if field is None:
            continue

        results.append(
            validate_description(
                name,
                field,
            )
        )

    return results


# ============================================================
# FINAL REVIEW FLAG
# ============================================================

def has_validation_failure(
    results,
) -> bool:

    return any(
        not result.passed
        for result in results
    )