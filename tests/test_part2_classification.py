from unihack.part2_classification.classify import (
    validate_classification,
)
from unihack.part2_classification.attributes import (
    validate_attribute,
)


def test_valid_classification():

    allowed = [
        "Kitchen > Faucets",
        "Kitchen > Sinks",
    ]

    result = validate_classification(
        {
            "classpath": "Kitchen > Faucets",
            "confidence": 0.95,
            "alternative_candidates": [],
            "reasoning": "Product is a faucet.",
        },
        allowed,
    )

    assert result.classpath == "Kitchen > Faucets"
    assert result.confidence == 0.95
    assert result.needs_review is False


def test_invalid_classification_is_rejected():

    allowed = [
        "Kitchen > Faucets",
        "Kitchen > Sinks",
    ]

    result = validate_classification(
        {
            "classpath": "Kitchen > Smart Products",
            "confidence": 0.99,
            "alternative_candidates": [],
            "reasoning": "Generated category.",
        },
        allowed,
    )

    assert result.classpath is None
    assert result.needs_review is True


def test_low_confidence_requires_review():

    allowed = [
        "Kitchen > Faucets",
    ]

    result = validate_classification(
        {
            "classpath": "Kitchen > Faucets",
            "confidence": 0.40,
            "alternative_candidates": [],
            "reasoning": "Ambiguous product.",
        },
        allowed,
    )

    assert result.needs_review is True


def test_valid_attribute():

    permitted = {
        "Material": [
            "Brass",
            "Stainless Steel",
        ]
    }

    result = validate_attribute(
        {
            "attribute": "Material",
            "value": "Brass",
            "confidence": 0.98,
            "needs_unit_normalization": False,
            "raw_text_span": "BRS",
        },
        permitted,
    )

    assert result is not None
    assert result.value == "Brass"
    assert result.needs_review is False


def test_invalid_attribute_is_rejected():

    permitted = {
        "Material": [
            "Brass",
            "Stainless Steel",
        ]
    }

    result = validate_attribute(
        {
            "attribute": "Material",
            "value": "Chrome Brass",
            "confidence": 0.98,
            "needs_unit_normalization": False,
            "raw_text_span": "chrome brass",
        },
        permitted,
    )

    assert result is not None
    assert result.needs_review is True


def test_unit_value_can_remain_raw():

    permitted = {
        "Width": []
    }

    result = validate_attribute(
        {
            "attribute": "Width",
            "value": "8.5 inches",
            "confidence": 0.96,
            "needs_unit_normalization": True,
            "raw_text_span": "8.5 inches",
        },
        permitted,
    )

    assert result is not None
    assert result.value == "8.5 inches"
    assert result.needs_unit_normalization is True