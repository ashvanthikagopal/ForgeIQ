"""
part1_foundation
-----------------
Data foundation layer for the UniHack / Unilog enrichment pipeline.

Owns:
    - Parsing all 9 raw pack files (parsers.py), defensively (merged cells,
      multi-row headers, side-by-side column blocks like Decimal_Fraction.xlsx).
    - Building the 4 shared lookup structures (lookups.py):
          manufacturer_brand_lookup
          uom_lookup
          decimal_fraction_lookup
          lov_lookup
    - Detecting and stripping placeholder values such as "-- Unbranded --"
      before they reach any downstream matching/generation logic
      (placeholder_utils.py).
    - The 200-item ground-truth test harness and scoring function that
      Parts 2-4 call to validate their outputs (test_harness.py).

Everything exported here is meant to be imported by part2_classification,
part3_normalization, and part4_enrichment_qa as clean, documented structures
-- not notebook scratch. See the Part 1 handoff checklist in the project
guide for what "done" looks like.
"""

from __future__ import annotations

# --- Placeholder utilities -------------------------------------------------
from .placeholder_utils import (
    KNOWN_PLACEHOLDERS,
    PlaceholderReport,
    clean_value,
    is_generic_empty_token,
    is_known_placeholder,
    is_placeholder_shaped,
    scan_column,
    strip_placeholders,
    strip_placeholders_from_record,
    summarize_placeholders,
)

# --- Ground-truth test harness ---------------------------------------------
from .test_harness import (
    FieldScore,
    GroundTruthRecord,
    RecordScore,
    TestHarness,
    load_ground_truth,
)

# --- Parsers & lookups -------------------------------------------------
# These are owned by the same Part 1 deliverable; imported here so the rest
# of the team has a single entry point: `from part1_foundation import ...`
# If parsers.py / lookups.py aren't present yet in a given checkout, don't
# hard-fail the whole package import -- surface a clear error only when the
# missing piece is actually used.
try:
    from .parsers import (  # noqa: F401
        parse_all_pack_files,
        parse_decimal_fraction,
        parse_manufacturer_brand_list,
        parse_uom_standards,
        parse_lov,
        parse_200_item_ground_truth,
    )
except ImportError:  # pragma: no cover - allows partial checkouts during dev
    pass

try:
    from .lookups import (  # noqa: F401
        ManufacturerBrandLookup,
        UomLookup,
        DecimalFractionLookup,
        LovLookup,
        build_all_lookups,
    )
except ImportError:  # pragma: no cover - allows partial checkouts during dev
    pass


__all__ = [
    # placeholder_utils
    "KNOWN_PLACEHOLDERS",
    "PlaceholderReport",
    "clean_value",
    "is_generic_empty_token",
    "is_known_placeholder",
    "is_placeholder_shaped",
    "scan_column",
    "strip_placeholders",
    "strip_placeholders_from_record",
    "summarize_placeholders",
    # test_harness
    "FieldScore",
    "GroundTruthRecord",
    "RecordScore",
    "TestHarness",
    "load_ground_truth",
    # parsers (if available)
    "parse_all_pack_files",
    "parse_decimal_fraction",
    "parse_manufacturer_brand_list",
    "parse_uom_standards",
    "parse_lov",
    "parse_200_item_ground_truth",
    # lookups (if available)
    "ManufacturerBrandLookup",
    "UomLookup",
    "DecimalFractionLookup",
    "LovLookup",
    "build_all_lookups",
]
