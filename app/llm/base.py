from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.llm.schemas import LLMEmailAnalysis


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class LLMRunMetrics:
    input_tokens: int
    output_tokens: int
    latency_ms: float
    ttft_ms: float | None = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMProvider(ABC):
    provider_name: str
    model_name: str

    @abstractmethod
    async def analyze_email(
        self,
        subject: str,
        body: str,
    ) -> LLMEmailAnalysis:
        raise NotImplementedError

    @abstractmethod
    async def stream_analysis(
        self,
        subject: str,
        body: str,
    ) -> AsyncIterator[str]:
        raise NotImplementedError

    @property
    def last_run_metrics(self) -> LLMRunMetrics | None:
        return None
