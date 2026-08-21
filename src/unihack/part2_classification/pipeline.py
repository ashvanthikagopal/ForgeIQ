from __future__ import annotations

from .classifier import (
    TaxonomyClassifier,
)

from .attribute_extractor import (
    LOVAttributeExtractor,
)

from .models import (
    ProductEnrichmentPart2,
)


def run_part2(
    part1_data,
    classpaths: list[str] | None = None,
):
    """
    Part 2 consumes Part 1 data.

    It does NOT reload the CSV.
    """

    # ========================================================
    # VALIDATE PART 1
    # ========================================================

    if part1_data is None:

        raise ValueError(
            "Part 1 data is required."
        )

    if (
        not hasattr(
            part1_data,
            "sample_input",
        )
    ):

        raise TypeError(
            "run_part2() expects Part1Data."
        )

    input_df = (
        part1_data.sample_input
    )

    # ========================================================
    # CLASSIFIER
    # ========================================================

    classifier = TaxonomyClassifier(
        allowed_classpaths=classpaths
    )

    # ========================================================
    # ATTRIBUTE EXTRACTOR
    # ========================================================

    attribute_extractor = None

    if (
        part1_data.lov_lookup
        is not None
    ):

        attribute_extractor = (
            LOVAttributeExtractor(
                part1_data.lov_lookup
            )
        )

    results = []

    # ========================================================
    # PROCESS INPUT
    # ========================================================

    for index, row in (
        input_df.iterrows()
    ):

        # ----------------------------------------------------
        # Read Part 1 fields
        # ----------------------------------------------------

        part_desc = str(
            row.get(
                "Part_Desc",
                "",
            )
        )

        mpn = str(
            row.get(
                "Mfg_Part_Num",
                "",
            )
        )

        manufacturer = str(
            row.get(
                "Part_Manuf",
                "",
            )
        )

        brand = str(
            row.get(
                "Unilog_Brand",
                "",
            )
        )

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        classification = (
            classifier.classify(
                part_desc=part_desc,
                mpn=mpn,
                manufacturer=manufacturer,
            )
        )

        # ----------------------------------------------------
        # Attributes
        # ----------------------------------------------------

        attributes = []

        if (
            attribute_extractor
            is not None
            and classification.classpath
        ):

            attributes = (
                attribute_extractor.extract(
                    classpath=(
                        classification.classpath
                    ),
                    part_desc=part_desc,
                )
            )

        # ----------------------------------------------------
        # Review reasons
        # ----------------------------------------------------

        review_reasons = []

        if classification.needs_review:

            review_reasons.append(
                classification.review_reason
                or
                "Classification requires review."
            )

        if not classification.classpath:

            review_reasons.append(
                "No Classpath assigned."
            )

        # ----------------------------------------------------
        # Create Part 2 result
        # ----------------------------------------------------

        result = ProductEnrichmentPart2(

            product_index=index,

            part_desc=part_desc,

            mpn=mpn,

            manufacturer=manufacturer,

            brand=brand,

            classpath=(
                classification.classpath
            ),

            classification_confidence=(
                classification.confidence
            ),

            attributes=attributes,

            needs_review=(
                len(review_reasons) > 0
            ),

            review_reasons=(
                review_reasons
            ),
        )

        results.append(
            result
        )

    return results