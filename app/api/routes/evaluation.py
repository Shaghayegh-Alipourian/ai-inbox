from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database
from app.core.config import get_settings
from app.domain.schemas import (
    EvaluationComparisonResponse,
    EvaluationRunCreate,
    EvaluationRunResponse,
)
from app.llm.groq_provider import GroqProvider
from app.services.evaluation_service import EvaluationService

router = APIRouter(
    prefix="/api/v1/evaluation",
    tags=["evaluation"],
)


@router.post(
    "/run",
    response_model=EvaluationRunResponse,
)
async def run_evaluation(
    data: EvaluationRunCreate,
    db: AsyncSession = Depends(get_database),
) -> EvaluationRunResponse:
    settings = get_settings()

    if not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY is not configured.",
        )

    provider = GroqProvider(
        prompt_version=data.prompt_version,
    )

    service = EvaluationService(
        db=db,
        provider=provider,
    )

    return await service.run_evaluation(
        dataset_path=data.dataset_path,
    )


@router.get(
    "/runs/{run_id}",
    response_model=EvaluationRunResponse,
)
async def get_evaluation_run(
    run_id: int,
    db: AsyncSession = Depends(get_database),
) -> EvaluationRunResponse:
    service = EvaluationService(db=db)

    run = await service.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation run not found.",
        )

    return run


@router.get(
    "/compare",
    response_model=EvaluationComparisonResponse,
)
async def compare_evaluations(
    db: AsyncSession = Depends(get_database),
) -> EvaluationComparisonResponse:
    service = EvaluationService(db=db)

    v1, v2 = await service.compare_latest()

    return EvaluationComparisonResponse(
        prompt_v1=v1,
        prompt_v2=v2,
    )
