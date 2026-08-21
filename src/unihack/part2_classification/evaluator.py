from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationMetrics:

    total: int

    matched: int

    accuracy: float


@dataclass
class AttributeMetrics:

    expected: int

    predicted: int

    correct: int

    precision: float

    recall: float


def calculate_classification_accuracy(
    predictions: list[str],
    expected: list[str],
) -> ClassificationMetrics:

    total = min(
        len(predictions),
        len(expected),
    )

    if total == 0:

        return ClassificationMetrics(
            total=0,
            matched=0,
            accuracy=0.0,
        )

    matched = sum(
        prediction == expected_value
        for prediction, expected_value
        in zip(
            predictions[:total],
            expected[:total],
        )
    )

    return ClassificationMetrics(

        total=total,

        matched=matched,

        accuracy=(
            matched / total
        ),
    )


def calculate_attribute_metrics(
    predicted: set[tuple[str, str]],
    expected: set[tuple[str, str]],
) -> AttributeMetrics:

    correct = len(
        predicted & expected
    )

    predicted_count = len(
        predicted
    )

    expected_count = len(
        expected
    )

    precision = (
        correct / predicted_count
        if predicted_count
        else 0.0
    )

    recall = (
        correct / expected_count
        if expected_count
        else 0.0
    )

    return AttributeMetrics(

        expected=expected_count,

        predicted=predicted_count,

        correct=correct,

        precision=precision,

        recall=recall,
    )