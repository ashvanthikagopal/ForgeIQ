import pandas as pd

from unihack.part1_foundation.lookups import (
    ManufacturerBrandLookup,
    build_decimal_fraction_lookup,
    build_uom_lookup,
    build_lov_lookup,
)


def test_manufacturer_brand():

    df = pd.DataFrame([
        {
            "MANUFACTURER_NAME":
                "Test Manufacturer",

            "MANUFACTURER_CODE":
                "M001",

            "BRAND_NAME":
                "Test Brand",

            "BRAND_CODE":
                "B001",
        }
    ])

    lookup = (
        ManufacturerBrandLookup
        .from_dataframe(df)
    )

    result = (
        lookup
        .find_manufacturer(
            "Test Manufacturer"
        )
    )

    assert len(result) == 1

    assert (
        result[0]
        .brand_name
        == "Test Brand"
    )


def test_manufacturer_without_brand():

    df = pd.DataFrame([
        {
            "MANUFACTURER_NAME":
                "Test Manufacturer",

            "MANUFACTURER_CODE":
                "M001",

            "BRAND_NAME":
                None,

            "BRAND_CODE":
                "",
        }
    ])

    lookup = (
        ManufacturerBrandLookup
        .from_dataframe(df)
    )

    result = (
        lookup
        .find_manufacturer(
            "Test Manufacturer"
        )
    )

    assert len(result) == 1

    assert (
        result[0]
        .brand_name
        == "Test Manufacturer"
    )


def test_decimal_fraction():

    df = pd.DataFrame([
        [
            "1/4",
            0.25,
            "1/2",
            0.50,
        ]
    ])

    lookup = (
        build_decimal_fraction_lookup(
            df
        )
    )

    assert (
        lookup
        .decimal_to_fraction(
            0.25
        )
        == "1/4"
    )

    assert (
        lookup
        .fraction_to_decimal(
            "1/2"
        )
        == 0.5
    )


def test_uom():

    units = pd.DataFrame([
        {
            "Term": "inches",
            "Approved Abbreviation": "in",
            "Measurement Type": "Length",
        }
    ])

    house_style = pd.DataFrame([
        {
            "Rule":
                "Use space between number and unit"
        }
    ])

    lookup = build_uom_lookup(
        units,
        house_style,
    )

    assert (
        lookup
        .normalize_unit(
            "inches"
        )
        == "in"
    )


def test_lov():

    df = pd.DataFrame([
        {
            "Classpath":
                "Test > Faucets",

            "Attribute Label":
                "Finish",

            "Filtering Y/N":
                "Y",

            "Attribute Values":
                "Chrome|Brushed Nickel",

            "Normalized Values":
                "Chrome|Brushed Nickel",

            "Guidelines":
                "Use approved values",

            "Remarks":
                "",
        }
    ])

    lookup = build_lov_lookup(
        df
    )

    result = (
        lookup
        .get_attribute(
            "Test > Faucets",
            "Finish",
        )
    )

    assert result is not None

    assert (
        "Chrome"
        in result.allowed_values
    )