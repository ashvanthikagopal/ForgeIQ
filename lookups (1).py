"""
lookups.py
Part 1 — Setup & Data Foundation

Builds the 4 shared lookup structures every downstream stage (Parts 2-4)
imports directly:

    manufacturer_brand_lookup
    uom_lookup
    decimal_fraction_lookup
    lov_lookup

Also provides fuzzy-matching helpers for turning a messy manufacturer
string into a canonical manufacturer/brand pair, since exact string
matching alone won't survive the "6 different spellings" problem
described in the pack.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .placeholder_utils import clean_value, is_placeholder


# ---------------------------------------------------------------------------
# 1. manufacturer_brand_lookup
# ---------------------------------------------------------------------------

@dataclass
class ManufacturerBrandRecord:
    manufacturer_name: str
    manufacturer_code: Optional[str]
    brand_name: Optional[str]  # None -> callers should fall back to manufacturer_name
    brand_code: Optional[str]


def _normalize_key(s: str) -> str:
    """Loose normalization used ONLY for matching keys, never for output.
    Lowercase, strip punctuation/legal suffixes/symbols, collapse whitespace."""
    s = s.lower()
    s = re.sub(r"[®™©]", "", s)
    s = re.sub(r"\b(inc|llc|ltd|co|corp|company|corporation)\b\.?", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_manufacturer_brand_lookup(
    df: pd.DataFrame,
    manufacturer_col: str = "MANUFACTURER_NAME",
    manufacturer_code_col: str = "MANUFACTURER_CODE",
    brand_col: str = "BRAND_NAME",
    brand_code_col: str = "BRAND_CODE",
) -> Dict[str, ManufacturerBrandRecord]:
    """
    Returns {normalized_key: ManufacturerBrandRecord}, where normalized_key
    covers BOTH the manufacturer name and (if present) the brand name, so a
    messy input string matching either resolves to the same canonical
    record. `manufacturer_name`/`brand_name` on the record are always the
    EXACT canonical strings (casing, ®/™, suffixes preserved) — never the
    normalized key.
    """
    lookup: Dict[str, ManufacturerBrandRecord] = {}

    missing_cols = [
        c
        for c in (manufacturer_col, manufacturer_code_col, brand_col, brand_code_col)
        if c not in df.columns
    ]
    if missing_cols:
        raise ValueError(
            f"manufacturer/brand list is missing expected columns {missing_cols}; "
            f"found columns: {list(df.columns)}"
        )

    for _, row in df.iterrows():
        manu = clean_value(row.get(manufacturer_col))
        if manu is None:
            continue  # a row with no real manufacturer name is useless as a lookup target
        brand = clean_value(row.get(brand_col))
        record = ManufacturerBrandRecord(
            manufacturer_name=manu,
            manufacturer_code=clean_value(row.get(manufacturer_code_col)),
            brand_name=brand,
            brand_code=clean_value(row.get(brand_code_col)),
        )
        lookup[_normalize_key(manu)] = record
        if brand:
            lookup[_normalize_key(brand)] = record

    return lookup


def resolve_manufacturer(
    raw_value: Optional[str],
    lookup: Dict[str, ManufacturerBrandRecord],
    fuzzy_threshold: float = 0.86,
) -> Optional[Tuple[ManufacturerBrandRecord, float]]:
    """
    Resolve a messy supplier manufacturer string to its canonical record.
    Tries exact normalized match first (fast path, confidence 1.0), then
    falls back to fuzzy matching (SequenceMatcher ratio) for confidence
    >= fuzzy_threshold. Returns (record, confidence) or None if nothing
    meets the threshold — callers should treat None as 'needs_review',
    never guess.

    Note: at 27,000+ rows, a production pipeline should swap the fuzzy
    fallback for a proper library (e.g. rapidfuzz) or a blocking/indexing
    strategy; SequenceMatcher keeps this file dependency-free for the
    hackathon and is fine at the ~1,000-row Sample_1000 scale.
    """
    if is_placeholder(raw_value):
        return None

    key = _normalize_key(str(raw_value))
    if key in lookup:
        return lookup[key], 1.0

    best_record, best_score = None, 0.0
    for candidate_key, record in lookup.items():
        score = SequenceMatcher(None, key, candidate_key).ratio()
        if score > best_score:
            best_score, best_record = score, record

    if best_record is not None and best_score >= fuzzy_threshold:
        return best_record, best_score
    return None


# ---------------------------------------------------------------------------
# 2. uom_lookup
# ---------------------------------------------------------------------------

@dataclass
class UomLookup:
    # normalized raw unit text (lower, stripped) -> approved abbreviation
    abbreviation_by_variant: Dict[str, str] = field(default_factory=dict)
    # measurement type (e.g. "Length") -> a default approved abbreviation
    approved_by_measurement_type: Dict[str, str] = field(default_factory=dict)
    # free-text house style rules (22 of them); Part 3 can turn specific
    # ones into code as needed (e.g. "always a space between number and unit")
    house_style_rules: List[str] = field(default_factory=list)


def _find_col(df: pd.DataFrame, candidates: Tuple[str, ...]) -> Optional[str]:
    for cand in candidates:
        for col in df.columns:
            if cand.lower() == str(col).strip().lower():
                return col
    for cand in candidates:
        for col in df.columns:
            if cand.lower() in str(col).strip().lower():
                return col
    return None


def build_uom_lookup(
    units_df: pd.DataFrame,
    house_style_rules_raw: pd.DataFrame,
    unit_variant_col_candidates: Tuple[str, ...] = (
        "Term",
        "Variant",
        "Abbreviation Variant",
        "Unit",
    ),
    approved_abbrev_col_candidates: Tuple[str, ...] = (
        "Approved Abbreviation",
        "Abbreviation",
        "Approved",
    ),
    measurement_type_col_candidates: Tuple[str, ...] = (
        "Measurement Type",
        "Type",
        "Category",
    ),
) -> UomLookup:
    """
    Builds a many-to-one lookup: every messy variant of a unit ("inches",
    "IN.", "inch", "in") -> the single approved abbreviation ("in"). Column
    names are matched case-insensitively against several candidate names
    since the exact header wording in the source file isn't guaranteed.
    """
    variant_col = _find_col(units_df, unit_variant_col_candidates)
    approved_col = _find_col(units_df, approved_abbrev_col_candidates)
    type_col = _find_col(units_df, measurement_type_col_candidates)

    if approved_col is None:
        raise ValueError(
            f"Could not find an 'approved abbreviation' column in UOM sheet; "
            f"available columns: {list(units_df.columns)}"
        )

    result = UomLookup()
    for _, row in units_df.iterrows():
        approved = clean_value(row.get(approved_col))
        if approved is None:
            continue

        if variant_col:
            variant = clean_value(row.get(variant_col))
            if variant:
                result.abbreviation_by_variant[variant.strip().lower()] = approved
        # The approved form should always resolve to itself.
        result.abbreviation_by_variant[approved.strip().lower()] = approved

        if type_col:
            mtype = clean_value(row.get(type_col))
            if mtype and mtype not in result.approved_by_measurement_type:
                result.approved_by_measurement_type[mtype] = approved

    # House-style rules sheet is free text / loosely structured — flatten
    # every non-empty cell into a list of rule strings rather than assuming
    # a fixed column layout (per the "notes in stray columns" warning).
    for _, row in house_style_rules_raw.iterrows():
        for val in row:
            cleaned = clean_value(val)
            if cleaned and len(cleaned) > 3:  # skip stray single chars/numbers
                result.house_style_rules.append(cleaned)

    seen = set()
    deduped_rules = []
    for r in result.house_style_rules:
        if r not in seen:
            seen.add(r)
            deduped_rules.append(r)
    result.house_style_rules = deduped_rules

    return result


def normalize_unit_text(raw_unit: str, uom_lookup: UomLookup) -> Optional[str]:
    """Look up the approved abbreviation for a raw unit string. Returns
    None (not a guess) if the unit isn't in the lookup at all."""
    if is_placeholder(raw_unit):
        return None
    return uom_lookup.abbreviation_by_variant.get(str(raw_unit).strip().lower())


