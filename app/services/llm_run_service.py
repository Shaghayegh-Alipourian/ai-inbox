import time
from collections.abc import Callable
from dataclasses import dataclass

import tiktoken


@dataclass(frozen=True)
class LLMRunMetrics:
    input_tokens: int
    output_tokens: int
    latency_ms: float
    ttft_ms: float | None = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def count_tokens(
    text: str,
    encoding_name: str = "cl100k_base",
) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def measure_execution[T](
    function: Callable[[], T],
    input_text: str,
    output_text: str,
) -> tuple[T, LLMRunMetrics]:
    start = time.perf_counter()

    result = function()

    latency_ms = (time.perf_counter() - start) * 1000

    metrics = LLMRunMetrics(
        input_tokens=count_tokens(input_text),
        output_tokens=count_tokens(output_text),
        latency_ms=latency_ms,
    )

    return result, metrics
