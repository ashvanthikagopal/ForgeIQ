from unihack.part2_classification import (
    LOVAttributeExtractor,
)


def test_attribute_extractor_without_lov():

    extractor = LOVAttributeExtractor(
        lov_lookup=None
    )

    result = extractor.extract(

        classpath="Kitchen > Faucets",

        part_desc=(
            "Stainless steel faucet"
        ),
    )

    assert result == []