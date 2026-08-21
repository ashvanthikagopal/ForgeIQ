from unihack.part1_foundation import (
    load_part1_data,
)

from unihack.part2_classification import (
    run_part2,
)


def test_part2_consumes_part1():

    part1_data = (
        load_part1_data()
    )

    results = run_part2(
        part1_data=part1_data,
        classpaths=[],
    )

    assert len(
        results
    ) == len(
        part1_data.sample_input
    )


def test_part2_requires_part1():

    try:

        run_part2(
            part1_data=None
        )

    except ValueError as exc:

        assert (
            "Part 1 data is required"
            in str(exc)
        )

    else:

        raise AssertionError(
            "Expected ValueError"
        )


def test_part2_flags_missing_lov():

    part1_data = (
        load_part1_data()
    )

    results = run_part2(
        part1_data=part1_data,
        classpaths=[],
    )

    assert len(
        results
    ) > 0

    first = results[0]

    assert (
        first.classpath
        == ""
    )

    assert (
        first.classification_confidence
        == 0.0
    )

    assert (
        first.needs_review
        is True
    )