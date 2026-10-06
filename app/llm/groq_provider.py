import asyncio
import json
import random
import time
from collections.abc import AsyncIterator

from groq import AsyncGroq, RateLimitError

from app.core.config import get_settings
from app.llm.base import LLMProvider, LLMRunMetrics
from app.llm.prompts import USER_PROMPT_TEMPLATE, load_system_prompt
from app.llm.schemas import LLMEmailAnalysis


class GroqProvider(LLMProvider):
    provider_name = "groq"

    def __init__(
        self,
        client: AsyncGroq | None = None,
        model_name: str | None = None,
        prompt_version: str = "v1",
    ) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.groq_model
        self.prompt_version = prompt_version
        self.system_prompt = load_system_prompt(prompt_version)
        self.client = client or AsyncGroq(api_key=settings.groq_api_key)
        self._last_run_metrics: LLMRunMetrics | None = None

    @property
    def last_run_metrics(self) -> LLMRunMetrics | None:
        return self._last_run_metrics

    def _messages(
        self,
        subject: str,
        body: str,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(
                    subject=subject,
                    body=body,
                ),
            },
        ]

    def _response_format(self) -> dict:
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "email_analysis",
                "strict": True,
                "schema": LLMEmailAnalysis.model_json_schema(),
            },
        }

    async def analyze_email(
        self,
        subject: str,
        body: str,
    ) -> LLMEmailAnalysis:
        start = time.perf_counter()

        for attempt in range(5):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self._messages(subject, body),
                    response_format=self._response_format(),
                )

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Groq returned an empty response.")

                payload = json.loads(content)
                result = LLMEmailAnalysis.model_validate(payload)

                latency_ms = (time.perf_counter() - start) * 1000
                usage = response.usage

                self._last_run_metrics = LLMRunMetrics(
                    input_tokens=usage.prompt_tokens if usage else 0,
                    output_tokens=usage.completion_tokens if usage else 0,
                    latency_ms=latency_ms,
                )

                return result

            except RateLimitError as exc:
                if attempt == 4:
                    raise

                retry_after = None

                if exc.response is not None:
                    retry_after_header = exc.response.headers.get("retry-after")
                    if retry_after_header is not None:
                        retry_after = float(retry_after_header)

                if retry_after is None:
                    retry_after = min(
                        2**attempt + random.random(),
                        30,
                    )

                await asyncio.sleep(retry_after)

        raise RuntimeError("Groq request failed after maximum retries.")

    async def stream_analysis(
        self,
        subject: str,
        body: str,
    ) -> AsyncIterator[str]:
        start = time.perf_counter()
        first_token_time: float | None = None
        input_tokens = 0
        output_tokens = 0

        stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=self._messages(subject, body),
            response_format=self._response_format(),
            stream=True,
        )

        async for chunk in stream:
            if first_token_time is None:
                first_token_time = time.perf_counter()

            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

            usage = getattr(chunk, "usage", None)
            if usage is not None:
                input_tokens = usage.prompt_tokens or 0
                output_tokens = usage.completion_tokens or 0

        latency_ms = (time.perf_counter() - start) * 1000
        ttft_ms = (
            (first_token_time - start) * 1000 if first_token_time is not None else None
        )

        self._last_run_metrics = LLMRunMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            ttft_ms=ttft_ms,
        )
