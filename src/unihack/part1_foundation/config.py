from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"

PROCESSED_DATA_DIR = DATA_DIR / "processed"


# ============================================================
# ACTUAL FILES YOU CURRENTLY HAVE
# ============================================================

SAMPLE_INPUT_FILE = (
    RAW_DATA_DIR
    / "Unihack_ Sample Dataset - Input.csv"
)

DELIVERY_FORMAT_FILE = (
    GROUND_TRUTH_DIR
    / "Unihack_ Expected Output - Delivery Format.csv"
)


# ============================================================
# OPTIONAL LOOKUP FILES
#
# These are the lookup sources required by the specification.
# Keep the paths here, but don't create fake files.
# ============================================================

UOM_FILE = (
    RAW_DATA_DIR
    / "Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx"
)

DECIMAL_FRACTION_FILE = (
    RAW_DATA_DIR
    / "Decimal_Fraction.xlsx"
)

MANUFACTURER_BRAND_FILE = (
    RAW_DATA_DIR
    / "UniCat_Manufacturer_and_Brand_List.xlsx"
)

LOV_FILE = (
    RAW_DATA_DIR
    / "Unicat_Lov_v1_0_Updated_With_Remarks.xlsx"
)

FAUCETS_LOV_FILE = (
    RAW_DATA_DIR
    / "FAUCETS_LOV.xlsx"
)

FITTINGS_LOV_FILE = (
    RAW_DATA_DIR
    / "Fittings_LOV.xlsx"
)