from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database
from app.domain.schemas import EmailCreate, EmailResponse
from app.services.email_service import EmailService

router = APIRouter(
    prefix="/api/v1/emails",
    tags=["emails"],
)


@router.post(
    "",
    response_model=EmailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_email(
    data: EmailCreate,
    db: AsyncSession = Depends(get_database),
) -> EmailResponse:
    service = EmailService(db)

    email = await service.create_email(data)

    return EmailResponse.model_validate(email)


@router.get(
    "",
    response_model=list[EmailResponse],
)
async def list_emails(
    db: AsyncSession = Depends(get_database),
) -> list[EmailResponse]:
    service = EmailService(db)

    emails = await service.list_emails()

    return [EmailResponse.model_validate(email) for email in emails]


@router.get(
    "/{email_id}",
    response_model=EmailResponse,
)
async def get_email(
    email_id: int,
    db: AsyncSession = Depends(get_database),
) -> EmailResponse:
    service = EmailService(db)

    email = await service.get_email(email_id)

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found.",
        )

    return EmailResponse.model_validate(email)
