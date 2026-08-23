from unihack.part2_classification import (
    TaxonomyClassifier,
)


def test_classifier_uses_only_allowed_classpaths():

    classifier = TaxonomyClassifier(

        allowed_classpaths=[
            "Kitchen > Faucets",
            "Bathroom > Faucets",
        ]
    )

    result = classifier.classify(

        part_desc="Kitchen faucet",

        mpn="ABC123",

        manufacturer="Test Manufacturer",
    )

    assert result.classpath in {
        "",
        "Kitchen > Faucets",
        "Bathroom > Faucets",
    }


def test_classifier_requires_lov():

    classifier = TaxonomyClassifier(
        allowed_classpaths=[]
    )

    result = classifier.classify(

        part_desc="Kitchen faucet",

        mpn="ABC123",

        manufacturer="Test",
    )

    assert (
        result.classpath
        == ""
    )

    assert (
        result.confidence
        == 0.0
    )

    assert (
        result.needs_review
        is True
    )