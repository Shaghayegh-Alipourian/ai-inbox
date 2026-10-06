from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_llm_provider
from app.domain.enums import EmailCategory, Priority
from app.llm.schemas import LLMEmailAnalysis
from app.main import app


class FakeProvider:
    provider_name = "fake"
    model_name = "test-model"

    async def analyze_email(
        self,
        subject: str,
        body: str,
    ) -> LLMEmailAnalysis:
        return LLMEmailAnalysis(
            category=EmailCategory.SUPPORT,
            priority=Priority.NORMAL,
            invoice_id=None,
            due_date=None,
            action_required=True,
            suggested_reply="We will investigate your issue.",
            confidence=0.9,
        )


async def test_analyze_email() -> None:
    app.dependency_overrides[get_llm_provider] = FakeProvider

    try:
        async with LifespanManager(app):
            transport = ASGITransport(app=app)

            async with AsyncClient(
                transport=transport,
                base_url="http://test",
            ) as client:
                create_response = await client.post(
                    "/api/v1/emails",
                    json={
                        "subject": "Support request",
                        "body": "I need help with my account.",
                    },
                )

                email_id = create_response.json()["id"]

                response = await client.post(
                    f"/api/v1/emails/{email_id}/analyze",
                )

        assert response.status_code == 200

        data = response.json()

        assert data["category"] == "support"
        assert data["priority"] == "normal"
        assert data["action_required"] is True

    finally:
        app.dependency_overrides.clear()
