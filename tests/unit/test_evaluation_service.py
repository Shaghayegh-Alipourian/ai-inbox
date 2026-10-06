from collections.abc import AsyncIterator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.enums import EmailCategory, Priority
from app.evaluation.dataset import EvaluationCase
from app.llm.base import LLMProvider
from app.llm.schemas import LLMEmailAnalysis
from app.services.evaluation_service import EvaluationService


class FakeProvider(LLMProvider):
    provider_name = "fake"
    model_name = "test-model"
    prompt_version = "v1"

    async def analyze_email(
        self,
        subject: str,
        body: str,
    ) -> LLMEmailAnalysis:
        return LLMEmailAnalysis(
            category=EmailCategory.SUPPORT,
            priority=Priority.NORMAL,
            invoice_id=None,
            due_date=None,
            action_required=True,
            suggested_reply="We will help.",
            confidence=0.9,
        )

    async def stream_analysis(
        self,
        subject: str,
        body: str,
    ) -> AsyncIterator[str]:
        yield "test"


@pytest.mark.asyncio
async def test_evaluation_service_persists_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cases = [
        EvaluationCase(
            case_id="test-001",
            subject="Support request",
            body="I need help.",
            expected_category=EmailCategory.SUPPORT,
            expected_priority=Priority.NORMAL,
            expected_invoice_id=None,
            expected_due_date=None,
            expected_action_required=True,
        ),
    ]

    monkeypatch.setattr(
        "app.services.evaluation_service.load_dataset",
        lambda _: cases,
    )

    db = Mock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    db.refresh = AsyncMock(
        side_effect=lambda run: (
            setattr(run, "id", 1),
            setattr(run, "created_at", datetime.now(UTC)),
        ),
    )

    provider = FakeProvider()

    service = EvaluationService(
        db=db,
        provider=provider,
    )

    result = await service.run_evaluation(
        dataset_path="test.jsonl",
    )

    assert result.id == 1
    assert result.total_cases == 1
    assert result.successful_cases == 1

    db.add.assert_called()
    db.commit.assert_awaited_once()
