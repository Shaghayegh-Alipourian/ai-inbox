from collections.abc import AsyncIterator

import pytest

from app.domain.enums import EmailCategory, Priority
from app.evaluation.ab_test import ABTestRunner
from app.evaluation.dataset import EvaluationCase
from app.llm.base import LLMProvider
from app.llm.schemas import LLMEmailAnalysis


class FakeProvider(LLMProvider):
    provider_name = "fake"
    model_name = "test-model"

    def __init__(self, prompt_version: str) -> None:
        self.prompt_version = prompt_version

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
            suggested_reply=(f"Reply generated with {self.prompt_version}."),
            confidence=0.9,
        )

    async def stream_analysis(
        self,
        subject: str,
        body: str,
    ) -> AsyncIterator[str]:
        yield "test"


@pytest.mark.asyncio
async def test_ab_test_uses_both_prompt_versions() -> None:
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

    runner = ABTestRunner(
        lambda version: FakeProvider(version),
    )

    report = await runner.run(cases)

    assert report.prompt_v1.total_cases == 1
    assert report.prompt_v2.total_cases == 1

    assert report.prompt_v1.results[0].metrics.response_quality == 1.0

    assert report.prompt_v2.results[0].metrics.response_quality == 1.0
