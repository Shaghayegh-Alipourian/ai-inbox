from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Email
from app.domain.schemas import EmailCreate


class EmailService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_email(self, data: EmailCreate) -> Email:
        email = Email(
            subject=data.subject,
            body=data.body,
        )

        self.db.add(email)
        await self.db.commit()
        await self.db.refresh(email)

        return email

    async def get_email(self, email_id: int) -> Email | None:
        result = await self.db.execute(select(Email).where(Email.id == email_id))

        return result.scalar_one_or_none()

    async def list_emails(self) -> list[Email]:
        result = await self.db.execute(select(Email).order_by(Email.created_at.desc()))

        return list(result.scalars().all())
