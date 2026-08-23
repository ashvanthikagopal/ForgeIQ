from __future__ import annotations

from .input_adapter import (
    adapt_part2_product,
)

from .lookup_adapter import (
    Part3Lookups,
    build_part3_lookups,
)

from .normalize import (
    normalize_product,
)

from .description_builder import (
    build_descriptions,
)

from .validator import (
    validate_product,
    validate_descriptions,
)

from .models import (
    ProductEnrichmentPart3,
)


# ============================================================
# RUN PART 3 FOR ONE PRODUCT
# ============================================================

def run_part3(
    product,
    lookups: Part3Lookups,
    llm=None,
) -> ProductEnrichmentPart3:

    if product is None:

        raise ValueError(
            "Part 2 product is required."
        )

    if lookups is None:

        lookups = Part3Lookups()

    # ========================================================
    # 1. NORMALIZATION
    # ========================================================

    normalized_product = (
        normalize_product(
            product,
            lookups,
        )
    )

    # ========================================================
    # 2. DESCRIPTION BUILDING
    # ========================================================

    descriptions = (
        build_descriptions(
            normalized_product
        )
    )

    # ========================================================
    # 3. VALIDATION
    # ========================================================

    product_validation = (
        validate_product(
            normalized_product
        )
    )

    description_validation = (
        validate_descriptions(
            descriptions
        )
    )

    validation_results = (
        product_validation
        + description_validation
    )

    # ========================================================
    # 4. REVIEW REASONS
    # ========================================================

    review_reasons = list(
        normalized_product.review_reasons
    )

    for result in validation_results:

        if not result.passed:

            if result.message not in review_reasons:

                review_reasons.append(
                    result.message
                )

    # ========================================================
    # 5. FINAL RESULT
    # ========================================================

    return ProductEnrichmentPart3(

        product=normalized_product,

        invoice_desc=(
            descriptions[
                "invoice_desc"
            ]
        ),

        mobile_desc=(
            descriptions[
                "mobile_desc"
            ]
        ),

        product_title=(
            descriptions[
                "product_title"
            ]
        ),

        long_description=(
            descriptions[
                "long_description"
            ]
        ),

        marketing_copy=(
            descriptions[
                "marketing_copy"
            ]
        ),

        needs_review=(
            len(review_reasons) > 0
        ),

        review_reasons=review_reasons,
    )


# ============================================================
# RUN PART 3 FOR MULTIPLE PART 2 RESULTS
# ============================================================

def run_part3_batch(
    products,
    lookups: Part3Lookups,
    llm=None,
):

    if products is None:

        return []

    results = []

    for product in products:

        results.append(
            run_part3(
                product=product,

                lookups=lookups,

                llm=llm,
            )
        )

    return results


# ============================================================
# PART 2 → PART 3
# ============================================================

def run_part3_from_part2(
    part2_results,
    part1_data,
    llm=None,
):

    lookups = (
        build_part3_lookups(
            part1_data
        )
    )

    return run_part3_batch(

        products=part2_results,

        lookups=lookups,

        llm=llm,
    )


# ============================================================
# PART 1 → PART 2 → PART 3
#
# Convenience function for the complete pipeline.
# ============================================================

def run_part1_to_part3(
    part1_data,
    part2_results,
    llm=None,
):

    return run_part3_from_part2(

        part2_results=part2_results,

        part1_data=part1_data,

        llm=llm,
    )