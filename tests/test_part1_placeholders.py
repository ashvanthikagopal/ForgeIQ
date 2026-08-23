from unihack.part1_foundation.placeholder_utils import (
    clean_value,
    is_placeholder,
)


def test_unbranded():

    assert is_placeholder(
        "-- Unbranded --"
    )


def test_no_unilog_brand():

    assert is_placeholder(
        "-- No Unilog Brand --"
    )


def test_no_dib_brand():

    assert is_placeholder(
        "-- No DIB Brand --"
    )


def test_real_brand():

    assert not is_placeholder(
        "FRIGIDAIRE®"
    )


def test_placeholder_cleaning():

    assert (
        clean_value(
            "-- Unbranded --"
        )
        is None
    )


def test_real_value_cleaning():

    assert (
        clean_value(
            "  FRIGIDAIRE®  "
        )
        == "FRIGIDAIRE®"
    )