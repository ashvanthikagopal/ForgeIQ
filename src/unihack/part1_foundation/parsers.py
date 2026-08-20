"""
parsers.py
Part 1 — Setup & Data Foundation

Defensive Excel parsing for the 9 files in the Unilog challenge pack.

Design principles (per the project guide):
- Never assume row 1 is a clean header — detect it.
- Never assume merged cells behave like normal cells — unmerge + forward-fill
  before handing data to pandas.
- Decimal_Fraction.xlsx is 4 side-by-side column blocks, not 1 column —
  parsed explicitly as such.
- Every parser logs a warning instead of silently guessing when something
  looks off, so problems surface early instead of corrupting downstream data.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import openpyxl
import pandas as pd


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

@dataclass
class SheetLoadWarning:
    file: str
    sheet: str
    message: str


_WARNINGS: List[SheetLoadWarning] = []


def get_load_warnings() -> List[SheetLoadWarning]:
    """All warnings collected across every parse call so far — check this
    at the end of Phase A and put anything in it into your handoff notes."""
    return list(_WARNINGS)


def clear_load_warnings() -> None:
    _WARNINGS.clear()


def _warn(file: str, sheet: str, message: str) -> None:
    _WARNINGS.append(SheetLoadWarning(file, sheet, message))
    warnings.warn(f"[{file} / {sheet}] {message}")


def wb_first_sheet(path: str) -> str:
    wb = openpyxl.load_workbook(path, read_only=True)
    return wb.sheetnames[0]


def load_and_unmerge(path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load a worksheet as raw cell values (no header assumption), unmerging
    any merged cell ranges by forward-filling the top-left value into every
    cell the merge spans. Returns a DataFrame of raw values with default
    integer columns — header detection happens separately.
    """
    wb = openpyxl.load_workbook(path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ValueError(
            f"Sheet '{sheet_name}' not found in {path}. Available: {wb.sheetnames}"
        )
    ws = wb[sheet_name]

    data = [[cell.value for cell in row] for row in ws.iter_rows()]
    df = pd.DataFrame(data)

    # openpyxl only stores the value in the top-left cell of a merged range;
    # every other cell in the range is None. Forward-fill it manually.
    for merged_range in ws.merged_cells.ranges:
        min_row, min_col = merged_range.min_row, merged_range.min_col
        max_row, max_col = merged_range.max_row, merged_range.max_col
        top_left_value = ws.cell(row=min_row, column=min_col).value
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                df.iat[r - 1, c - 1] = top_left_value

    if ws.merged_cells.ranges:
        _warn(
            Path(path).name,
            sheet_name,
            f"{len(ws.merged_cells.ranges)} merged cell range(s) found and unmerged.",
        )

    return df


def detect_header_row(raw_df: pd.DataFrame, max_scan_rows: int = 10) -> int:
    """
    Heuristic header-row detector: scans the first `max_scan_rows` rows and
    picks the row with the highest fraction of non-null, string (not purely
    numeric) cells — usually the real header, even when row 0 is a title,
    a merged banner, or a stray note (as in the UOM sheet).
    """
    best_row = 0
    best_score = -1.0
    n_scan = min(max_scan_rows, len(raw_df))

    for i in range(n_scan):
        row = raw_df.iloc[i]
        non_null = row.notna().sum()
        if non_null == 0:
            continue
        string_like = sum(
            1
            for v in row
            if isinstance(v, str)
            and v.strip() != ""
            and not v.strip().replace(".", "", 1).isdigit()
        )
        score = string_like / max(non_null, 1) * (non_null / raw_df.shape[1])
        if score > best_score:
            best_score = score
            best_row = i

    return best_row


def load_sheet_with_header_detection(
    path: str, sheet_name: str, expected_header_hint: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Full defensive load: unmerge, detect header row, promote it, drop rows
    above it, reset the index. If `expected_header_hint` is given (a list
    of column names we expect to see), and none of them appear in the
    detected header row, we warn loudly rather than silently returning
    garbage.
    """
    raw = load_and_unmerge(path, sheet_name)
    header_row_idx = detect_header_row(raw)

    header = raw.iloc[header_row_idx].tolist()
    body = raw.iloc[header_row_idx + 1 :].reset_index(drop=True)
    body.columns = [
        str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(header)
    ]

    if header_row_idx != 0:
        _warn(
            Path(path).name,
            sheet_name,
            f"Header row detected at index {header_row_idx}, not row 0 — "
            f"rows above it were dropped as banner/notes.",
        )

    if expected_header_hint:
        found = any(
            any(hint.lower() in str(c).lower() for c in body.columns)
            for hint in expected_header_hint
        )
        if not found:
            _warn(
                Path(path).name,
                sheet_name,
                f"None of the expected header hints {expected_header_hint} were "
                f"found in detected header {list(body.columns)}. Header detection "
                f"may be wrong — inspect manually.",
            )

    # Drop fully-empty rows/columns that often remain after unmerging.
    body = body.dropna(axis=0, how="all").dropna(axis=1, how="all")
    return body


def _load_all_sheets(path: str) -> Dict[str, pd.DataFrame]:
    wb = openpyxl.load_workbook(path, read_only=True)
    result = {}
    for sheet_name in wb.sheetnames:
        try:
            result[sheet_name] = load_sheet_with_header_detection(path, sheet_name)
        except Exception as e:  # noqa: BLE001 - one bad sheet shouldn't kill the load
            _warn(Path(path).name, sheet_name, f"Failed to parse sheet: {e}")
    return result


# ---------------------------------------------------------------------------
# File-specific parsers
# ---------------------------------------------------------------------------

def load_reference_summary(path: str) -> pd.DataFrame:
    """Reference_Documents_Summary.xlsx — the pack's own index."""
    return load_sheet_with_header_detection(path, wb_first_sheet(path))


def load_200_items(path: str) -> Dict[str, pd.DataFrame]:
    """
    Unilog-Sample_200_Items-Input-vs-Output.xlsx
    Returns {'input': df, 'delivery_format': df} — the ground-truth pair
    every later stage gets scored against. Sheet names are matched
    fuzzily since exact naming varies across exports.
    """
    wb = openpyxl.load_workbook(path, read_only=True)
    sheets = wb.sheetnames

    def _find(*keywords: str) -> str:
        for s in sheets:
            low = s.lower()
            if all(k in low for k in keywords):
                return s
        raise ValueError(f"Could not find a sheet matching {keywords} in {sheets}")

    input_sheet = _find("input")
    delivery_sheet = _find("delivery")

    return {
        "input": load_sheet_with_header_detection(
            path, input_sheet, expected_header_hint=["Part_Desc", "SKU"]
        ),
        "delivery_format": load_sheet_with_header_detection(
            path, delivery_sheet, expected_header_hint=["Classpath", "Brand"]
        ),
    }


def load_uom_standards(path: str) -> Dict[str, pd.DataFrame]:
    """
    Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx
    Sheet1: ~500 approved unit abbreviations across 89 measurement types.
    Sheet2: 22 house-style rules — often free text, NOT a clean table (this
    is the sheet the guide warns has "notes parked in stray columns"), so
    it's loaded leniently and left as raw rows for lookups.py to flatten.
    """
    wb = openpyxl.load_workbook(path, read_only=True)
    sheets = wb.sheetnames
    if len(sheets) < 2:
        _warn(
            Path(path).name,
            "workbook",
            f"Expected 2 sheets (units + house-style rules), found {len(sheets)}: {sheets}",
        )

    units_sheet = sheets[0]
    rules_sheet = sheets[1] if len(sheets) > 1 else sheets[0]

    units_df = load_sheet_with_header_detection(
        path, units_sheet, expected_header_hint=["Unit", "Abbreviation"]
    )

    rules_raw = load_and_unmerge(path, rules_sheet)
    rules_raw = (
        rules_raw.dropna(axis=0, how="all").dropna(axis=1, how="all").reset_index(drop=True)
    )

    return {"units": units_df, "house_style_rules_raw": rules_raw}


def load_decimal_fraction(path: str) -> pd.DataFrame:
    """
    Decimal_Fraction.xlsx — 63 rows laid out as 4 SIDE-BY-SIDE
    Fraction | Decimal column-pair blocks, not one long column. Detects
    each 'Fraction'/'Decimal'-labelled pair anywhere across the sheet width
    and stacks them into one tidy long-format table:
        columns -> ['fraction', 'decimal']
    """
    sheet = wb_first_sheet(path)
    raw = load_and_unmerge(path, sheet)
    header_row_idx = detect_header_row(raw)
    header = raw.iloc[header_row_idx].tolist()
    body = raw.iloc[header_row_idx + 1 :].reset_index(drop=True)

    pairs = []
    for col_idx, col_name in enumerate(header):
        if col_name is None:
            continue
        name_low = str(col_name).strip().lower()
        if name_low.startswith("fraction"):
            decimal_col_idx = None
            for probe in (col_idx + 1, col_idx + 2):
                if (
                    probe < len(header)
                    and header[probe] is not None
                    and str(header[probe]).strip().lower().startswith("decimal")
                ):
                    decimal_col_idx = probe
                    break
            if decimal_col_idx is None:
                _warn(
                    Path(path).name,
                    sheet,
                    f"Found 'Fraction' column at index {col_idx} with no paired "
                    f"'Decimal' column nearby — skipped this block.",
                )
                continue
            pairs.append((col_idx, decimal_col_idx))

    if not pairs:
        raise ValueError(
            "No Fraction|Decimal column pairs detected in Decimal_Fraction.xlsx — "
            "layout may have changed; inspect the file manually."
        )
    if len(pairs) != 4:
        _warn(
            Path(path).name,
            sheet,
            f"Expected 4 side-by-side Fraction|Decimal blocks, found {len(pairs)}.",
        )

    frames = []
    for frac_idx, dec_idx in pairs:
        block = body.iloc[:, [frac_idx, dec_idx]].copy()
        block.columns = ["fraction", "decimal"]
        block = block.dropna(how="all")
        frames.append(block)

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=["fraction", "decimal"]).reset_index(drop=True)
    combined["fraction"] = combined["fraction"].astype(str).str.strip()
    combined["decimal"] = pd.to_numeric(combined["decimal"], errors="coerce")

    if len(combined) != 63:
        _warn(
            Path(path).name,
            sheet,
            f"Expected 63 fraction/decimal rows total, parsed {len(combined)} — "
            f"check for blank rows within blocks or a miscounted pair.",
        )

    return combined


def load_manufacturer_brand_list(path: str) -> pd.DataFrame:
    """UniCat_Manufacturer_and_Brand_List.xlsx — 27,000+ rows of canonical
    manufacturer/brand names with exact legal casing/®/™/suffixes."""
    return load_sheet_with_header_detection(
        path,
        wb_first_sheet(path),
        expected_header_hint=["MANUFACTURER_NAME", "BRAND_NAME"],
    )


def load_unicat_lov(path: str) -> pd.DataFrame:
    """
    Unicat_Lov_v1_0_Updated_With_Remarks.xlsx — ~161,000 rows, the master
    constrained-vocabulary table keyed by Classpath. Loaded via pandas
    directly (an openpyxl unmerge pass would be slow at this size, and this
    sheet is not expected to contain merged cells).
    """
    sheet = wb_first_sheet(path)
    df = pd.read_excel(path, sheet_name=sheet)
    expected = ["Classpath", "Attribute Label", "Normalized Values"]
    missing = [
        c for c in expected if not any(c.lower() in str(col).lower() for col in df.columns)
    ]
    if missing:
        _warn(
            Path(path).name,
            sheet,
            f"Expected columns like {expected} not clearly found in "
            f"{list(df.columns)} — verify header row.",
        )
    return df.dropna(axis=0, how="all").reset_index(drop=True)


def load_faucets_lov(path: str) -> Dict[str, pd.DataFrame]:
    """FAUCETS_LOV.xlsx — worked category example, likely multiple sheets
    (summary, attribute detail, visual style guide). Every sheet is loaded
    with header detection and returned keyed by sheet name."""
    return _load_all_sheets(path)


def load_fittings_lov(path: str) -> Dict[str, pd.DataFrame]:
    """Fittings_LOV.xlsx — same multi-sheet pattern as Faucets."""
    return _load_all_sheets(path)


def load_1000_items(path: str) -> pd.DataFrame:
    """Sample-1000_Items.xlsx — 1,000 raw rows, 6 columns. Simple sheet,
    still routed through defensive loading for consistency."""
    return load_sheet_with_header_detection(
        path,
        wb_first_sheet(path),
        expected_header_hint=["Mfg_Part_Num", "Part_Desc"],
    )
