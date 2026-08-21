from __future__ import annotations

from pathlib import Path

import pandas as pd


# ============================================================
# COMMON
# ============================================================

def verify_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Required file was not found:\n{path}"
        )


# ============================================================
# CSV
# ============================================================

def read_csv_file(
    path: Path,
) -> pd.DataFrame:

    verify_file(path)

    df = pd.read_csv(
        path
    )

    if df.empty:

        raise ValueError(
            f"CSV contains no rows:\n{path}"
        )

    return df


# ============================================================
# SAMPLE INPUT
# ============================================================

def parse_sample_input(
    path: Path,
) -> pd.DataFrame:

    df = read_csv_file(
        path
    )

    required_columns = [
        "Mfg_Part_Num",
        "Part_Desc",
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand",
        "Part_Manuf",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Sample input is missing "
            f"columns: {missing}\n"
            f"Available columns: "
            f"{list(df.columns)}"
        )

    return df


# ============================================================
# DELIVERY FORMAT
# ============================================================

def parse_delivery_format(
    path: Path,
) -> pd.DataFrame:

    df = read_csv_file(
        path
    )

    # These are the core fields that we know
    # should be present in the delivery file.
    required_columns = [
        "Mfg_Part_Num",
        "Part_Desc",
        "Part_Manuf",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Delivery format is missing "
            f"columns: {missing}\n"
            f"Available columns: "
            f"{list(df.columns)}"
        )

    return df


# ============================================================
# EXCEL
#
# These functions are for the lookup files required by
# Part 1 when they are available.
# ============================================================

def read_excel_file(
    path: Path,
    sheet_name=0,
    header=0,
) -> pd.DataFrame:

    verify_file(path)

    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=header,
    )


def get_sheet_names(
    path: Path,
) -> list[str]:

    verify_file(path)

    excel = pd.ExcelFile(
        path
    )

    return excel.sheet_names


# ============================================================
# MANUFACTURER / BRAND
# ============================================================

def parse_manufacturer_brand(
    path: Path,
) -> pd.DataFrame:

    return read_excel_file(
        path
    )


# ============================================================
# UOM
# ============================================================

def parse_uom(
    path: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:

    sheets = get_sheet_names(
        path
    )

    if len(sheets) < 2:

        raise ValueError(
            "UOM workbook should contain "
            "at least two sheets."
        )

    units_df = pd.read_excel(
        path,
        sheet_name=sheets[0],
    )

    house_style_df = pd.read_excel(
        path,
        sheet_name=sheets[1],
    )

    return (
        units_df,
        house_style_df,
    )


# ============================================================
# DECIMAL / FRACTION
# ============================================================

def parse_decimal_fraction(
    path: Path,
) -> pd.DataFrame:

    # The specification describes four side-by-side
    # Fraction | Decimal blocks.
    #
    # Therefore we intentionally don't assume a normal
    # one-row header.

    return pd.read_excel(
        path,
        header=None,
    )


# ============================================================
# LOV
# ============================================================

def parse_lov(
    path: Path,
) -> pd.DataFrame:

    return read_excel_file(
        path
    )


# ============================================================
# CATEGORY LOV
# ============================================================

def parse_all_sheets(
    path: Path,
) -> dict[str, pd.DataFrame]:

    sheets = get_sheet_names(
        path
    )

    result = {}

    for sheet in sheets:

        result[sheet] = pd.read_excel(
            path,
            sheet_name=sheet,
        )

    return result