from unihack.part3_normalization import (
    NormalizedAttribute,
    NormalizedProduct,
)

from unihack.part3_normalization.description_builder import (
    build_invoice_description,
    build_mobile_description,
    build_product_title,
)


def make_product():

    return NormalizedProduct(

        product_index=1,

        mpn="ABC123",

        manufacturer="Frigidaire",

        brand="Frigidaire",

        classpath=(
            "Kitchen > Dishwashers"
        ),

        classification_confidence=0.95,

        attributes=[

            NormalizedAttribute(

                attribute="Finish",

                raw_value="Stainless Steel",

                normalized_value=(
                    "Stainless Steel"
                ),

                confidence=0.95,
            )
        ],
    )


def test_invoice_description():

    result = (
        build_invoice_description(
            make_product()
        )
    )

    assert (
        result.value
        == result.value.upper()
    )

    assert (
        result.char_count
        <= 40
    )


def test_mobile_description():

    result = (
        build_mobile_description(
            make_product()
        )
    )

    assert (
        result.char_count
        == len(result.value)
    )


def test_product_title():

    result = (
        build_product_title(
            make_product()
        )
    )

    assert (
        "Frigidaire"
        in result.value
    )

    assert (
        "ABC123"
        in result.value
    )