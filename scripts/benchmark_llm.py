import asyncio
import time

from app.llm.groq_provider import GroqProvider
from app.services.llm_run_service import count_tokens


async def main() -> None:
    provider = GroqProvider()

    subject = "Support request"
    body = "I need help with my account."

    input_text = f"{subject}\n{body}"

    start = time.perf_counter()

    result = await provider.analyze_email(
        subject=subject,
        body=body,
    )

    end = time.perf_counter()

    latency_ms = (end - start) * 1000

    output_text = result.model_dump_json()

    print("\nLLM Benchmark")
    print("=============")
    print(f"Model: {provider.model_name}")
    print(f"Prompt version: {provider.prompt_version}")
    print(f"Input tokens (estimated): {count_tokens(input_text)}")
    print(f"Output tokens (estimated): {count_tokens(output_text)}")
    print(f"Latency: {latency_ms:.2f} ms")


if __name__ == "__main__":
    asyncio.run(main())
