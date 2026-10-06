from dataclasses import dataclass


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: float
    output_per_million: float


MODEL_PRICING: dict[str, ModelPricing] = {
    "openai/gpt-oss-20b": ModelPricing(
        input_per_million=0.075,
        output_per_million=0.30,
    ),
}


def get_model_pricing(model_name: str) -> ModelPricing:
    try:
        return MODEL_PRICING[model_name]
    except KeyError as exc:
        raise ValueError(
            f"No pricing configuration found for model: {model_name}"
        ) from exc


def calculate_cost(
    usage: TokenUsage,
    pricing: ModelPricing,
) -> float:
    input_cost = (usage.input_tokens / 1_000_000) * pricing.input_per_million

    output_cost = (usage.output_tokens / 1_000_000) * pricing.output_per_million

    return input_cost + output_cost
