from app.evaluation.metrics import (
    EvaluationMetrics,
    average_metrics,
)


def test_average_performance_metrics() -> None:
    first = EvaluationMetrics(
        classification_accuracy=1.0,
        priority_accuracy=1.0,
        extraction_accuracy=1.0,
        action_required_accuracy=1.0,
        structured_output_validity=1.0,
        response_quality=1.0,
        average_latency_ms=100.0,
        average_ttft_ms=50.0,
        average_input_tokens=100.0,
        average_output_tokens=50.0,
        average_cost=0.001,
    )
    second = EvaluationMetrics(
        classification_accuracy=0.0,
        priority_accuracy=0.0,
        extraction_accuracy=0.0,
        action_required_accuracy=0.0,
        structured_output_validity=0.0,
        response_quality=0.0,
        average_latency_ms=200.0,
        average_ttft_ms=100.0,
        average_input_tokens=200.0,
        average_output_tokens=100.0,
        average_cost=0.003,
    )

    result = average_metrics([first, second])

    assert result.average_latency_ms == 150.0
    assert result.average_ttft_ms == 75.0
    assert result.average_input_tokens == 150.0
    assert result.average_output_tokens == 75.0
    assert result.average_cost == 0.002
