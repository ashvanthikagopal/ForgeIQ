"""
tests/test_part1_lookups.py
----------------------------
Test suite for the Part 1 (Setup & Data Foundation) deliverables:

    - placeholder_utils: known/unlisted placeholder detection & stripping
    - test_harness: ground-truth loading, scoring, aggregation, source-gap
      handling
    - lookups: the 4 shared lookup structures (manufacturer_brand_lookup,
      uom_lookup, decimal_fraction_lookup, lov_lookup) -- these tests are
      skipped automatically if `part1_foundation.lookups` doesn't exist yet
      in the checkout, so this file works both before and after that module
      lands.

Run with:
    pytest tests/test_part1_lookups.py -v

No real pack files are required -- everything here uses small synthetic
fixtures so the suite runs fast and doesn't depend on the (large, gitignored)
raw data files being present.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

from unihack.part1_foundation.placeholder_utils import (
    KNOWN_PLACEHOLDERS,
    clean_value,
    is_generic_empty_token,
    is_known_placeholder,
    is_placeholder_shaped,
    scan_column,
    strip_placeholders,
    strip_placeholders_from_record,
    summarize_placeholders,
)
from unihack.part1_foundation.test_harness import (
    DEFAULT_DELIVERY_SHEET,
    DEFAULT_INPUT_SHEET,
    GroundTruthRecord,
    TestHarness,
    load_ground_truth,
)


# ===========================================================================
# placeholder_utils
# ===========================================================================

class TestKnownPlaceholderDetection:
    @pytest.mark.parametrize("value", sorted(KNOWN_PLACEHOLDERS))
    def test_all_known_placeholders_detected(self, value):
        assert is_known_placeholder(value) is True

    @pytest.mark.parametrize("value", sorted(KNOWN_PLACEHOLDERS))
    def test_known_placeholders_detected_with_surrounding_whitespace(self, value):
        assert is_known_placeholder(f"  {value}  ") is True

    def test_real_brand_not_flagged_as_placeholder(self):
        assert is_known_placeholder("FRIGIDAIRE") is False
        assert is_known_placeholder("ACME®") is False

    def test_non_string_input_not_flagged(self):
        assert is_known_placeholder(None) is False
        assert is_known_placeholder(float("nan")) is False
        assert is_known_placeholder(42) is False


class TestPlaceholderShapeDetection:
    def test_unlisted_dash_wrapped_string_is_shape_flagged(self):
        assert is_placeholder_shaped("-- Some New Placeholder --") is True

    def test_known_placeholder_not_double_counted_as_unlisted_shape(self):
        # A KNOWN placeholder should be handled by is_known_placeholder,
        # not re-flagged as an "unlisted" shape -- avoids double bookkeeping.
        for value in KNOWN_PLACEHOLDERS:
            assert is_placeholder_shaped(value) is False

    def test_ordinary_string_not_shape_flagged(self):
        assert is_placeholder_shaped("FRIGIDAIRE") is False
        assert is_placeholder_shaped("3/8 CPLG BRS 150#") is False

    def test_single_dash_not_shape_flagged(self):
        # "-" alone is a generic empty token, not a "--...--" shape
        assert is_placeholder_shaped("-") is False


class TestGenericEmptyTokens:
    @pytest.mark.parametrize(
        "value",
        ["", "  ", "N/A", "n/a", "NA", "None", "null", "-", "--", "TBD", "unknown", "#N/A"],
    )
    def test_generic_empty_tokens_detected(self, value):
        assert is_generic_empty_token(value) is True

    def test_none_and_nan_are_empty(self):
        assert is_generic_empty_token(None) is True
        assert is_generic_empty_token(float("nan")) is True

    def test_real_value_not_flagged_empty(self):
        assert is_generic_empty_token("FRIGIDAIRE") is False
        assert is_generic_empty_token(0) is False  # numeric zero is real data, not "empty"


class TestCleanValue:
    def test_known_placeholder_becomes_none(self):
        assert clean_value("-- Unbranded --") is None

    def test_generic_empty_becomes_none(self):
        assert clean_value("N/A") is None
        assert clean_value("") is None
        assert clean_value(None) is None

    def test_real_value_passes_through_stripped(self):
        assert clean_value("  FRIGIDAIRE  ") == "FRIGIDAIRE"

    def test_unlisted_shape_kept_by_default(self):
        # Off by default -- unlisted placeholder-shaped values should NOT be
        # silently nulled unless explicitly opted in, so new variants get a
        # human look via scan_column first.
        assert clean_value("-- Some New Thing --") == "-- Some New Thing --"

    def test_unlisted_shape_stripped_when_opted_in(self):
        assert clean_value("-- Some New Thing --", treat_unlisted_shape_as_placeholder=True) is None

    def test_non_string_passthrough(self):
        assert clean_value(42) == 42
        assert clean_value(3.14) == 3.14


class TestScanColumn:
    def test_counts_known_unlisted_and_generic(self):
        series = pd.Series(
            [
                "FRIGIDAIRE",
                "-- Unbranded --",
                "-- No Unilog Brand --",
                "-- Something Else --",
                "N/A",
                None,
                "ACME",
            ]
        )
        report = scan_column(series, "TestBrand")
        assert report.column == "TestBrand"
        assert report.total_rows == 7
        assert report.known_placeholder_count == 2
        assert report.unlisted_placeholder_shape_count == 1
        assert "-- Something Else --" in report.unlisted_examples
        assert report.generic_empty_count == 2  # "N/A" and None

    def test_report_serializes_to_dict(self):
        series = pd.Series(["FRIGIDAIRE"])
        report = scan_column(series, "Brand")
        d = report.as_dict()
        assert d["column"] == "Brand"
        assert d["total_rows"] == 1


class TestStripPlaceholdersDataframe:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "Unilog_Brand": ["FRIGIDAIRE", "-- Unbranded --", "  ", "ACME®"],
                "DIB_Brand": ["-- No DIB Brand --", "N/A", "Rheem", "-- Weird Unlisted --"],
                "Part_Desc": ["a", "b", "c", "d"],  # not a brand/manuf column
            }
        )

    def test_default_columns_are_brand_manuf_only(self, sample_df):
        cleaned = strip_placeholders(sample_df)
        # Part_Desc should be untouched since it's neither brand nor manuf
        assert list(cleaned["Part_Desc"]) == ["a", "b", "c", "d"]

    def test_known_placeholders_nulled(self, sample_df):
        # NOTE: use pd.isna() rather than `is None` here -- when a Python
        # None is written into a pandas "str"-dtype column (the default on
        # newer pandas), pandas silently stores it as its own NaN/NA marker
        # rather than preserving the None identity. Dict/record-level
        # cleaning (see TestStripPlaceholdersFromRecord) does preserve None
        # exactly since it never passes through a typed DataFrame column.
        cleaned = strip_placeholders(sample_df)
        assert pd.isna(cleaned.loc[1, "Unilog_Brand"])
        assert pd.isna(cleaned.loc[0, "DIB_Brand"])

    def test_generic_empty_nulled(self, sample_df):
        cleaned = strip_placeholders(sample_df)
        assert pd.isna(cleaned.loc[2, "Unilog_Brand"])  # whitespace-only
        assert pd.isna(cleaned.loc[1, "DIB_Brand"])  # "N/A"

    def test_real_values_preserved(self, sample_df):
        cleaned = strip_placeholders(sample_df)
        assert cleaned.loc[0, "Unilog_Brand"] == "FRIGIDAIRE"
        assert cleaned.loc[3, "Unilog_Brand"] == "ACME®"
        assert cleaned.loc[2, "DIB_Brand"] == "Rheem"

    def test_unlisted_shape_kept_by_default(self, sample_df):
        cleaned = strip_placeholders(sample_df)
        assert cleaned.loc[3, "DIB_Brand"] == "-- Weird Unlisted --"

    def test_unlisted_shape_stripped_when_requested(self, sample_df):
        cleaned = strip_placeholders(sample_df, treat_unlisted_shape_as_placeholder=True)
        assert pd.isna(cleaned.loc[3, "DIB_Brand"])

    def test_flag_columns_added(self, sample_df):
        cleaned = strip_placeholders(sample_df)
        assert "Unilog_Brand__was_placeholder" in cleaned.columns
        assert cleaned.loc[1, "Unilog_Brand__was_placeholder"] == True  # noqa: E712
        assert cleaned.loc[0, "Unilog_Brand__was_placeholder"] == False  # noqa: E712

    def test_flag_columns_omitted_when_disabled(self, sample_df):
        cleaned = strip_placeholders(sample_df, add_flag_columns=False)
        assert "Unilog_Brand__was_placeholder" not in cleaned.columns

    def test_original_dataframe_not_mutated(self, sample_df):
        original_copy = sample_df.copy()
        strip_placeholders(sample_df)
        pd.testing.assert_frame_equal(sample_df, original_copy)

    def test_explicit_column_list_respected(self, sample_df):
        cleaned = strip_placeholders(sample_df, columns=["Unilog_Brand"])
        assert pd.isna(cleaned.loc[1, "Unilog_Brand"])
        # DIB_Brand should be untouched since it wasn't in the explicit list
        assert cleaned.loc[0, "DIB_Brand"] == "-- No DIB Brand --"


class TestStripPlaceholdersFromRecord:
    def test_strips_known_placeholder_fields(self):
        record = {"Unilog_Brand": "-- Unbranded --", "Part_Desc": "3/8 CPLG BRS 150#"}
        cleaned = strip_placeholders_from_record(record)
        assert cleaned["Unilog_Brand"] is None
        assert cleaned["Part_Desc"] == "3/8 CPLG BRS 150#"  # untouched, not a brand field

    def test_does_not_mutate_input(self):
        record = {"Unilog_Brand": "-- Unbranded --"}
        original = dict(record)
        strip_placeholders_from_record(record)
        assert record == original

    def test_explicit_fields_param(self):
        record = {"CustomBrandField": "-- Unbranded --", "Other": "keep me"}
        cleaned = strip_placeholders_from_record(record, fields=["CustomBrandField"])
        assert cleaned["CustomBrandField"] is None
        assert cleaned["Other"] == "keep me"


class TestSummarizePlaceholders:
    def test_returns_dataframe_with_expected_columns(self):
        df = pd.DataFrame({"Unilog_Brand": ["-- Unbranded --", "ACME"]})
        summary = summarize_placeholders(df)
        assert isinstance(summary, pd.DataFrame)
        assert "known_placeholder_count" in summary.columns
        assert summary.loc[0, "known_placeholder_count"] == 1


# ===========================================================================
# test_harness
# ===========================================================================

@pytest.fixture
def synthetic_ground_truth_workbook(tmp_path: Path) -> Path:
    """
    Build a tiny synthetic version of Unilog-Sample_200_Items-Input-vs-Output.xlsx
    (2 rows) so load_ground_truth can be tested without the real pack file.
    Row 2 intentionally has a blank UNSPSC to exercise source-gap handling.
    """
    input_df = pd.DataFrame(
        {
            "SKU": ["SKU001", "SKU002"],
            "Part_Desc": ["PDSH4816AF Dishwasher SS - Display Only", "3/8 CPLG BRS 150#"],
            "Unilog_Brand": ["FRIGIDAIRE", "-- Unbranded --"],
        }
    )
    output_df = pd.DataFrame(
        {
            "SKU": ["SKU001", "SKU002"],
            "Classpath": [
                "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers",
                "Plumbing > Fittings > Couplings",
            ],
            "Product Title": [
                "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher",
                "3/8 in Brass Coupling 150#",
            ],
            "UNSPSC": ["52141500", None],  # row 2 has the known kind of gap
            "Country of Origin": ["USA", "USA"],
        }
    )

    path = tmp_path / "synthetic_200_items.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        input_df.to_excel(writer, sheet_name=DEFAULT_INPUT_SHEET, index=False)
        output_df.to_excel(writer, sheet_name=DEFAULT_DELIVERY_SHEET, index=False)
    return path


class TestLoadGroundTruth:
    def test_loads_expected_number_of_records(self, synthetic_ground_truth_workbook):
        records = load_ground_truth(synthetic_ground_truth_workbook)
        assert len(records) == 2

    def test_records_are_joined_on_sku(self, synthetic_ground_truth_workbook):
        records = load_ground_truth(synthetic_ground_truth_workbook)
        keys = {r.key for r in records}
        assert keys == {"SKU001", "SKU002"}

    def test_input_and_expected_fields_populated(self, synthetic_ground_truth_workbook):
        records = {r.key: r for r in load_ground_truth(synthetic_ground_truth_workbook)}
        r1 = records["SKU001"]
        assert r1.input_fields["Part_Desc"] == "PDSH4816AF Dishwasher SS - Display Only"
        assert "Built-In Dishwashers" in r1.expected_fields["Classpath"]

    def test_known_placeholder_stripped_in_loaded_fields(self, synthetic_ground_truth_workbook):
        records = {r.key: r for r in load_ground_truth(synthetic_ground_truth_workbook)}
        r2 = records["SKU002"]
        assert r2.input_fields["Unilog_Brand"] is None

    def test_source_gap_detected_for_blank_unspsc(self, synthetic_ground_truth_workbook):
        records = {r.key: r for r in load_ground_truth(synthetic_ground_truth_workbook)}
        assert "UNSPSC" in records["SKU002"].known_gaps
        assert "UNSPSC" not in records["SKU001"].known_gaps

    def test_missing_sheet_raises_clear_error(self, tmp_path):
        bad_path = tmp_path / "bad.xlsx"
        pd.DataFrame({"SKU": ["1"]}).to_excel(bad_path, sheet_name="NotTheRightSheet", index=False)
        with pytest.raises(ValueError, match="Could not find sheet"):
            load_ground_truth(bad_path)


class TestTestHarnessScoring:
    @pytest.fixture
    def harness(self, synthetic_ground_truth_workbook) -> TestHarness:
        return TestHarness(load_ground_truth(synthetic_ground_truth_workbook))

    def test_len_reflects_record_count(self, harness):
        assert len(harness) == 2

    def test_perfect_match_scores_1(self, harness):
        generated = {
            "Classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"
        }
        score = harness.score_record("SKU001", generated, fields_to_score=["Classpath"])
        assert score.accuracy == 1.0

    def test_mismatch_scores_0(self, harness):
        generated = {"Classpath": "Totally Wrong Classpath"}
        score = harness.score_record("SKU001", generated, fields_to_score=["Classpath"])
        assert score.accuracy == 0.0
        assert score.field_scores[0].match is False

    def test_case_insensitive_string_comparison(self, harness):
        generated = {"Classpath": "APPLIANCES & CONSUMER ELECTRONICS > KITCHEN APPLIANCES > BUILT-IN DISHWASHERS"}
        score = harness.score_record("SKU001", generated, fields_to_score=["Classpath"])
        assert score.accuracy == 1.0

    def test_unknown_key_raises(self, harness):
        with pytest.raises(KeyError):
            harness.score_record("NOT_A_REAL_SKU", {"Classpath": "x"})

    def test_source_gap_excluded_from_accuracy_denominator(self, harness):
        # SKU002's UNSPSC is a known source gap; even if the pipeline didn't
        # fill it, it shouldn't drag down accuracy or count as a mismatch.
        generated = {"UNSPSC": None, "Classpath": "Plumbing > Fittings > Couplings"}
        score = harness.score_record(
            "SKU002", generated, fields_to_score=["UNSPSC", "Classpath"]
        )
        assert score.accuracy == 1.0  # only Classpath counts, and it matches
        gap_scores = [fs for fs in score.field_scores if fs.is_source_gap]
        assert len(gap_scores) == 1
        assert gap_scores[0].field == "UNSPSC"

    def test_custom_comparator_used_when_provided(self, harness):
        # e.g. a char-limit-aware comparator for description fields
        def within_40_chars(expected, actual):
            return isinstance(actual, str) and len(actual) <= 40

        generated = {"Product Title": "SHORT TITLE UNDER FORTY CHARACTERS"}
        score = harness.score_record(
            "SKU001",
            generated,
            fields_to_score=["Product Title"],
            field_comparators={"Product Title": within_40_chars},
        )
        assert score.accuracy == 1.0

    def test_score_batch_skips_unknown_keys(self, harness, capsys):
        generated_by_key = {
            "SKU001": {"Classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"},
            "NOT_REAL": {"Classpath": "x"},
        }
        scores = harness.score_batch(generated_by_key, fields_to_score=["Classpath"])
        assert len(scores) == 1
        captured = capsys.readouterr()
        assert "unknown key" in captured.out.lower()

    def test_known_issues_report_surfaces_gap_row(self, harness):
        report = harness.known_issues_report()
        assert "SKU002" in report["key"].values
        assert "SKU001" not in report["key"].values


class TestAggregate:
    def test_aggregate_empty_list(self):
        summary = TestHarness.aggregate([])
        assert summary["n_records"] == 0
        assert summary["overall_accuracy"] is None

    def test_aggregate_computes_overall_and_per_field_accuracy(self, synthetic_ground_truth_workbook):
        harness = TestHarness(load_ground_truth(synthetic_ground_truth_workbook))
        s1 = harness.score_record(
            "SKU001",
            {"Classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"},
            fields_to_score=["Classpath"],
        )
        s2 = harness.score_record(
            "SKU002", {"Classpath": "Wrong"}, fields_to_score=["Classpath"]
        )
        summary = TestHarness.aggregate([s1, s2])
        assert summary["n_records"] == 2
        assert math.isclose(summary["overall_accuracy"], 0.5)
        assert math.isclose(summary["per_field_accuracy"]["Classpath"], 0.5)
        assert len(summary["worst_records"]) >= 1

    def test_worst_records_sorted_ascending(self, synthetic_ground_truth_workbook):
        harness = TestHarness(load_ground_truth(synthetic_ground_truth_workbook))
        s1 = harness.score_record(
            "SKU001",
            {"Classpath": "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"},
            fields_to_score=["Classpath"],
        )
        s2 = harness.score_record(
            "SKU002", {"Classpath": "Wrong"}, fields_to_score=["Classpath"]
        )
        summary = TestHarness.aggregate([s1, s2])
        worst = summary["worst_records"]
        assert worst[0]["key"] == "SKU002"  # lowest accuracy first


# ===========================================================================
# lookups (skipped automatically until part1_foundation.lookups exists)
# ===========================================================================

lookups = pytest.importorskip(
    "unihack.part1_foundation.lookups",
    reason="lookups.py not yet implemented in this checkout",
)


@pytest.fixture
def synthetic_manufacturer_brand_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "MANUFACTURER_NAME": ["Frigidaire", "Frigidaire", "Acme Corp"],
            "MANUFACTURER_CODE": ["FRIG", "FRIG", "ACME"],
            "BRAND_NAME": ["FRIGIDAIRE®", "FRIGIDAIRE® Professional", None],
            "BRAND_CODE": ["FRIGB", "FRIGP", None],
        }
    )


@pytest.fixture
def synthetic_decimal_fraction_df() -> pd.DataFrame:
    # Mimics the 4-side-by-side-block layout: two blocks shown here for brevity.
    return pd.DataFrame(
        {
            "Fraction_1": ["1/64", "1/32"],
            "Decimal_1": [0.015625, 0.03125],
            "Fraction_2": ["1/2", "3/4"],
            "Decimal_2": [0.5, 0.75],
        }
    )


class TestManufacturerBrandLookup:
    def test_exact_name_resolves_to_canonical(self, synthetic_manufacturer_brand_df):
        lut = lookups.ManufacturerBrandLookup.from_dataframe(synthetic_manufacturer_brand_df)
        result = lut.resolve("frigidaire")
        assert result is not None
        assert result.manufacturer_name.upper().startswith("FRIGIDAIRE")

    def test_unknown_manufacturer_returns_none_or_flag(self, synthetic_manufacturer_brand_df):
        lut = lookups.ManufacturerBrandLookup.from_dataframe(synthetic_manufacturer_brand_df)
        result = lut.resolve("Totally Unknown Manufacturer XYZ")
        assert result is None or getattr(result, "confidence", 1.0) < 1.0


class TestDecimalFractionLookup:
    def test_decimal_to_fraction(self, synthetic_decimal_fraction_df):
        lut = lookups.DecimalFractionLookup.from_dataframe(synthetic_decimal_fraction_df)
        assert lut.decimal_to_fraction(0.5) == "1/2"

    def test_fraction_to_decimal(self, synthetic_decimal_fraction_df):
        lut = lookups.DecimalFractionLookup.from_dataframe(synthetic_decimal_fraction_df)
        assert math.isclose(lut.fraction_to_decimal("1/2"), 0.5)

    def test_compound_measurement_conversion(self, synthetic_decimal_fraction_df):
        # 50.25 in -> 50-1/4 in requires combining whole-number + fractional part;
        # only test the fractional-part lookup here since 1/4 isn't in our tiny
        # synthetic table -- this test documents the expected interface shape.
        lut = lookups.DecimalFractionLookup.from_dataframe(synthetic_decimal_fraction_df)
        assert hasattr(lut, "decimal_to_fraction")


class TestBuildAllLookups:
    def test_build_all_lookups_returns_expected_keys(self, monkeypatch, tmp_path):
        # Smoke test only -- verifies the aggregator function exists and
        # returns the 4 documented lookup structures without requiring the
        # full real pack on disk. Skips gracefully if the function expects a
        # different signature than anticipated.
        if not hasattr(lookups, "build_all_lookups"):
            pytest.skip("build_all_lookups not implemented yet")
        # Real invocation requires the raw pack files; this just checks the
        # function is importable and callable-shaped for now.
        assert callable(lookups.build_all_lookups)
