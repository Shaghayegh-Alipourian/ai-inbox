from collections.abc import Callable
from dataclasses import dataclass

from app.evaluation.dataset import EvaluationCase
from app.evaluation.runner import EvaluationReport, EvaluationRunner
from app.llm.base import LLMProvider


@dataclass(frozen=True)
class ABTestReport:
    prompt_v1: EvaluationReport
    prompt_v2: EvaluationReport


class ABTestRunner:
    def __init__(
        self,
        provider_factory: Callable[[str], LLMProvider],
    ) -> None:
        self.provider_factory = provider_factory

    async def run(
        self,
        cases: list[EvaluationCase],
    ) -> ABTestReport:
        provider_v1 = self.provider_factory("v1")
        provider_v2 = self.provider_factory("v2")

        report_v1 = await EvaluationRunner(
            provider_v1,
        ).run(cases)

        report_v2 = await EvaluationRunner(
            provider_v2,
        ).run(cases)

        return ABTestReport(
            prompt_v1=report_v1,
            prompt_v2=report_v2,
        )
