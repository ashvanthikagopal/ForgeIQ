from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .placeholder_utils import (
    clean_value,
)


# ============================================================
# MANUFACTURER / BRAND
# ============================================================

@dataclass
class ManufacturerBrandRecord:

    manufacturer_name: str

    manufacturer_code: str

    brand_name: str

    brand_code: str


class ManufacturerBrandLookup:

    def __init__(
        self,
        records: list[
            ManufacturerBrandRecord
        ],
    ):

        self.records = records

        self.by_manufacturer = {}

        self.by_brand = {}

        for record in records:

            manufacturer_key = (
                record
                .manufacturer_name
                .strip()
                .lower()
            )

            brand_key = (
                record
                .brand_name
                .strip()
                .lower()
            )

            self.by_manufacturer.setdefault(
                manufacturer_key,
                [],
            ).append(record)

            if brand_key:

                self.by_brand.setdefault(
                    brand_key,
                    [],
                ).append(record)

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
    ):

        records = []

        for _, row in df.iterrows():

            manufacturer = clean_value(
                row.get(
                    "MANUFACTURER_NAME"
                )
            )

            brand = clean_value(
                row.get(
                    "BRAND_NAME"
                )
            )

            if manufacturer is None:
                continue

            # ------------------------------------------------
            # If no brand is available, use manufacturer
            # ------------------------------------------------

            if brand is None:
                brand = manufacturer

            records.append(
                ManufacturerBrandRecord(
                    manufacturer_name=manufacturer,

                    manufacturer_code=str(
                        row.get(
                            "MANUFACTURER_CODE",
                            "",
                        )
                    ),

                    brand_name=brand,

                    brand_code=str(
                        row.get(
                            "BRAND_CODE",
                            "",
                        )
                    ),
                )
            )

        return cls(records)

    # ========================================================
    # FIND MANUFACTURER
    # ========================================================

    def find_manufacturer(
        self,
        value: str,
    ) -> list[
        ManufacturerBrandRecord
    ]:

        if not value:
            return []

        key = (
            value
            .strip()
            .lower()
        )

        return self.by_manufacturer.get(
            key,
            [],
        )

    # ========================================================
    # FIND BRAND
    # ========================================================

    def find_brand(
        self,
        value: str,
    ) -> list[
        ManufacturerBrandRecord
    ]:

        if not value:
            return []

        key = (
            value
            .strip()
            .lower()
        )

        return self.by_brand.get(
            key,
            [],
        )

    # ========================================================
    # RESOLVE
    # ========================================================

    def resolve(
        self,
        value: str,
    ) -> ManufacturerBrandRecord | None:
        """
        Resolve a manufacturer or brand value
        to a canonical ManufacturerBrandRecord.

        Part 3 expects this method.

        Resolution order:

        1. Exact manufacturer match
        2. Exact brand match
        3. None if no match
        """

        if not value:
            return None

        # ----------------------------------------------------
        # First try manufacturer
        # ----------------------------------------------------

        manufacturer_matches = (
            self.find_manufacturer(
                value
            )
        )

        if manufacturer_matches:

            return manufacturer_matches[0]

        # ----------------------------------------------------
        # Then try brand
        # ----------------------------------------------------

        brand_matches = (
            self.find_brand(
                value
            )
        )

        if brand_matches:

            return brand_matches[0]

        # ----------------------------------------------------
        # No match
        # ----------------------------------------------------

        return None


# ============================================================
# UOM
# ============================================================

@dataclass
class UOMLookup:

    variant_to_abbreviation: dict[str, str]

    measurement_types: dict[str, str]

    house_style_rules: pd.DataFrame | None = None

    # ========================================================
    # NORMALIZE UNIT
    # ========================================================

    def normalize_unit(
        self,
        unit: str,
    ) -> str | None:

        if not unit:
            return None

        key = (
            unit
            .strip()
            .lower()
        )

        return self.variant_to_abbreviation.get(
            key
        )


