from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any


def normalize_text(value: str) -> str:
    value = str(value or "").lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^a-z0-9 ]", "", value)
    return value


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b),
    ).ratio()


def are_likely_duplicates(
    row_a: dict[str, Any],
    row_b: dict[str, Any],
    description_threshold: float = 0.92,
) -> bool:

    mpn_a = normalize_text(row_a.get("Mfg_Part_Num", ""))
    mpn_b = normalize_text(row_b.get("Mfg_Part_Num", ""))

    if mpn_a and mpn_b and mpn_a == mpn_b:
        return True

    desc_a = row_a.get("Part_Desc", "")
    desc_b = row_b.get("Part_Desc", "")

    return similarity(desc_a, desc_b) >= description_threshold


def find_duplicate_candidates(
    products: list[dict[str, Any]],
    threshold: float = 0.92,
) -> list[tuple[int, int, float]]:

    candidates = []

    for i in range(len(products)):
        for j in range(i + 1, len(products)):

            mpn_a = normalize_text(
                products[i].get("Mfg_Part_Num", "")
            )

            mpn_b = normalize_text(
                products[j].get("Mfg_Part_Num", "")
            )

            if mpn_a and mpn_b and mpn_a == mpn_b:
                candidates.append((i, j, 1.0))
                continue

            score = similarity(
                products[i].get("Part_Desc", ""),
                products[j].get("Part_Desc", ""),
            )

            if score >= threshold:
                candidates.append((i, j, score))

    return candidates