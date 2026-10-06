from app.services.llm_run_service import (
    count_tokens,
    measure_execution,
)


def test_count_tokens_returns_positive_value() -> None:
    result = count_tokens(
        "This is a test email.",
    )

    assert result > 0


def test_measure_execution() -> None:
    result, metrics = measure_execution(
        function=lambda: "analysis result",
        input_text="Analyze this email.",
        output_text="analysis result",
    )

    assert result == "analysis result"
    assert metrics.input_tokens > 0
    assert metrics.output_tokens > 0
    assert metrics.latency_ms >= 0
