from app.domain.enums import EmailCategory, Priority
from app.evaluation.metrics import (
    average_metrics,
    calculate_metrics,
)
from app.llm.schemas import LLMEmailAnalysis


def build_result() -> LLMEmailAnalysis:
    return LLMEmailAnalysis(
        category=EmailCategory.INVOICE,
        priority=Priority.NORMAL,
        invoice_id="INV-0001",
        due_date="2026-10-15",
        action_required=True,
        suggested_reply="Thank you. We will process the invoice.",
        confidence=0.95,
    )


def test_calculate_metrics_for_correct_result() -> None:
    metrics = calculate_metrics(
        expected_category="invoice",
        expected_priority="normal",
        expected_invoice_id="INV-0001",
        expected_due_date="2026-10-15",
        expected_action_required=True,
        result=build_result(),
    )

    assert metrics.classification_accuracy == 1.0
    assert metrics.extraction_accuracy == 1.0
    assert metrics.action_required_accuracy == 1.0
    assert metrics.structured_output_validity == 1.0
    assert metrics.response_quality == 1.0


def test_calculate_metrics_for_invalid_result() -> None:
    metrics = calculate_metrics(
        expected_category="invoice",
        expected_priority="normal",
        expected_invoice_id="INV-0001",
        expected_due_date="2026-10-15",
        expected_action_required=True,
        result=None,
    )

    assert metrics.structured_output_validity == 0.0
    assert metrics.classification_accuracy == 0.0


def test_average_metrics() -> None:
    first = calculate_metrics(
        expected_category="invoice",
        expected_priority="normal",
        expected_invoice_id="INV-0001",
        expected_due_date="2026-10-15",
        expected_action_required=True,
        result=build_result(),
    )

    second = calculate_metrics(
        expected_category="support",
        expected_priority="normal",
        expected_invoice_id=None,
        expected_due_date=None,
        expected_action_required=True,
        result=None,
    )

    average = average_metrics([first, second])

    assert average.classification_accuracy == 0.5
    assert average.extraction_accuracy == 0.5
    assert average.structured_output_validity == 0.5
