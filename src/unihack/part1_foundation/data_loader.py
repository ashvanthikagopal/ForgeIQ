from __future__ import annotations

from dataclasses import dataclass

from .config import (
    DECIMAL_FRACTION_FILE,
    DELIVERY_FORMAT_FILE,
    FAUCETS_LOV_FILE,
    FITTINGS_LOV_FILE,
    LOV_FILE,
    MANUFACTURER_BRAND_FILE,
    SAMPLE_INPUT_FILE,
    UOM_FILE,
)

from .ground_truth import (
    GroundTruthHarness,
)

from .lookup_sources import (
    LookupSourceStatus,
    inspect_part1_sources,
)

from .parsers import (
    parse_delivery_format,
    parse_sample_input,
)


# ============================================================
# PART 1 DATA
# ============================================================

@dataclass
class Part1Data:

    # --------------------------------------------------------
    # Main input
    # --------------------------------------------------------

    sample_input: object

    # --------------------------------------------------------
    # Delivery / expected output
    # --------------------------------------------------------

    delivery_format: object | None

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    ground_truth: GroundTruthHarness | None

    # --------------------------------------------------------
    # Lookup objects
    #
    # These are optional because the actual lookup files
    # currently do not contain usable data.
    # --------------------------------------------------------

    manufacturer_brand_lookup: object | None = None

    uom_lookup: object | None = None

    decimal_fraction_lookup: object | None = None

    lov_lookup: object | None = None

    # --------------------------------------------------------
    # Source availability information
    # --------------------------------------------------------

    lookup_sources: dict[
        str,
        LookupSourceStatus,
    ] | None = None


# ============================================================
# LOAD PART 1 DATA
# ============================================================

def load_part1_data() -> Part1Data:

    # ========================================================
    # 1. LOAD REAL INPUT CSV
    # ========================================================

    sample_input = (
        parse_sample_input(
            SAMPLE_INPUT_FILE
        )
    )

    # ========================================================
    # 2. LOAD DELIVERY FORMAT
    # ========================================================

    delivery_format = None

    if DELIVERY_FORMAT_FILE.exists():

        try:

            delivery_format = (
                parse_delivery_format(
                    DELIVERY_FORMAT_FILE
                )
            )

        except Exception:

            delivery_format = None

    # ========================================================
    # 3. GROUND TRUTH
    # ========================================================

    ground_truth = None

    if delivery_format is not None:

        ground_truth = GroundTruthHarness(
            input_df=sample_input,
            expected_df=delivery_format,
        )

    # ========================================================
    # 4. INSPECT LOOKUP FILES
    #
    # We DO NOT create fake lookup data.
    # ========================================================

    lookup_paths = {

        "UOM":
            UOM_FILE,

        "Decimal/Fraction":
            DECIMAL_FRACTION_FILE,

        "Manufacturer/Brand":
            MANUFACTURER_BRAND_FILE,

        "General LOV":
            LOV_FILE,

        "Faucets LOV":
            FAUCETS_LOV_FILE,

        "Fittings LOV":
            FITTINGS_LOV_FILE,
    }

    lookup_sources = (
        inspect_part1_sources(
            lookup_paths
        )
    )

    # ========================================================
    # 5. LOOKUP OBJECTS
    #
    # Currently None because your actual reference files
    # are empty.
    #
    # When real files are supplied, these are the places
    # where we will build the actual lookup objects.
    # ========================================================

    manufacturer_brand_lookup = None

    uom_lookup = None

    decimal_fraction_lookup = None

    lov_lookup = None

    # ========================================================
    # 6. RETURN PART 1 DATA
    # ========================================================

    return Part1Data(

        sample_input=sample_input,

        delivery_format=delivery_format,

        ground_truth=ground_truth,

        manufacturer_brand_lookup=(
            manufacturer_brand_lookup
        ),

        uom_lookup=(
            uom_lookup
        ),

        decimal_fraction_lookup=(
            decimal_fraction_lookup
        ),

        lov_lookup=(
            lov_lookup
        ),

        lookup_sources=(
            lookup_sources
        ),
    )