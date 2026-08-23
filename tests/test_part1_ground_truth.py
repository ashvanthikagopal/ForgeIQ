from unihack.part1_foundation.data_loader import (
    load_part1_data,
)


def test_input_file_contains_1000_products():

    data = load_part1_data()

    assert (
        len(data.sample_input)
        == 1000
    )


def test_delivery_format_is_loaded():

    data = load_part1_data()

    # The uploaded Delivery Format file is
    # a separate reference dataset.
    #
    # It currently contains 2 records and
    # 252 columns.

    assert (
        len(data.delivery_format)
        > 0
    )

    assert (
        len(data.delivery_format.columns)
        > 0
    )


def test_delivery_format_contains_expected_columns():

    data = load_part1_data()

    required_columns = [
        "Mfg_Part_Num",
        "Part_Desc",
        "Part_Manuf",
    ]

    for column in required_columns:

        assert (
            column
            in data.delivery_format.columns
        )


def test_ground_truth_harness():

    data = load_part1_data()

    # The harness itself should be created
    # successfully even though the delivery
    # reference contains fewer records than
    # the 1000-item input dataset.

    assert (
        data.ground_truth is not None
    )

    assert (
        data.ground_truth.input_df is
        data.sample_input
    )

    assert (
        data.ground_truth.expected_df is
        data.delivery_format
    )


def test_ground_truth_compare_existing_record():

    data = load_part1_data()

    # Use an actual record that exists in
    # the delivery-format file.

    expected_row = (
        data.delivery_format
        .iloc[0]
    )

    part_number = (
        expected_row["Mfg_Part_Num"]
    )

    result = (
        data
        .ground_truth
        .compare_record(
            index=0,
            generated={
                "Mfg_Part_Num":
                    part_number
            },
        )
    )

    assert (
        result.total_fields
        == 1
    )

    assert (
        result.matched_fields
        == 1
    )

    assert (
        result.accuracy
        == 1.0
    )