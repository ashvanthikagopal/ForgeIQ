from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from unihack.schemas import ClassificationResult
from .prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        ...


def build_classification_prompt(
    part_desc: str,
    mpn: str,
    manufacturer: str,
    allowed_classpaths: list[str],
) -> str:
    return CLASSIFICATION_USER_TEMPLATE.format(
        part_desc=part_desc or "",
        mpn=mpn or "",
        manufacturer=manufacturer or "",
        allowed_classpaths="\n".join(
            f"- {classpath}" for classpath in allowed_classpaths
        ),
    )


def validate_classification(
    result: dict[str, Any],
    allowed_classpaths: list[str],
) -> ClassificationResult:
    classpath = result.get("classpath")
    confidence = result.get("confidence", 0.0)
    alternatives = result.get("alternative_candidates", [])
    reasoning = result.get("reasoning", "")

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    if not isinstance(alternatives, list):
        alternatives = []

    alternatives = [
        str(x)
        for x in alternatives
        if str(x) in allowed_classpaths
    ]

    if classpath not in allowed_classpaths:
        return ClassificationResult(
            classpath=None,
            confidence=0.0,
            alternative_candidates=alternatives,
            reasoning=reasoning,
            needs_review=True,
            validation_error=(
                "Model returned a Classpath that is not present "
                "in the allowed Classpath list."
            ),
        )

    needs_review = confidence < 0.5

    return ClassificationResult(
        classpath=classpath,
        confidence=confidence,
        alternative_candidates=alternatives[:3],
        reasoning=reasoning,
        needs_review=needs_review,
    )


def classify_product(
    product: dict[str, Any],
    allowed_classpaths: list[str],
    llm: LLMClient,
) -> ClassificationResult:

    if not allowed_classpaths:
        return ClassificationResult(
            classpath=None,
            confidence=0.0,
            needs_review=True,
            validation_error="No allowed Classpaths were supplied.",
        )

    part_desc = str(product.get("Part_Desc", "") or "")
    mpn = str(product.get("Mfg_Part_Num", "") or "")
    manufacturer = str(
        product.get("Part_Manuf", "")
        or product.get("Manufacturer", "")
        or ""
    )

    prompt = build_classification_prompt(
        part_desc=part_desc,
        mpn=mpn,
        manufacturer=manufacturer,
        allowed_classpaths=allowed_classpaths,
    )

    try:
        raw_result = llm.generate_json(
            system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
            user_prompt=prompt,
        )
    except Exception as exc:
        logger.exception("Classification failed")
        return ClassificationResult(
            classpath=None,
            confidence=0.0,
            needs_review=True,
            validation_error=f"LLM classification error: {exc}",
        )

    return validate_classification(
        result=raw_result,
        allowed_classpaths=allowed_classpaths,
    )


def classify_batch(
    products: list[dict[str, Any]],
    allowed_classpaths: list[str],
    llm: LLMClient,
) -> list[ClassificationResult]:

    results = []

    for product in products:
        results.append(
            classify_product(
                product=product,
                allowed_classpaths=allowed_classpaths,
                llm=llm,
            )
        )

    return results