def build_uom_lookup(
    units_df: pd.DataFrame,
    house_style_df: pd.DataFrame,
) -> UOMLookup:

    columns = {
        str(column)
        .strip()
        .lower():
            column

        for column in units_df.columns
    }

    term_column = None

    abbreviation_column = None

    measurement_column = None

    # ========================================================
    # FIND COLUMNS
    # ========================================================

    for normalized, actual in columns.items():

        # Term / unit / variant

        if (
            term_column is None
            and (
                "term" in normalized
                or "unit" in normalized
                or "variant" in normalized
            )
        ):

            term_column = actual

        # Abbreviation

        if (
            abbreviation_column is None
            and (
                "abbreviation"
                in normalized
                or "abbr"
                in normalized
            )
        ):

            abbreviation_column = actual

        # Measurement type

        if (
            measurement_column is None
            and "measurement"
            in normalized
        ):

            measurement_column = actual

    # ========================================================
    # VALIDATION
    # ========================================================

    if (
        term_column is None
        or abbreviation_column is None
    ):

        raise ValueError(
            "Unable to identify UOM "
            "term and abbreviation columns.\n"
            f"Available columns: "
            f"{list(units_df.columns)}"
        )

    variants = {}

    measurement_types = {}

    # ========================================================
    # BUILD LOOKUP
    # ========================================================

    for _, row in units_df.iterrows():

        term = clean_value(
            row.get(
                term_column
            )
        )

        abbreviation = clean_value(
            row.get(
                abbreviation_column
            )
        )

        if (
            term is None
            or abbreviation is None
        ):

            continue

        variants[
            term.lower()
        ] = abbreviation

        # ----------------------------------------------------
        # Measurement type
        # ----------------------------------------------------

        if measurement_column:

            measurement = clean_value(
                row.get(
                    measurement_column
                )
            )

            if measurement:

                measurement_types[
                    abbreviation
                ] = measurement

    return UOMLookup(
        variant_to_abbreviation=variants,

        measurement_types=measurement_types,

        house_style_rules=house_style_df,
    )


# ============================================================
# DECIMAL / FRACTION
# ============================================================

