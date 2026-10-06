from dataclasses import dataclass, replace

from app.evaluation.dataset import EvaluationCase
from app.evaluation.metrics import (
    EvaluationMetrics,
    average_metrics,
    calculate_metrics,
)
from app.llm.base import LLMProvider
from app.llm.schemas import LLMEmailAnalysis
from app.services.cost_service import (
    TokenUsage,
    calculate_cost,
    get_model_pricing,
)


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    valid_output: bool
    metrics: EvaluationMetrics
    error: str | None = None


@dataclass(frozen=True)
class EvaluationReport:
    total_cases: int
    successful_cases: int
    failed_cases: int
    metrics: EvaluationMetrics
    results: list[EvaluationResult]


class EvaluationRunner:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def run(
        self,
        cases: list[EvaluationCase],
    ) -> EvaluationReport:
        results: list[EvaluationResult] = []

        for index, case in enumerate(cases, start=1):
            print(
                f"Evaluating {index}/{len(cases)}: {case.case_id}",
                flush=True,
            )
            result = await self._evaluate_case(case)
            results.append(result)

        successful = [result.metrics for result in results if result.valid_output]

        metrics = average_metrics(
            [result.metrics for result in results],
        )

        return EvaluationReport(
            total_cases=len(cases),
            successful_cases=len(successful),
            failed_cases=len(cases) - len(successful),
            metrics=metrics,
            results=results,
        )

    async def _evaluate_case(
        self,
        case: EvaluationCase,
    ) -> EvaluationResult:
        try:
            result: LLMEmailAnalysis = await self.provider.analyze_email(
                subject=case.subject,
                body=case.body,
            )

            metrics = calculate_metrics(
                expected_category=case.expected_category.value,
                expected_priority=case.expected_priority.value,
                expected_invoice_id=case.expected_invoice_id,
                expected_due_date=case.expected_due_date,
                expected_action_required=case.expected_action_required,
                result=result,
            )

            run_metrics = self.provider.last_run_metrics

            if run_metrics is not None:
                pricing = get_model_pricing(self.provider.model_name)

                cost = calculate_cost(
                    TokenUsage(
                        input_tokens=run_metrics.input_tokens,
                        output_tokens=run_metrics.output_tokens,
                    ),
                    pricing,
                )

                metrics = replace(
                    metrics,
                    average_latency_ms=run_metrics.latency_ms,
                    average_ttft_ms=run_metrics.ttft_ms or 0.0,
                    average_input_tokens=run_metrics.input_tokens,
                    average_output_tokens=run_metrics.output_tokens,
                    average_cost=cost,
                )

            return EvaluationResult(
                case_id=case.case_id,
                valid_output=True,
                metrics=metrics,
            )

        except Exception as exc:
            metrics = calculate_metrics(
                expected_category=case.expected_category.value,
                expected_priority=case.expected_priority.value,
                expected_invoice_id=case.expected_invoice_id,
                expected_due_date=case.expected_due_date,
                expected_action_required=case.expected_action_required,
                result=None,
            )

            return EvaluationResult(
                case_id=case.case_id,
                valid_output=False,
                metrics=metrics,
                error=str(exc),
            )
