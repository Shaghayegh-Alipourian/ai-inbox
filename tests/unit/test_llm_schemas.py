import pytest
from pydantic import ValidationError

from app.domain.enums import EmailCategory, Priority
from app.llm.schemas import LLMEmailAnalysis


def test_valid_llm_analysis() -> None:
    analysis = LLMEmailAnalysis(
        category=EmailCategory.INVOICE,
        priority=Priority.HIGH,
        invoice_id="INV-100",
        due_date="2026-10-01",
        action_required=True,
        suggested_reply="We will review the invoice.",
        confidence=0.92,
    )

    assert analysis.category == EmailCategory.INVOICE
    assert analysis.priority == Priority.HIGH
    assert analysis.confidence == 0.92


def test_optional_values_can_be_null() -> None:
    analysis = LLMEmailAnalysis(
        category=EmailCategory.SUPPORT,
        priority=Priority.NORMAL,
        invoice_id=None,
        due_date=None,
        action_required=False,
        suggested_reply="We will review your request.",
        confidence=0.8,
    )

    assert analysis.invoice_id is None
    assert analysis.due_date is None


def test_invalid_confidence_is_rejected() -> None:
    with pytest.raises(ValidationError):
        LLMEmailAnalysis(
            category=EmailCategory.OTHER,
            priority=Priority.NORMAL,
            invoice_id=None,
            due_date=None,
            action_required=False,
            suggested_reply="No action required.",
            confidence=1.5,
        )
