from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.api.routes import evaluation
from app.main import app


async def test_get_missing_evaluation_run() -> None:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/v1/evaluation/runs/999999",
            )

    assert response.status_code == 404


async def test_evaluation_requires_api_key(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        evaluation,
        "get_settings",
        lambda: type(
            "Settings",
            (),
            {"groq_api_key": None},
        )(),
    )

    async with LifespanManager(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/evaluation/run",
                json={
                    "dataset_path": "data/golden/emails.jsonl",
                    "prompt_version": "v1",
                },
            )

    assert response.status_code == 503
    assert "GROQ_API_KEY" in response.json()["detail"]
