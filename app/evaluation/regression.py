from dataclasses import dataclass

from app.evaluation.metrics import EvaluationMetrics


@dataclass(frozen=True)
class RegressionResult:
    passed: bool
    failures: list[str]


def check_regression(
    baseline: EvaluationMetrics,
    current: EvaluationMetrics,
    allowed_drop: float = 0.05,
) -> RegressionResult:
    failures: list[str] = []

    metrics = {
        "classification_accuracy": (
            baseline.classification_accuracy,
            current.classification_accuracy,
        ),
        "priority_accuracy": (
            baseline.priority_accuracy,
            current.priority_accuracy,
        ),
        "extraction_accuracy": (
            baseline.extraction_accuracy,
            current.extraction_accuracy,
        ),
        "action_required_accuracy": (
            baseline.action_required_accuracy,
            current.action_required_accuracy,
        ),
        "structured_output_validity": (
            baseline.structured_output_validity,
            current.structured_output_validity,
        ),
        "response_quality": (
            baseline.response_quality,
            current.response_quality,
        ),
    }

    for name, (baseline_value, current_value) in metrics.items():
        if current_value < baseline_value - allowed_drop:
            failures.append(
                f"{name}: baseline={baseline_value:.3f}, current={current_value:.3f}"
            )

    return RegressionResult(
        passed=not failures,
        failures=failures,
    )
