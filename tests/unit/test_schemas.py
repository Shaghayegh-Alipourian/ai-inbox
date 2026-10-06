from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.enums import EmailCategory, Priority
from app.domain.schemas import EmailAnalysis


def test_valid_email_analysis() -> None:
    analysis = EmailAnalysis(
        category=EmailCategory.PAYMENT_ISSUE,
        priority=Priority.HIGH,
        invoice_id="INV-4821",
        due_date=date(2026, 9, 15),
        action_required=True,
        suggested_reply="We will review the payment status.",
        confidence=0.95,
    )

    assert analysis.category == EmailCategory.PAYMENT_ISSUE
    assert analysis.priority == Priority.HIGH
    assert analysis.confidence == 0.95


def test_confidence_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category=EmailCategory.OTHER,
            priority=Priority.NORMAL,
            action_required=False,
            suggested_reply="No action is required.",
            confidence=1.5,
        )
