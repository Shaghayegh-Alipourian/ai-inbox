from dataclasses import dataclass

from app.llm.schemas import LLMEmailAnalysis


@dataclass(frozen=True)
class EvaluationMetrics:
    classification_accuracy: float
    priority_accuracy: float
    extraction_accuracy: float
    action_required_accuracy: float
    structured_output_validity: float
    response_quality: float
    average_latency_ms: float = 0.0
    average_ttft_ms: float = 0.0
    average_input_tokens: float = 0.0
    average_output_tokens: float = 0.0
    average_cost: float = 0.0


def calculate_metrics(
    expected_category: str,
    expected_priority: str,
    expected_invoice_id: str | None,
    expected_due_date: str | None,
    expected_action_required: bool,
    result: LLMEmailAnalysis | None,
) -> EvaluationMetrics:
    if result is None:
        return EvaluationMetrics(
            classification_accuracy=0.0,
            priority_accuracy=0.0,
            extraction_accuracy=0.0,
            action_required_accuracy=0.0,
            structured_output_validity=0.0,
            response_quality=0.0,
        )

    classification_accuracy = float(result.category.value == expected_category)

    priority_accuracy = float(result.priority.value == expected_priority)

    extraction_fields = [
        result.invoice_id == expected_invoice_id,
        result.due_date == expected_due_date,
    ]

    extraction_accuracy = sum(extraction_fields) / len(extraction_fields)

    action_required_accuracy = float(result.action_required == expected_action_required)

    response_quality = float(bool(result.suggested_reply.strip()))

    return EvaluationMetrics(
        classification_accuracy=classification_accuracy,
        priority_accuracy=priority_accuracy,
        extraction_accuracy=extraction_accuracy,
        action_required_accuracy=action_required_accuracy,
        structured_output_validity=1.0,
        response_quality=response_quality,
    )


def average_metrics(
    metrics: list[EvaluationMetrics],
) -> EvaluationMetrics:
    if not metrics:
        raise ValueError("Cannot average an empty metrics list.")

    count = len(metrics)

    return EvaluationMetrics(
        classification_accuracy=sum(item.classification_accuracy for item in metrics)
        / count,
        priority_accuracy=sum(item.priority_accuracy for item in metrics) / count,
        extraction_accuracy=sum(item.extraction_accuracy for item in metrics) / count,
        action_required_accuracy=sum(item.action_required_accuracy for item in metrics)
        / count,
        structured_output_validity=sum(
            item.structured_output_validity for item in metrics
        )
        / count,
        response_quality=sum(item.response_quality for item in metrics) / count,
        average_latency_ms=sum(item.average_latency_ms for item in metrics) / count,
        average_ttft_ms=sum(item.average_ttft_ms for item in metrics) / count,
        average_input_tokens=sum(item.average_input_tokens for item in metrics) / count,
        average_output_tokens=sum(item.average_output_tokens for item in metrics)
        / count,
        average_cost=sum(item.average_cost for item in metrics) / count,
    )
