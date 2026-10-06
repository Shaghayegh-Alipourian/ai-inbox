from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.schemas import EmailCreate
from app.services.email_service import EmailService


@pytest.mark.asyncio
async def test_create_email() -> None:
    db = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    service = EmailService(db)

    data = EmailCreate(
        subject="Invoice question",
        body="Please check invoice INV-100.",
    )

    email = await service.create_email(data)

    assert email.subject == data.subject
    assert email.body == data.body
    db.add.assert_called_once_with(email)
    db.commit.assert_awaited_once()
