from app.evaluation.metrics import EvaluationMetrics
from app.evaluation.regression import check_regression


def build_metrics(
    classification: float,
    extraction: float,
) -> EvaluationMetrics:
    return EvaluationMetrics(
        classification_accuracy=classification,
        priority_accuracy=1.0,
        extraction_accuracy=extraction,
        action_required_accuracy=1.0,
        structured_output_validity=1.0,
        response_quality=1.0,
    )


def test_regression_passes_when_drop_is_within_threshold() -> None:
    baseline = build_metrics(0.90, 0.90)
    current = build_metrics(0.86, 0.87)

    result = check_regression(
        baseline=baseline,
        current=current,
        allowed_drop=0.05,
    )

    assert result.passed is True
    assert result.failures == []


def test_regression_fails_when_metric_drops_too_much() -> None:
    baseline = build_metrics(0.90, 0.90)
    current = build_metrics(0.80, 0.90)

    result = check_regression(
        baseline=baseline,
        current=current,
        allowed_drop=0.05,
    )

    assert result.passed is False
    assert "classification_accuracy" in result.failures[0]
