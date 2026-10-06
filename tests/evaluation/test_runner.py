from collections.abc import AsyncIterator

import pytest

from app.domain.enums import EmailCategory, Priority
from app.evaluation.dataset import EvaluationCase
from app.evaluation.runner import EvaluationRunner
from app.llm.base import LLMProvider
from app.llm.schemas import LLMEmailAnalysis


class FakeProvider(LLMProvider):
    provider_name = "fake"
    model_name = "test-model"

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
            suggested_reply="We will help you.",
            confidence=0.9,
        )

    async def stream_analysis(
        self,
        subject: str,
        body: str,
    ) -> AsyncIterator[str]:
        yield "test"


@pytest.mark.asyncio
async def test_evaluation_runner() -> None:
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

    runner = EvaluationRunner(FakeProvider())

    report = await runner.run(cases)

    assert report.total_cases == 1
    assert report.successful_cases == 1
    assert report.failed_cases == 0
    assert report.metrics.classification_accuracy == 1.0
