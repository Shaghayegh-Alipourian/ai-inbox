from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.db.models import Analysis, Email
from app.domain.enums import EmailCategory, Priority
from app.llm.schemas import LLMEmailAnalysis
from app.services.analysis_service import AnalysisService


class FakeProvider:
    provider_name = "fake"
    model_name = "test-model"

    async def analyze_email(
        self,
        subject: str,
        body: str,
    ) -> LLMEmailAnalysis:
        return LLMEmailAnalysis(
            category=EmailCategory.INVOICE,
            priority=Priority.HIGH,
            invoice_id="INV-100",
            due_date="2026-10-01",
            action_required=True,
            suggested_reply="We will review the invoice.",
            confidence=0.95,
        )


@pytest.mark.asyncio
async def test_analyze_email() -> None:
    db = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    async def refresh_analysis(analysis: Analysis) -> None:
        analysis.id = 1
        analysis.created_at = datetime.now()

    db.refresh = AsyncMock(side_effect=refresh_analysis)

    email = Email(
        id=1,
        subject="Invoice",
        body="Please review INV-100.",
    )
    service = AnalysisService(
        db=db,
        provider=FakeProvider(),
    )

    result = await service.analyze_email(email)

    assert result.email_id == 1
    assert result.category == EmailCategory.INVOICE
    assert result.priority == Priority.HIGH
    assert result.invoice_id == "INV-100"
    assert result.action_required is True
