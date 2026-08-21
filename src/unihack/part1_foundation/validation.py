from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .data_loader import (
    Part1Data,
)


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class ValidationResult:

    name: str

    passed: bool

    message: str


# ============================================================
# PART 1 VALIDATOR
# ============================================================

class Part1Validator:

    REQUIRED_INPUT_COLUMNS = [
        "Mfg_Part_Num",
        "Part_Desc",
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand",
        "Part_Manuf",
    ]

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        data: Part1Data,
    ):

        self.data = data

    # ========================================================
    # RUN ALL VALIDATIONS
    # ========================================================

    def validate(self) -> list[
        ValidationResult
    ]:

        results = []

        results.append(
            self.validate_input_exists()
        )

        results.append(
            self.validate_input_columns()
        )

        results.append(
            self.validate_input_rows()
        )

        results.append(
            self.validate_part_numbers()
        )

        results.append(
            self.validate_descriptions()
        )

        return results

    # ========================================================
    # INPUT EXISTS
    # ========================================================

    def validate_input_exists(
        self,
    ) -> ValidationResult:

        if self.data.sample_input is None:

            return ValidationResult(
                name="Input dataset",
                passed=False,
                message=(
                    "Input dataset was not loaded"
                ),
            )

        return ValidationResult(
            name="Input dataset",
            passed=True,
            message=(
                "Input dataset loaded successfully"
            ),
        )

    # ========================================================
    # INPUT COLUMNS
    # ========================================================

    def validate_input_columns(
        self,
    ) -> ValidationResult:

        columns = list(
            self
            .data
            .sample_input
            .columns
        )

        missing = [
            column
            for column
            in self.REQUIRED_INPUT_COLUMNS
            if column not in columns
        ]

        if missing:

            return ValidationResult(
                name="Input schema",
                passed=False,
                message=(
                    "Missing columns: "
                    f"{missing}"
                ),
            )

        return ValidationResult(
            name="Input schema",
            passed=True,
            message=(
                "All required columns are present"
            ),
        )

    # ========================================================
    # INPUT ROWS
    # ========================================================

    def validate_input_rows(
        self,
    ) -> ValidationResult:

        row_count = len(
            self
            .data
            .sample_input
        )

        if row_count == 0:

            return ValidationResult(
                name="Input rows",
                passed=False,
                message=(
                    "Input dataset contains "
                    "zero rows"
                ),
            )

        return ValidationResult(
            name="Input rows",
            passed=True,
            message=(
                f"{row_count} input records loaded"
            ),
        )

    # ========================================================
    # PART NUMBER
    # ========================================================

    def validate_part_numbers(
        self,
    ) -> ValidationResult:

        df = self.data.sample_input

        if "Mfg_Part_Num" not in df.columns:

            return ValidationResult(
                name="Manufacturer part number",
                passed=False,
                message=(
                    "Mfg_Part_Num column missing"
                ),
            )

        missing_count = (
            df["Mfg_Part_Num"]
            .isna()
            .sum()
        )

        if missing_count > 0:

            return ValidationResult(
                name="Manufacturer part number",
                passed=False,
                message=(
                    f"{missing_count} records "
                    "have missing part numbers"
                ),
            )

        return ValidationResult(
            name="Manufacturer part number",
            passed=True,
            message=(
                "All records contain "
                "a manufacturer part number"
            ),
        )

    # ========================================================
    # DESCRIPTION
    # ========================================================

    def validate_descriptions(
        self,
    ) -> ValidationResult:

        df = self.data.sample_input

        if "Part_Desc" not in df.columns:

            return ValidationResult(
                name="Part description",
                passed=False,
                message=(
                    "Part_Desc column missing"
                ),
            )

        missing_count = (
            df["Part_Desc"]
            .isna()
            .sum()
        )

        if missing_count > 0:

            return ValidationResult(
                name="Part description",
                passed=False,
                message=(
                    f"{missing_count} records "
                    "have missing descriptions"
                ),
            )

        return ValidationResult(
            name="Part description",
            passed=True,
            message=(
                "All records contain "
                "a part description"
            ),
        )


# ============================================================
# PRINT VALIDATION REPORT
# ============================================================

def print_validation_report(
    data: Part1Data,
) -> bool:

    validator = Part1Validator(
        data
    )

    results = (
        validator.validate()
    )

    print()
    print("=" * 65)
    print("PART 1 VALIDATION REPORT")
    print("=" * 65)

    all_passed = True

    for result in results:

        status = (
            "PASS"
            if result.passed
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{result.name}: "
            f"{result.message}"
        )

        if not result.passed:

            all_passed = False

    # ========================================================
    # LOOKUP SOURCE REPORT
    # ========================================================

    print()
    print("LOOKUP SOURCE STATUS")
    print("-" * 65)

    for (
        name,
        source,
    ) in data.lookup_sources.items():

        if source.has_data:

            status = "AVAILABLE"

        elif source.exists:

            status = "EMPTY"

        else:

            status = "MISSING"

        print(
            f"[{status}] "
            f"{name}: "
            f"{source.message}"
        )

    print()
    print("=" * 65)

    if all_passed:

        print(
            "PART 1 CORE VALIDATION: PASS"
        )

    else:

        print(
            "PART 1 CORE VALIDATION: FAIL"
        )

    print("=" * 65)

    return all_passed