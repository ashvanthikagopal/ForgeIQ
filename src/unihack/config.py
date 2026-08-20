"""Shared paths + constants. Import this instead of hardcoding paths."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
DATA_GROUND_TRUTH = REPO_ROOT / "data" / "ground_truth"

# --- Part 1 source files (expected filenames in data/raw/) ---
FILE_REFERENCE_INDEX = "Reference_Documents_Summary.xlsx"
FILE_GROUND_TRUTH_200 = "Unilog-Sample_200_Items-Input-vs-Output.xlsx"
FILE_CONTENT_GUIDELINES = "UNILOG_INTERNAL_CONTENT_GUIDELINES.docx"
FILE_UOM_STANDARDS = "Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx"
FILE_DECIMAL_FRACTION = "Decimal_Fraction.xlsx"
FILE_MANUFACTURER_BRAND = "UniCat_Manufacturer_and_Brand_List.xlsx"
FILE_LOV = "Unicat_Lov_v1_0_Updated_With_Remarks.xlsx"
FILE_FAUCETS_LOV = "FAUCETS_LOV.xlsx"
FILE_FITTINGS_LOV = "Fittings_LOV.xlsx"          # optional second category
FILE_SAMPLE_1000 = "Sample-1000_Items.xlsx"

# --- category scope ---
PRIMARY_CATEGORY = "Faucets"
SECONDARY_CATEGORY_OPTIONAL = "Fittings"

# --- placeholders that mean "empty", never real data ---
PLACEHOLDER_STRINGS = {
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --",
}

# --- sourcing policy (Phase G) ---
ALLOWED_SOURCE_TYPE = "manufacturer_official"