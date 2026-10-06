from app.services.cost_service import (
    ModelPricing,
    TokenUsage,
    calculate_cost,
)


def test_total_tokens() -> None:
    usage = TokenUsage(
        input_tokens=100,
        output_tokens=50,
    )

    assert usage.total_tokens == 150


def test_calculate_cost() -> None:
    usage = TokenUsage(
        input_tokens=1_000_000,
        output_tokens=500_000,
    )

    pricing = ModelPricing(
        input_per_million=1.0,
        output_per_million=2.0,
    )

    cost = calculate_cost(
        usage=usage,
        pricing=pricing,
    )

    assert cost == 2.0
