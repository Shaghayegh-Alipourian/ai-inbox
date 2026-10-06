from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EvaluationResult, EvaluationRun
from app.domain.schemas import (
    EvaluationMetricsResponse,
    EvaluationRunResponse,
)
from app.evaluation.dataset import load_dataset
from app.evaluation.runner import EvaluationRunner
from app.llm.base import LLMProvider


class EvaluationService:
    def __init__(
        self,
        db: AsyncSession,
        provider: LLMProvider | None = None,
    ) -> None:
        self.db = db
        self.provider = provider

    async def run_evaluation(
        self,
        dataset_path: str,
    ) -> EvaluationRunResponse:
        if self.provider is None:
            raise ValueError("LLM provider is required to run an evaluation.")

        cases = load_dataset(Path(dataset_path))

        report = await EvaluationRunner(
            self.provider,
        ).run(cases)

        run = EvaluationRun(
            dataset_version=dataset_path,
            prompt_version=getattr(
                self.provider,
                "prompt_version",
                "v1",
            ),
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            total_cases=report.total_cases,
            successful_cases=report.successful_cases,
            failed_cases=report.failed_cases,
            classification_accuracy=(report.metrics.classification_accuracy),
            priority_accuracy=(report.metrics.priority_accuracy),
            extraction_accuracy=(report.metrics.extraction_accuracy),
            action_required_accuracy=(report.metrics.action_required_accuracy),
            structured_output_validity=(report.metrics.structured_output_validity),
            response_quality=report.metrics.response_quality,
            average_latency_ms=(report.metrics.average_latency_ms),
            average_ttft_ms=report.metrics.average_ttft_ms,
            average_input_tokens=(report.metrics.average_input_tokens),
            average_output_tokens=(report.metrics.average_output_tokens),
            average_cost=report.metrics.average_cost,
        )

        self.db.add(run)
        await self.db.flush()

        for result in report.results:
            db_result = EvaluationResult(
                evaluation_run_id=run.id,
                case_id=result.case_id,
                valid_output=result.valid_output,
                classification_accuracy=(result.metrics.classification_accuracy),
                priority_accuracy=(result.metrics.priority_accuracy),
                extraction_accuracy=(result.metrics.extraction_accuracy),
                action_required_accuracy=(result.metrics.action_required_accuracy),
                structured_output_validity=(result.metrics.structured_output_validity),
                response_quality=result.metrics.response_quality,
                error=result.error,
            )

            self.db.add(db_result)

        await self.db.commit()
        await self.db.refresh(run)

        return self._to_response(run)

    async def get_run(
        self,
        run_id: int,
    ) -> EvaluationRunResponse | None:
        result = await self.db.execute(
            select(EvaluationRun).where(
                EvaluationRun.id == run_id,
            )
        )

        run = result.scalar_one_or_none()

        if run is None:
            return None

        return self._to_response(run)

    async def compare_latest(
        self,
    ) -> tuple[
        EvaluationRunResponse | None,
        EvaluationRunResponse | None,
    ]:
        v1_result = await self.db.execute(
            select(EvaluationRun)
            .where(EvaluationRun.prompt_version == "v1")
            .order_by(EvaluationRun.created_at.desc())
            .limit(1)
        )

        v2_result = await self.db.execute(
            select(EvaluationRun)
            .where(EvaluationRun.prompt_version == "v2")
            .order_by(EvaluationRun.created_at.desc())
            .limit(1)
        )

        v1 = v1_result.scalar_one_or_none()
        v2 = v2_result.scalar_one_or_none()

        return (
            self._to_response(v1) if v1 else None,
            self._to_response(v2) if v2 else None,
        )

    @staticmethod
    def _to_response(
        run: EvaluationRun,
    ) -> EvaluationRunResponse:
        return EvaluationRunResponse(
            id=run.id,
            dataset_version=run.dataset_version,
            prompt_version=run.prompt_version,
            provider=run.provider,
            model=run.model,
            total_cases=run.total_cases,
            successful_cases=run.successful_cases,
            failed_cases=run.failed_cases,
            metrics=EvaluationMetricsResponse(
                classification_accuracy=(run.classification_accuracy),
                priority_accuracy=run.priority_accuracy,
                extraction_accuracy=run.extraction_accuracy,
                action_required_accuracy=(run.action_required_accuracy),
                structured_output_validity=(run.structured_output_validity),
                response_quality=run.response_quality,
                average_latency_ms=run.average_latency_ms,
                average_ttft_ms=run.average_ttft_ms,
                average_input_tokens=(run.average_input_tokens),
                average_output_tokens=(run.average_output_tokens),
                average_cost=run.average_cost,
            ),
            created_at=run.created_at,
        )
