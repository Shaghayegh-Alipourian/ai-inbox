from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database, get_llm_provider
from app.db.models import Email
from app.domain.schemas import AnalysisResponse
from app.llm.base import LLMProvider
from app.llm.streaming import sse_stream
from app.services.analysis_service import AnalysisService
from app.services.email_service import EmailService

router = APIRouter(
    prefix="/api/v1/emails",
    tags=["analysis"],
)


@router.post(
    "/{email_id}/analyze",
    response_model=AnalysisResponse,
)
async def analyze_email(
    email_id: int,
    db: AsyncSession = Depends(get_database),
    provider: LLMProvider = Depends(get_llm_provider),
) -> AnalysisResponse:
    email_service = EmailService(db)

    email: Email | None = await email_service.get_email(email_id)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found.",
        )

    service = AnalysisService(
        db=db,
        provider=provider,
    )

    return await service.analyze_email(email)


@router.get(
    "/{email_id}/analyze/stream",
)
async def stream_analysis(
    email_id: int,
    db: AsyncSession = Depends(get_database),
    provider: LLMProvider = Depends(get_llm_provider),
) -> StreamingResponse:
    email_service = EmailService(db)

    email: Email | None = await email_service.get_email(email_id)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found.",
        )

    service = AnalysisService(
        db=db,
        provider=provider,
    )

    return StreamingResponse(
        sse_stream(
            service.stream_analysis(email),
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
