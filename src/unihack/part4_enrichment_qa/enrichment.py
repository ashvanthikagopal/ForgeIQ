"""
Part 4, Phase G (optional — only if Parts 1-3's output is solid) —
Enrichment from Manufacturer Sources.

For attributes still missing after Part 2's extraction, retrieve
additional info ONLY from the manufacturer's own site/documentation.
Marketplace/distributor sources are explicitly excluded (rule #4).

If there's no live retrieval infrastructure in time, simulate this stage
with a small manually-curated set of manufacturer spec sheets for Faucets
and clearly label it as a proof-of-concept in the demo.
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass

from unihack.schemas import AttributeValue
from unihack.config import ALLOWED_SOURCE_TYPE
from unihack.part4_enrichment_qa.prompts import (
    ENRICHMENT_SYSTEM_PROMPT,
    ENRICHMENT_USER_PROMPT,
)

log = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    source_url: str
    source_type: str  # "manufacturer_official" | "marketplace" | "distributor" | ...


def filter_to_manufacturer_sources(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """The sourcing-hierarchy backstop in code, not just in the prompt.
    Discard anything not tagged manufacturer_official BEFORE it ever
    reaches the model — don't rely on the LLM to self-police this."""
    kept = [c for c in chunks if c.source_type == ALLOWED_SOURCE_TYPE]
    dropped = len(chunks) - len(kept)
    if dropped:
        log.info("Dropped %d non-manufacturer-sourced chunks before enrichment call.", dropped)
    return kept


def build_enrichment_prompt(
    brand: str, mpn: str, classpath: str,
    missing_attributes: list[str], chunks: list[RetrievedChunk],
) -> tuple[str, str]:
    chunk_block = "\n\n".join(
        f"[source_type={c.source_type}, url={c.source_url}]\n{c.text}" for c in chunks
    )
    user = ENRICHMENT_USER_PROMPT.format(
        brand=brand, mpn=mpn, classpath=classpath,
        missing_attribute_list=", ".join(missing_attributes),
        retrieved_chunks_with_source_type_tag=chunk_block or "(no qualifying chunks retrieved)",
    )
    return ENRICHMENT_SYSTEM_PROMPT, user


def parse_enrichment_response(raw_json: str) -> list[AttributeValue]:
    data = json.loads(raw_json)
    results = []
    for item in data:
        if item.get("value") in (None, "not_available"):
            continue
        results.append(AttributeValue(
            attribute=item["attribute"],
            value=item["value"],
            confidence=float(item.get("confidence", 0.0)),
            source_url=item.get("source_url"),
            method="inferred_manufacturer_source",
        ))
    return results


def enrich_missing_attributes(
    brand: str, mpn: str, classpath: str,
    missing_attributes: list[str],
    retrieved_chunks: list[RetrievedChunk],
    llm_call,
) -> list[AttributeValue]:
    """`llm_call(system, user) -> raw_json_str` injected for testability.
    If you're simulating this stage with curated spec sheets instead of
    live retrieval, pass those in as `retrieved_chunks` with
    source_type="manufacturer_official" and label it POC in the demo."""
    qualifying = filter_to_manufacturer_sources(retrieved_chunks)
    system, user = build_enrichment_prompt(brand, mpn, classpath, missing_attributes, qualifying)
    raw_response = llm_call(system, user)
    return parse_enrichment_response(raw_response)