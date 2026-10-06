from collections.abc import AsyncIterator

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_llm_provider
from app.main import app


class FakeStreamingProvider:
    provider_name = "fake"
    model_name = "test-model"

    async def analyze_email(
        self,
        subject: str,
        body: str,
    ):
        raise NotImplementedError

    async def stream_analysis(
        self,
        subject: str,
        body: str,
    ) -> AsyncIterator[str]:
        yield '{"category":'
        yield '"support"}'


async def test_stream_analysis() -> None:
    app.dependency_overrides[get_llm_provider] = FakeStreamingProvider

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
                        "body": "I need help.",
                    },
                )

                email_id = create_response.json()["id"]

                response = await client.get(
                    f"/api/v1/emails/{email_id}/analyze/stream",
                )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "text/event-stream",
        )

        assert '{"type": "chunk", "content": "{\\"category\\":"}' in (response.text)
        assert '{"type": "done"}' in response.text

    finally:
        app.dependency_overrides.clear()