def format_value_with_unit(number: str, approved_unit: str) -> str:
    """The one house-style rule every generator needs constantly: always a
    space between the number and the unit ('24 in', never '24in')."""
    return f"{number} {approved_unit}"


# ---------------------------------------------------------------------------
# 3. decimal_fraction_lookup
# ---------------------------------------------------------------------------

@dataclass
class DecimalFractionLookup:
    fraction_to_decimal: Dict[str, float] = field(default_factory=dict)
    decimal_to_fraction: Dict[float, str] = field(default_factory=dict)

    def decimal_to_fraction_str(self, value: float, tolerance: float = 1e-4) -> Optional[str]:
        """Nearest-match lookup for a raw decimal (e.g. 0.5) -> '1/2'.
        Returns None if nothing in the 63-row table is within tolerance —
        callers should NOT invent a fraction in that case."""
        best_key, best_diff = None, float("inf")
        for dec, frac in self.decimal_to_fraction.items():
            diff = abs(dec - value)
            if diff < best_diff:
                best_diff, best_key = diff, frac
        if best_key is not None and best_diff <= tolerance:
            return best_key
        return None

    def mixed_number_to_fraction_str(self, value: float) -> Optional[str]:
        """Handles values like 50.25 -> '50-1/4' by splitting whole/
        fractional parts and looking up only the fractional part."""
        whole = int(value)
        frac_part = round(value - whole, 6)
        if frac_part == 0:
            return str(whole)
        frac_str = self.decimal_to_fraction_str(frac_part)
        if frac_str is None:
            return None
        return f"{whole}-{frac_str}" if whole else frac_str


