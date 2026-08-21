from unihack.part2_classification import (
    AttributeResult,
    ProductEnrichmentPart2,
)

from unihack.part3_normalization import (
    Part3Lookups,
    run_part3,
)


# ============================================================
# TEST 1
# ============================================================

def test_part3_normalization():

    product = ProductEnrichmentPart2(

        product_index=1,

        part_desc=(
            "Dishwasher 50.25 inches"
        ),

        mpn="ABC123",

        manufacturer="frigidaire",

        brand="",

        classpath=(
            "Kitchen > Dishwashers"
        ),

        classification_confidence=0.95,

        attributes=[

            AttributeResult(

                attribute="Depth",

                value="50.25 inches",

                confidence=0.95,

                needs_unit_normalization=True,

                raw_text_span=(
                    "50.25 inches"
                ),
            ),

            AttributeResult(

                attribute="Finish",

                value="Stainless Steel",

                confidence=0.95,

                needs_unit_normalization=False,

                raw_text_span=(
                    "Stainless Steel"
                ),
            ),
        ],
    )

    result = run_part3(

        product=product,

        lookups=Part3Lookups(),

        llm=None,
    )

    assert result is not None

    assert (
        result.product.mpn
        == "ABC123"
    )

    assert (
        result.product.classpath
        == "Kitchen > Dishwashers"
    )

    assert (
        result.product.attributes[0]
        .attribute
        == "Depth"
    )

    assert (
        result.product.attributes[0]
        .raw_value
        == "50.25 inches"
    )


# ============================================================
# TEST 2
# ============================================================

def test_unknown_unit_requires_review():

    product = ProductEnrichmentPart2(

        product_index=1,

        part_desc="Test",

        mpn="TEST001",

        manufacturer="Frigidaire",

        brand="",

        classpath=(
            "Kitchen > Dishwashers"
        ),

        classification_confidence=0.95,

        attributes=[

            AttributeResult(

                attribute="Depth",

                value="10 xyz",

                confidence=0.90,

                needs_unit_normalization=True,

                raw_text_span="10 xyz",
            )
        ],
    )

    result = run_part3(

        product=product,

        lookups=Part3Lookups(),

        llm=None,
    )

    assert result.needs_review is True