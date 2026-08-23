"""
Integration test: Part 3 -> Part 4 handoff.

Builds a REAL ProductEnrichmentPart3 object by running the actual,
unmodified part2_classification and part3_normalization pipelines, then
feeds it straight into run_part4 -- no hand-built dict standing in for
Part 3's output. This is what proves the two stages are actually wired
together, not just individually mocked.

No changes were made to part1_foundation, part2_classification, or
part3_normalization to make this pass -- only part4_enrichment_qa was
touched (input_adapter.py, pipeline.py, __init__.py).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unihack.part2_classification.models import ProductEnrichmentPart2, AttributeResult
from unihack.part3_normalization.pipeline import run_part3, run_part3_batch
from unihack.part3_normalization.lookup_adapter import Part3Lookups

from unihack.part4_enrichment_qa import (
    run_part4,
    run_part4_batch,
    run_part4_from_part3,
    adapt_part3_output,
)


def _make_part2_product(index: int, mpn: str, missing_finish: bool = False) -> ProductEnrichmentPart2:
    attributes = [AttributeResult(attribute="Mount Type", value="Deck Mount", confidence=0.9)]
    if not missing_finish:
        attributes.append(AttributeResult(attribute="Finish", value="Chrome", confidence=0.9))

    return ProductEnrichmentPart2(
        product_index=index,
        part_desc=f"{mpn} Kitchen Faucet Deck Mount Chrome",
        mpn=mpn,
        manufacturer="Frigidaire",
        brand="Frigidaire",
        classpath="Plumbing > Faucets > Kitchen Faucets",
        classification_confidence=0.9,
        attributes=attributes,
        needs_review=False,
        review_reasons=[],
    )


def test_adapter_flattens_real_part3_object():
    part2_product = _make_part2_product(1, "PDSH-K100")
    part3_result = run_part3(part2_product, Part3Lookups())

    adapted = adapt_part3_output(part3_result)

    # identity fields pulled from the nested NormalizedProduct
    assert adapted["mpn"] == "PDSH-K100"
    assert adapted["manufacturer"] == "Frigidaire"
    assert adapted["classpath"] == "Plumbing > Faucets > Kitchen Faucets"

    # DescriptionField objects unwrapped to plain strings
    assert isinstance(adapted["invoice_desc"], str)
    assert isinstance(adapted["product_title"], str)
    assert len(adapted["invoice_desc"]) > 0

    # attributes flattened to top-level keys, keyed by attribute name
    assert adapted["Mount Type"] == "Deck Mount"
    assert adapted["Finish"] == "Chrome"

    # bookkeeping preserved under underscore-prefixed keys, not polluting
    # the fields validate_product actually scans
    assert adapted["_part3_product_index"] == 1
    assert isinstance(adapted["_part3_attribute_detail"], list)
    print("adapter test passed")


def test_run_part4_accepts_real_part3_object_directly():
    part2_product = _make_part2_product(2, "PDSH-K200", missing_finish=True)
    part3_result = run_part3(part2_product, Part3Lookups())

    # Finish is missing after Part 3 -- Part 4 should detect it and attempt
    # enrichment. No retrieved_sources given, so it should be flagged
    # needs_review rather than guessed.
    result = run_part4(
        part3_result,
        required_attributes=["Mount Type", "Finish"],
        lov_values={"Mount Type": ["Deck Mount", "Wall Mount"], "Finish": ["Chrome", "Matte Black"]},
        char_limits={"invoice_desc": 40, "mobile_desc": 80},
    )

    assert result["mpn"] == "PDSH-K200"
    assert result["Mount Type"] == "Deck Mount"
    assert "part4_status" in result
    assert "part4_evaluation" in result
    assert result["_part4"]["missing_before_enrichment"] == ["Finish"]
    assert result["_part4"]["needs_review"] is True  # no official source -> flagged, not guessed
    print("single run_part4 with real Part 3 object passed:", result["part4_status"])


def test_run_part4_batch_from_real_part3_batch():
    part2_products = [_make_part2_product(i, f"PDSH-K{100 + i}") for i in range(3)]
    part3_results = run_part3_batch(part2_products, Part3Lookups())

    assert len(part3_results) == 3

    results = run_part4_from_part3(
        part3_results,
        required_attributes=["Mount Type", "Finish"],
        lov_values={"Mount Type": ["Deck Mount"], "Finish": ["Chrome"]},
    )

    assert len(results) == 3
    for r in results:
        assert "part4_status" in r
        assert r["Mount Type"] == "Deck Mount"
    print("batch run_part4_from_part3 passed:", [r["part4_status"] for r in results])


def test_run_part4_still_accepts_plain_dict_for_backward_compatibility():
    # Anyone who already built a flat dict by hand (old calling convention)
    # should keep working unchanged.
    hand_built = {
        "mpn": "LEGACY-1",
        "manufacturer": "Frigidaire",
        "classpath": "Plumbing > Faucets > Kitchen Faucets",
        "invoice_desc": "KITCHEN FAUCET LEGACY-1",
        "Mount Type": "Deck Mount",
        "Finish": "Chrome",
    }

    result = run_part4(hand_built, required_attributes=["Mount Type", "Finish"])
    assert result["mpn"] == "LEGACY-1"
    assert "part4_status" in result
    print("backward-compatible plain-dict input passed")


if __name__ == "__main__":
    test_adapter_flattens_real_part3_object()
    test_run_part4_accepts_real_part3_object_directly()
    test_run_part4_batch_from_real_part3_batch()
    test_run_part4_still_accepts_plain_dict_for_backward_compatibility()
    print("\nAll Part 3 -> Part 4 integration tests passed.")