def build_decimal_fraction_lookup(df: pd.DataFrame) -> DecimalFractionLookup:
    """Consumes the tidy long-format df produced by
    parsers.load_decimal_fraction() (columns: fraction, decimal) and builds
    both-direction dictionaries."""
    result = DecimalFractionLookup()
    for _, row in df.iterrows():
        frac = clean_value(row.get("fraction"))
        dec = row.get("decimal")
        if frac is None or pd.isna(dec):
            continue
        dec = float(dec)
        result.fraction_to_decimal[frac] = dec
        result.decimal_to_fraction[dec] = frac
    return result


# ---------------------------------------------------------------------------
# 4. lov_lookup — Classpath -> {attribute: allowed/normalized values}
# ---------------------------------------------------------------------------

@dataclass
class AttributeSpec:
    attribute_label: str
    normalized_label: Optional[str]
    filtering: bool
    allowed_values: List[str] = field(default_factory=list)     # raw seen values
    normalized_values: List[str] = field(default_factory=list)  # canonical values
    guidelines: Optional[str] = None
    remarks: Optional[str] = None


LovLookup = Dict[str, Dict[str, AttributeSpec]]  # classpath -> attribute_label -> spec


def build_lov_lookup(
    df: pd.DataFrame,
    classpath_col_candidates: Tuple[str, ...] = ("Classpath",),
    attribute_col_candidates: Tuple[str, ...] = ("Attribute Label",),
    normalized_label_col_candidates: Tuple[str, ...] = ("Normalized Label",),
    filtering_col_candidates: Tuple[str, ...] = ("Filtering Y/N", "Filtering"),
    values_col_candidates: Tuple[str, ...] = ("Attribute Values", "Values"),
    normalized_values_col_candidates: Tuple[str, ...] = ("Normalized Values",),
    guidelines_col_candidates: Tuple[str, ...] = ("Guidelines",),
    remarks_col_candidates: Tuple[str, ...] = ("Remarks",),
) -> LovLookup:
    """
    Builds the constrained-vocabulary lookup that Parts 2 and 3 must never
    generate outside of. Rows with placeholder/blank classpath or attribute
    are skipped.

    Multiple rows sharing the same (classpath, attribute) are merged: their
    allowed_values / normalized_values lists are unioned, since the source
    LOV file is typically one row per (classpath, attribute, value).
    """
    classpath_col = _find_col(df, classpath_col_candidates)
    attribute_col = _find_col(df, attribute_col_candidates)
    normalized_label_col = _find_col(df, normalized_label_col_candidates)
    filtering_col = _find_col(df, filtering_col_candidates)
    values_col = _find_col(df, values_col_candidates)
    normalized_values_col = _find_col(df, normalized_values_col_candidates)
    guidelines_col = _find_col(df, guidelines_col_candidates)
    remarks_col = _find_col(df, remarks_col_candidates)

    if classpath_col is None or attribute_col is None:
        raise ValueError(
            f"Could not find Classpath/Attribute Label columns; "
            f"available columns: {list(df.columns)}"
        )

    lookup: LovLookup = {}

    for _, row in df.iterrows():
        classpath = clean_value(row.get(classpath_col))
        attribute = clean_value(row.get(attribute_col))
        if classpath is None or attribute is None:
            continue  # unusable row for building the constrained vocabulary

        classpath_bucket = lookup.setdefault(classpath, {})
        spec = classpath_bucket.get(attribute)
        if spec is None:
            filtering_raw = clean_value(row.get(filtering_col)) if filtering_col else None
            spec = AttributeSpec(
                attribute_label=attribute,
                normalized_label=clean_value(row.get(normalized_label_col))
                if normalized_label_col
                else None,
                filtering=(str(filtering_raw).strip().lower() in ("y", "yes", "true"))
                if filtering_raw
                else False,
                guidelines=clean_value(row.get(guidelines_col)) if guidelines_col else None,
                remarks=clean_value(row.get(remarks_col)) if remarks_col else None,
            )
            classpath_bucket[attribute] = spec

        raw_value = clean_value(row.get(values_col)) if values_col else None
        if raw_value and raw_value not in spec.allowed_values:
            spec.allowed_values.append(raw_value)

        norm_value = clean_value(row.get(normalized_values_col)) if normalized_values_col else None
        if norm_value and norm_value not in spec.normalized_values:
            spec.normalized_values.append(norm_value)

    return lookup


def is_value_in_lov(
    classpath: str, attribute: str, value: str, lov_lookup: LovLookup
) -> bool:
    """Hard gate used by validation (Phase E/H): is `value` an actually
    permitted normalized value for this classpath+attribute? Returns False
    (not an exception) for an unknown classpath/attribute so callers can
    treat it as a 'needs_review' flag rather than crashing the pipeline."""
    spec = lov_lookup.get(classpath, {}).get(attribute)
    if spec is None:
        return False
    return value in spec.normalized_values or value in spec.allowed_values
