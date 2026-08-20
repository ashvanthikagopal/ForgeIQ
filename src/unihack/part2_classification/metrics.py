from __future__ import annotations

from typing import Any


def classification_accuracy(
    predictions: list[str | None],
    ground_truth: list[str | None],
) -> float:

    if len(predictions) != len(ground_truth):
        raise ValueError(
            "Prediction and ground-truth lengths differ."
        )

    if not predictions:
        return 0.0

    correct = sum(
        pred == truth
        for pred, truth in zip(predictions, ground_truth)
    )

    return correct / len(predictions)


def attribute_precision_recall(
    predicted: set[tuple[str, str]],
    expected: set[tuple[str, str]],
) -> dict[str, float]:

    true_positive = len(
        predicted.intersection(expected)
    )

    false_positive = len(
        predicted - expected
    )

    false_negative = len(
        expected - predicted
    )

    precision = (
        true_positive /
        (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )

    recall = (
        true_positive /
        (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )

    f1 = (
        2 * precision * recall /
        (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def lov_compliance_rate(
    generated: list[tuple[str, str]],
    permitted_values: dict[str, list[str]],
) -> float:

    if not generated:
        return 0.0

    valid = 0

    for attribute, value in generated:

        if value in permitted_values.get(attribute, []):
            valid += 1

    return valid / len(generated)