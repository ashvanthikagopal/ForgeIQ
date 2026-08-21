from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ============================================================
# FIELD COMPARISON
# ============================================================

@dataclass
class FieldComparison:

    field: str

    expected: object

    actual: object

    matched: bool


# ============================================================
# RECORD SCORE
# ============================================================

@dataclass
class RecordScore:

    total_fields: int

    matched_fields: int

    accuracy: float

    comparisons: list[
        FieldComparison
    ]


# ============================================================
# GROUND TRUTH HARNESS
# ============================================================

class GroundTruthHarness:

    def __init__(
        self,
        input_df: pd.DataFrame,
        expected_df: pd.DataFrame,
    ):

        self.input_df = input_df

        self.expected_df = expected_df

        # ----------------------------------------------------
        # Build MPN index when available
        # ----------------------------------------------------

        self.expected_by_mpn = {}

        if (
            "Mfg_Part_Num"
            in expected_df.columns
        ):

            for _, row in (
                expected_df.iterrows()
            ):

                mpn = row.get(
                    "Mfg_Part_Num"
                )

                if pd.isna(mpn):
                    continue

                mpn_key = (
                    str(mpn)
                    .strip()
                    .lower()
                )

                if mpn_key:

                    self.expected_by_mpn[
                        mpn_key
                    ] = row

    # ========================================================
    # FIND EXPECTED RECORD BY MPN
    # ========================================================

    def find_expected_record(
        self,
        mpn: str,
    ):

        if not mpn:
            return None

        key = (
            str(mpn)
            .strip()
            .lower()
        )

        return (
            self
            .expected_by_mpn
            .get(key)
        )

    # ========================================================
    # COMPARE BY MPN
    # ========================================================

    def compare_by_mpn(
        self,
        mpn: str,
        generated: dict,
    ) -> RecordScore | None:

        expected_row = (
            self
            .find_expected_record(
                mpn
            )
        )

        if expected_row is None:

            return None

        return self._compare_row(
            expected_row,
            generated,
        )

    # ========================================================
    # COMPARE RECORD BY INDEX
    # ========================================================

    def compare_record(
        self,
        index: int,
        generated: dict,
    ) -> RecordScore:

        expected_row = (
            self
            .expected_df
            .iloc[index]
        )

        return self._compare_row(
            expected_row,
            generated,
        )

    # ========================================================
    # INTERNAL COMPARISON
    # ========================================================

    def _compare_row(
        self,
        expected_row,
        generated: dict,
    ) -> RecordScore:

        comparisons = []

        for field, actual in (
            generated.items()
        ):

            expected = (
                expected_row.get(
                    field
                )
            )

            # ------------------------------------------------
            # Normalize expected
            # ------------------------------------------------

            if pd.isna(
                expected
            ):

                expected = ""

            # ------------------------------------------------
            # Normalize actual
            # ------------------------------------------------

            if actual is None:

                actual = ""

            expected_text = str(
                expected
            ).strip()

            actual_text = str(
                actual
            ).strip()

            matched = (
                expected_text
                ==
                actual_text
            )

            comparisons.append(
                FieldComparison(
                    field=field,
                    expected=expected,
                    actual=actual,
                    matched=matched,
                )
            )

        total = len(
            comparisons
        )

        matched = sum(
            comparison.matched
            for comparison
            in comparisons
        )

        accuracy = (
            matched / total
            if total
            else 0.0
        )

        return RecordScore(
            total_fields=total,
            matched_fields=matched,
            accuracy=accuracy,
            comparisons=comparisons,
        )

    # ========================================================
    # COMPARE SINGLE FIELD
    # ========================================================

    def compare_field(
        self,
        index: int,
        field: str,
        actual,
    ) -> bool:

        expected = (
            self
            .expected_df
            .iloc[index]
            .get(
                field
            )
        )

        if pd.isna(
            expected
        ):

            expected = ""

        if actual is None:

            actual = ""

        return (
            str(expected).strip()
            ==
            str(actual).strip()
        )