from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_create_email() -> None:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/emails",
                json={
                    "subject": "Payment issue",
                    "body": "Our payment failed.",
                },
            )

    assert response.status_code == 201

    data = response.json()

    assert data["subject"] == "Payment issue"
    assert data["body"] == "Our payment failed."
    assert "id" in data