class DecimalFractionLookup:

    def __init__(
        self,
        decimal_to_fraction: dict[
            float,
            str,
        ],

        fraction_to_decimal: dict[
            str,
            float,
        ],
    ):

        self.decimal_to_fraction_map = (
            decimal_to_fraction
        )

        self.fraction_to_decimal_map = (
            fraction_to_decimal
        )

    # ========================================================
    # DECIMAL -> FRACTION
    # ========================================================

    def decimal_to_fraction(
        self,
        value: float,
    ) -> str | None:

        if value is None:
            return None

        try:

            numeric_value = round(
                float(value),
                6,
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

        return (
            self
            .decimal_to_fraction_map
            .get(
                numeric_value
            )
        )

    # ========================================================
    # FRACTION -> DECIMAL
    # ========================================================

    def fraction_to_decimal(
        self,
        value: str,
    ) -> float | None:

        if not value:
            return None

        key = (
            str(value)
            .strip()
            .lower()
        )

        return (
            self
            .fraction_to_decimal_map
            .get(
                key
            )
        )


def build_decimal_fraction_lookup(
    df: pd.DataFrame,
) -> DecimalFractionLookup:

    decimal_to_fraction = {}

    fraction_to_decimal = {}

    # ========================================================
    # DECIMAL / FRACTION FILE
    #
    # The source contains side-by-side:
    #
    # Fraction | Decimal
    #
    # blocks.
    # ========================================================

    for row_index in range(
        len(df)
    ):

        row = df.iloc[
            row_index
        ]

        for column_index in range(
            0,
            len(row) - 1,
            2,
        ):

            fraction = row.iloc[
                column_index
            ]

            decimal = row.iloc[
                column_index + 1
            ]

            if (
                pd.isna(fraction)
                or pd.isna(decimal)
            ):

                continue

            fraction_text = str(
                fraction
            ).strip()

            # Ignore headers / notes

            if "/" not in fraction_text:

                continue

            try:

                decimal_value = round(
                    float(decimal),
                    6,
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            # ------------------------------------------------
            # Decimal -> Fraction
            # ------------------------------------------------

            decimal_to_fraction[
                decimal_value
            ] = fraction_text

            # ------------------------------------------------
            # Fraction -> Decimal
            # ------------------------------------------------

            fraction_to_decimal[
                fraction_text.lower()
            ] = decimal_value

    return DecimalFractionLookup(
        decimal_to_fraction,

        fraction_to_decimal,
    )


# ============================================================
# LOV
# ============================================================

@dataclass
class LOVAttribute:

    allowed_values: list[str]

    normalized_values: list[str]

    filtering: str = ""

    guidelines: str = ""

    remarks: str = ""


class LOVLookup:

    def __init__(
        self,
        data: dict,
    ):

        self.data = data

    # ========================================================
    # GET ATTRIBUTE
    # ========================================================

    def get_attribute(
        self,
        classpath: str,
        attribute: str,
    ) -> LOVAttribute | None:

        return (
            self
            .data
            .get(
                classpath,
                {}
            )
            .get(
                attribute
            )
        )

    # ========================================================
    # GET CLASSPATH
    # ========================================================

    def get_classpath(
        self,
        classpath: str,
    ) -> dict:

        return self.data.get(
            classpath,
            {}
        )


# ============================================================
# LOV VALUE SPLITTER
# ============================================================

def _split_values(
    value,
) -> list[str]:

    value = clean_value(
        value
    )

    if value is None:

        return []

    import re

    values = re.split(
        r"[|;,]",
        value,
    )

    return [
        item.strip()
        for item in values
        if item.strip()
    ]


# ============================================================
# BUILD LOV LOOKUP
# ============================================================

def build_lov_lookup(
    df: pd.DataFrame,
) -> LOVLookup:

    def find_column(
        *keywords,
    ):

        for column in df.columns:

            name = (
                str(column)
                .strip()
                .lower()
            )

            if all(
                keyword in name
                for keyword in keywords
            ):

                return column

        return None

    # ========================================================
    # IDENTIFY COLUMNS
    # ========================================================

    classpath_column = find_column(
        "classpath"
    )

    attribute_column = find_column(
        "attribute",
        "label",
    )

    values_column = find_column(
        "attribute",
        "values",
    )

    normalized_values_column = (
        find_column(
            "normalized",
            "values",
        )
    )

    filtering_column = find_column(
        "filtering"
    )

    guidelines_column = find_column(
        "guidelines"
    )

    remarks_column = find_column(
        "remarks"
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    required = {
        "Classpath":
            classpath_column,

        "Attribute":
            attribute_column,

        "Attribute Values":
            values_column,

        "Normalized Values":
            normalized_values_column,
    }

    missing = [
        name
        for name, column
        in required.items()
        if column is None
    ]

    if missing:

        raise ValueError(
            "Required LOV columns not found: "
            f"{missing}\n"
            f"Available columns: "
            f"{list(df.columns)}"
        )

    result = {}

    # ========================================================
    # BUILD LOOKUP
    # ========================================================

    for _, row in df.iterrows():

        classpath = clean_value(
            row.get(
                classpath_column
            )
        )

        attribute = clean_value(
            row.get(
                attribute_column
            )
        )

        if (
            classpath is None
            or attribute is None
        ):

            continue

        result.setdefault(
            classpath,
            {}
        )

        result[
            classpath
        ][attribute] = LOVAttribute(

            allowed_values=_split_values(
                row.get(
                    values_column
                )
            ),

            normalized_values=(
                _split_values(
                    row.get(
                        normalized_values_column
                    )
                )
            ),

            filtering=(
                clean_value(
                    row.get(
                        filtering_column
                    )
                )
                or ""
                if filtering_column
                else ""
            ),

            guidelines=(
                clean_value(
                    row.get(
                        guidelines_column
                    )
                )
                or ""
                if guidelines_column
                else ""
            ),

            remarks=(
                clean_value(
                    row.get(
                        remarks_column
                    )
                )
                or ""
                if remarks_column
                else ""
            ),
        )

    return LOVLookup(
        result
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

# Part 3 currently uses these names.

LovLookup = LOVLookup

UomLookup = UOMLookup