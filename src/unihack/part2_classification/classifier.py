from __future__ import annotations

import re

from .models import (
    ClassificationResult,
)


class TaxonomyClassifier:

    def __init__(
        self,
        allowed_classpaths: list[str] | None = None,
    ):

        self.allowed_classpaths = [
            value.strip()
            for value in (
                allowed_classpaths or []
            )
            if value
            and value.strip()
        ]

    # ========================================================
    # CLASSIFY
    # ========================================================

    def classify(
        self,
        part_desc: str,
        mpn: str = "",
        manufacturer: str = "",
    ) -> ClassificationResult:

        # ----------------------------------------------------
        # No LOV
        # ----------------------------------------------------

        if not self.allowed_classpaths:

            return ClassificationResult(

                classpath="",

                confidence=0.0,

                alternative_candidates=[],

                reasoning=(
                    "No allowed Classpath "
                    "taxonomy is available."
                ),

                needs_review=True,

                review_reason=(
                    "Classification requires "
                    "the Part 1 LOV Classpath list."
                ),
            )

        # ----------------------------------------------------
        # Build searchable text
        # ----------------------------------------------------

        text = " ".join(
            [
                part_desc or "",
                manufacturer or "",
            ]
        ).lower()

        scored = []

        # ----------------------------------------------------
        # Score only allowed classpaths
        # ----------------------------------------------------

        for classpath in (
            self.allowed_classpaths
        ):

            words = re.findall(
                r"[a-z0-9]+",
                classpath.lower(),
            )

            score = sum(
                1
                for word in words
                if len(word) > 2
                and word in text
            )

            if score > 0:

                scored.append(
                    (
                        score,
                        classpath,
                    )
                )

        # ----------------------------------------------------
        # Nothing matched
        # ----------------------------------------------------

        if not scored:

            return ClassificationResult(

                classpath="",

                confidence=0.0,

                alternative_candidates=[],

                reasoning=(
                    "No allowed Classpath "
                    "matched the product text."
                ),

                needs_review=True,

                review_reason=(
                    "No suitable Classpath "
                    "was identified."
                ),
            )

        # ----------------------------------------------------
        # Best match
        # ----------------------------------------------------

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        best_score = scored[0][0]

        best_classpath = scored[0][1]

        alternatives = [
            item[1]
            for item in scored[1:4]
        ]

        confidence = min(
            0.95,
            0.40 + (
                best_score * 0.15
            ),
        )

        needs_review = (
            confidence < 0.5
        )

        return ClassificationResult(

            classpath=best_classpath,

            confidence=confidence,

            alternative_candidates=(
                alternatives
            ),

            reasoning=(
                "Selected the best matching "
                "Classpath from the allowed "
                "taxonomy."
            ),

            needs_review=needs_review,

            review_reason=(
                "Low classification confidence."
                if needs_review
                else None
            ),
        )