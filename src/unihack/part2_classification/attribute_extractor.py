from __future__ import annotations

import re

from .models import (
    AttributeResult,
)


class LOVAttributeExtractor:

    def __init__(
        self,
        lov_lookup,
    ):

        self.lov_lookup = lov_lookup

    # ========================================================
    # EXTRACT
    # ========================================================

    def extract(
        self,
        classpath: str,
        part_desc: str,
    ) -> list[AttributeResult]:

        if not classpath:

            return []

        if self.lov_lookup is None:

            return []

        class_data = (
            self
            .lov_lookup
            .get_classpath(
                classpath
            )
        )

        if not class_data:

            return []

        results = []

        text = (
            part_desc or ""
        )

        text_lower = (
            text.lower()
        )

        for (
            attribute_name,
            definition,
        ) in class_data.items():

            permitted_values = (
                definition
                .normalized_values
            )

            for value in (
                permitted_values
            ):

                if (
                    value.lower()
                    not in text_lower
                ):

                    continue

                raw_span = (
                    self._find_raw_span(
                        text,
                        value,
                    )
                )

                needs_unit = (
                    self
                    ._looks_like_measurement(
                        raw_span
                    )
                )

                results.append(
                    AttributeResult(

                        attribute=(
                            attribute_name
                        ),

                        value=value,

                        confidence=0.95,

                        needs_unit_normalization=(
                            needs_unit
                        ),

                        raw_text_span=(
                            raw_span
                        ),
                    )
                )

                break

        return results

    # ========================================================
    # FIND RAW TEXT
    # ========================================================

    @staticmethod
    def _find_raw_span(
        text: str,
        value: str,
    ) -> str:

        match = re.search(
            re.escape(value),
            text,
            re.IGNORECASE,
        )

        if match:

            return match.group(0)

        return value

    # ========================================================
    # CHECK UNIT
    # ========================================================

    @staticmethod
    def _looks_like_measurement(
        value: str,
    ) -> bool:

        return bool(
            re.search(
                r"\d+(?:\.\d+)?\s*"
                r"(?:in|inch|inches|mm|cm|ft|"
                r"lb|lbs|oz|psi|v|w)\b",
                value,
                re.IGNORECASE,
            )
        )