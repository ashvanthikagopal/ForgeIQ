from unihack.part2_classification import (
    AttributeResult,
    ClassificationResult,
    ProductEnrichmentPart2,
)


def test_classification_result():

    result = ClassificationResult(

        classpath="Kitchen > Faucets",

        confidence=0.95,
    )

    assert (
        result.classpath
        == "Kitchen > Faucets"
    )

    assert (
        result.confidence
        == 0.95
    )


def test_attribute_result():

    result = AttributeResult(

        attribute="Depth",

        value="50.25 inches",

        confidence=0.90,

        needs_unit_normalization=True,

        raw_text_span="50.25 inches",
    )

    assert (
        result.attribute
        == "Depth"
    )

    assert (
        result.needs_unit_normalization
        is True
    )