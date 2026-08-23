from unihack.part1_foundation.data_loader import (
    load_part1_data,
)


def test_input_file():

    data = load_part1_data()

    assert len(
        data.sample_input
    ) == 1000

    expected_columns = [
        "Mfg_Part_Num",
        "Part_Desc",
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand",
        "Part_Manuf",
    ]

    assert list(
        data.sample_input.columns
    ) == expected_columns