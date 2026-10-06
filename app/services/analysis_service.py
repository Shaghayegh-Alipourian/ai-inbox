from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Analysis, Email
from app.domain.schemas import AnalysisResponse
from app.evaluation.adversarial import determine_analysis_status
from app.llm.base import LLMProvider
from app.services.validation_service import validate_analysis


class AnalysisService:
    def __init__(
        self,
        db: AsyncSession,
        provider: LLMProvider,
    ) -> None:
        self.db = db
        self.provider = provider

    async def analyze_email(
        self,
        email: Email,
    ) -> AnalysisResponse:
        llm_analysis = await self.provider.analyze_email(
            subject=email.subject,
            body=email.body,
        )

        analysis_data = validate_analysis(llm_analysis)

        if analysis_data.due_date is not None:
            analysis_data.due_date = date.fromisoformat(str(analysis_data.due_date))

        status = determine_analysis_status(
            subject=email.subject,
            body=email.body,
            analysis=llm_analysis,
        )

        analysis = Analysis(
            email_id=email.id,
            category=analysis_data.category,
            priority=analysis_data.priority,
            invoice_id=analysis_data.invoice_id,
            due_date=analysis_data.due_date,
            action_required=analysis_data.action_required,
            suggested_reply=analysis_data.suggested_reply,
            confidence=analysis_data.confidence,
            status=status,
        )

        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        return AnalysisResponse.model_validate(analysis)

    async def stream_analysis(
        self,
        email: Email,
    ):
        async for chunk in self.provider.stream_analysis(
            subject=email.subject,
            body=email.body,
        ):
            yield chunk
