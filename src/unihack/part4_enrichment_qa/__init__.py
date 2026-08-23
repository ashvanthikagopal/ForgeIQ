"""
Part 4 - Enrichment and QA.
"""
from .pipeline import run_part4, run_part4_batch, run_part4_from_part3
from .input_adapter import adapt_part3_output
from .confidence import (
    ConfidenceResult,
    calculate_confidence,
)

from .enrichment import (
    enrich_missing_attributes,
    find_missing_attributes,
)

from .validation import (
    validate_product,
)

from .evaluation import (
    evaluate_product,
    evaluate_batch,
)

from .packaging import (
    package_product,
)


__all__ = [
    "run_part4",
    "run_part4_batch",
    "run_part4_from_part3",
    "adapt_part3_output",
    "ConfidenceResult",
    "calculate_confidence",
    "enrich_missing_attributes",
    "find_missing_attributes",
    "validate_product",
    "evaluate_product",
    "evaluate_batch",
    "package_product",
]