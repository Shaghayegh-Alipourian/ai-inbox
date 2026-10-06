from app.evaluation.metrics import EvaluationMetrics
from app.evaluation.regression import check_regression


def make_metrics(
    classification: float,
    priority: float,
    extraction: float = 1.0,
    action_required: float = 1.0,
    structured_output: float = 1.0,
    response_quality: float = 1.0,
) -> EvaluationMetrics:
    return EvaluationMetrics(
        classification_accuracy=classification,
        priority_accuracy=priority,
        extraction_accuracy=extraction,
        action_required_accuracy=action_required,
        structured_output_validity=structured_output,
        response_quality=response_quality,
    )


def test_regression_passes_when_metrics_do_not_drop_beyond_threshold() -> None:
    baseline = make_metrics(
        classification=0.90,
        priority=0.80,
    )
    current = make_metrics(
        classification=0.86,
        priority=0.76,
    )

    result = check_regression(
        baseline=baseline,
        current=current,
        allowed_drop=0.05,
    )

    assert result.passed is True
    assert result.failures == []


def test_regression_fails_when_metric_drops_beyond_threshold() -> None:
    baseline = make_metrics(
        classification=0.90,
        priority=0.80,
    )
    current = make_metrics(
        classification=0.80,
        priority=0.76,
    )

    result = check_regression(
        baseline=baseline,
        current=current,
        allowed_drop=0.05,
    )

    assert result.passed is False
    assert "classification_accuracy" in result.failures[0]


def test_regression_checks_all_supported_metrics() -> None:
    baseline = make_metrics(
        classification=0.90,
        priority=0.90,
        extraction=0.90,
        action_required=0.90,
        structured_output=0.90,
        response_quality=0.90,
    )
    current = make_metrics(
        classification=0.80,
        priority=0.80,
        extraction=0.80,
        action_required=0.80,
        structured_output=0.80,
        response_quality=0.80,
    )

    result = check_regression(
        baseline=baseline,
        current=current,
        allowed_drop=0.05,
    )

    assert result.passed is False
    assert len(result.failures) == 6
