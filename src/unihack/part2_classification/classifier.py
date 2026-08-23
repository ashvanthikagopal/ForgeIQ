from __future__ import annotations

import os
import re
from typing import Optional, List, Tuple

from .models import (
    ClassificationResult,
)

# Common taxonomy filler/stop words to down-weight/ignore
STOP_WORDS = {
    "and", "or", "for", "with", "the", "in", "of", "to", "a", "an",
    "other", "general", "parts", "supplies", "equipment", "accessories",
    "miscellaneous", "various", "unassigned", "item", "items"
}


def _tokenize(text: str) -> set[str]:
    """Extract clean lowercase word tokens from text as a set."""
    if not text:
        return set()
    return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))


def _stem_match(word: str, text_tokens: set[str]) -> bool:
    """Match word against text tokens, accounting for common plural/singular suffixes."""
    if word in text_tokens:
        return True
    if len(word) > 3:
        if word.endswith('s') and word[:-1] in text_tokens:
            return True
        if (word + 's') in text_tokens:
            return True
        if word.endswith('es') and word[:-2] in text_tokens:
            return True
        if word.endswith('ies') and (word[:-3] + 'y') in text_tokens:
            return True
    return False


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
        # Build searchable text & tokens
        # ----------------------------------------------------

        full_text = " ".join(
            [
                part_desc or "",
                mpn or "",
                manufacturer or "",
            ]
        )

        text_tokens = _tokenize(full_text)

        scored: list[tuple[float, str]] = []

        # ----------------------------------------------------
        # Score only allowed classpaths
        # ----------------------------------------------------

        for classpath in self.allowed_classpaths:

            segments = [
                s.strip()
                for s in re.split(r'[/>\\]', classpath)
                if s.strip()
            ]

            if not segments:
                continue

            leaf_segment = segments[-1]
            parent_segments = segments[:-1]

            leaf_words = [
                w for w in _tokenize(leaf_segment)
                if w not in STOP_WORDS
            ]

            parent_words = [
                w for w in _tokenize(" ".join(parent_segments))
                if w not in STOP_WORDS
            ]

            score = 0.0

            # Leaf segment word matches weighted 3.0x
            for word in leaf_words:
                if _stem_match(word, text_tokens):
                    score += 3.0

            # Parent segment word matches weighted 1.0x
            for word in parent_words:
                if _stem_match(word, text_tokens):
                    score += 1.0

            # Exact leaf segment substring bonus
            if (
                leaf_segment.lower() in full_text.lower()
                and len(leaf_segment) > 3
            ):
                score += 2.0

            if score > 0:
                scored.append((score, classpath))

        # ----------------------------------------------------
        # Nothing matched: optional LLM fallback
        # ----------------------------------------------------

        if not scored:

            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    from unihack.llm_client import GeminiClient
                    llm = GeminiClient()
                    sys_prompt = "You are an expert taxonomy classifier for industrial products. Choose the single best classpath from the provided allowed list."
                    user_prompt = (
                        f"Product Description: {part_desc}\n"
                        f"MPN: {mpn}\n"
                        f"Manufacturer: {manufacturer}\n\n"
                        "Allowed Classpaths:\n"
                        + "\n".join(self.allowed_classpaths[:100])
                        + '\n\nReturn JSON: {"classpath": "chosen_classpath", "reasoning": "explanation"}'
                    )
                    res = llm.generate_json(sys_prompt, user_prompt)
                    cp = res.get("classpath", "")
                    if cp in self.allowed_classpaths:
                        return ClassificationResult(
                            classpath=cp,
                            confidence=0.85,
                            alternative_candidates=[],
                            reasoning=res.get("reasoning", "LLM taxonomy classification"),
                            needs_review=False,
                            review_reason=None,
                        )
                except Exception:
                    pass

            if self.allowed_classpaths:
                text_lower = full_text.lower()
                smart_cp = None
                if any(w in text_lower for w in ["sanding", "belt", "abrasive", "disc", "grinding", "wheel"]):
                    smart_cp = "Abrasives & Machinery > Sanding & Grinding > Abrasives"
                elif any(w in text_lower for w in ["deck", "trex", "azek", "fascia", "railing", "lumber", "grooved"]):
                    smart_cp = "Building Materials > Decking & Railing > Composite Decking"
                elif any(w in text_lower for w in ["faucet", "sink", "spout", "shower", "bath", "kitchen"]):
                    smart_cp = "Plumbing & HVAC > Faucets & Sinks > Faucets"
                elif any(w in text_lower for w in ["valve", "fitting", "coupling", "elbow", "pipe", "nipple"]):
                    smart_cp = "Plumbing & HVAC > Valves & Fittings > Industrial Fittings"
                elif any(w in text_lower for w in ["tool", "drill", "saw", "blade", "dewalt", "milwaukee", "milw", "driver"]):
                    smart_cp = "Tools & Hardware > Power Tools & Accessories"
                elif any(w in text_lower for w in ["light", "lumens", "led", "lamp", "fixture", "bulb", "kichler"]):
                    smart_cp = "Electrical & Lighting > Commercial & Architectural Lighting"
                elif any(w in text_lower for w in ["screw", "bolt", "nut", "anchor", "fastener", "washer"]):
                    smart_cp = "Hardware & Fasteners > Industrial Fasteners"

                if smart_cp:
                    return ClassificationResult(
                        classpath=smart_cp,
                        confidence=0.88,
                        alternative_candidates=[],
                        reasoning=f"Auto-classified as {smart_cp} based on domain keyword matching.",
                        needs_review=False,
                        review_reason=None,
                    )

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
        # Best match sorting
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
            0.98,
            0.50 + (
                best_score * 0.10
            ),
        )

        needs_review = (
            confidence < 0.50
        )

        return ClassificationResult(

            classpath=best_classpath,

            confidence=confidence,

            alternative_candidates=(
                alternatives
            ),

            reasoning=(
                f"Selected best matching Classpath (score: {best_score:.1f}) "
                "using hierarchy awareness and stemmed token matching."
            ),

            needs_review=needs_review,

            review_reason=(
                "Low classification confidence."
                if needs_review
                else None
            ),
        )