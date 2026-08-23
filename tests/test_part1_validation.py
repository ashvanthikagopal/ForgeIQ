from unihack.part1_foundation import (
    Part1Validator,
    load_part1_data,
)


def test_part1_validation():

    data = load_part1_data()

    validator = Part1Validator(
        data
    )

    results = validator.validate()

    assert len(results) > 0

    for result in results:

        assert result.passed, (
            f"{result.name}: "
            f"{result.message}"
        )


def test_actual_input_has_1000_rows():

    data = load_part1_data()

    assert (
        len(data.sample_input)
        == 1000
    )


def test_actual_input_has_six_columns():

    data = load_part1_data()

    assert (
        len(data.sample_input.columns)
        == 6
    )