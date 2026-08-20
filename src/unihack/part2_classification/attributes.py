from __future__ import annotations

import logging
from typing import Any, Protocol

from unihack.schemas import AttributeResult
from .prompts import (
    ATTRIBUTE_SYSTEM_PROMPT,
    ATTRIBUTE_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        ...


def build_attribute_rules(
    attributes: dict[str, list[str]],
) -> str:

    lines = []

    for attribute, permitted_values in attributes.items():
        lines.append(f"ATTRIBUTE: {attribute}")

        if permitted_values:
            lines.append("PERMITTED VALUES:")
            for value in permitted_values:
                lines.append(f"  - {value}")

        lines.append("")

    return "\n".join(lines)


def build_attribute_prompt(
    classpath: str,
    source_text: str,
    attributes: dict[str, list[str]],
) -> str:

    return ATTRIBUTE_USER_TEMPLATE.format(
        classpath=classpath,
        source_text=source_text,
        attribute_rules=build_attribute_rules(attributes),
    )


def validate_attribute(
    raw_attribute: dict[str, Any],
    permitted_values: dict[str, list[str]],
) -> AttributeResult | None:

    attribute = str(raw_attribute.get("attribute", "")).strip()
    value = str(raw_attribute.get("value", "")).strip()

    if not attribute or not value:
        return None

    confidence = raw_attribute.get("confidence", 0.0)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    needs_unit_normalization = bool(
        raw_attribute.get("needs_unit_normalization", False)
    )

    raw_text_span = str(
        raw_attribute.get("raw_text_span", "")
    ).strip()

    allowed = permitted_values.get(attribute, [])

    # Unit-bearing values are deliberately allowed to remain raw.
    if needs_unit_normalization:
        needs_review = confidence < 0.5

        return AttributeResult(
            attribute=attribute,
            value=value,
            confidence=confidence,
            needs_unit_normalization=True,
            raw_text_span=raw_text_span,
            needs_review=needs_review,
        )

    # Non-unit values MUST exist in the LOV.
    if value not in allowed:
        return AttributeResult(
            attribute=attribute,
            value=value,
            confidence=0.0,
            needs_unit_normalization=False,
            raw_text_span=raw_text_span,
            needs_review=True,
            validation_error=(
                f"Value '{value}' is not permitted for "
                f"attribute '{attribute}'."
            ),
        )

    return AttributeResult(
        attribute=attribute,
        value=value,
        confidence=confidence,
        needs_unit_normalization=False,
        raw_text_span=raw_text_span,
        needs_review=confidence < 0.5,
    )


def extract_attributes(
    classpath: str,
    source_text: str,
    permitted_values: dict[str, list[str]],
    llm: LLMClient,
) -> list[AttributeResult]:

    if not classpath:
        return []

    if not source_text.strip():
        return []

    prompt = build_attribute_prompt(
        classpath=classpath,
        source_text=source_text,
        attributes=permitted_values,
    )

    try:
        response = llm.generate_json(
            system_prompt=ATTRIBUTE_SYSTEM_PROMPT,
            user_prompt=prompt,
        )
    except Exception as exc:
        logger.exception("Attribute extraction failed")

        return [
            AttributeResult(
                attribute="__SYSTEM__",
                value="",
                confidence=0.0,
                needs_unit_normalization=False,
                raw_text_span="",
                needs_review=True,
                validation_error=str(exc),
            )
        ]

    raw_attributes = response.get("attributes", [])

    if not isinstance(raw_attributes, list):
        return []

    results = []

    for raw_attribute in raw_attributes:
        if not isinstance(raw_attribute, dict):
            continue

        result = validate_attribute(
            raw_attribute=raw_attribute,
            permitted_values=permitted_values,
        )

        if result is not None:
            results.append(result)

    return results