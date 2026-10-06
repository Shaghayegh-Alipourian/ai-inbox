import asyncio
from pathlib import Path

from app.evaluation.ab_test import ABTestRunner
from app.evaluation.dataset import load_dataset
from app.evaluation.regression import check_regression
from app.llm.groq_provider import GroqProvider

DATASET_PATH = Path("data/golden/emails.jsonl")


async def main() -> None:
    cases = load_dataset(DATASET_PATH)

    runner = ABTestRunner(
        lambda version: GroqProvider(
            prompt_version=version,
        ),
    )

    report = await runner.run(cases)

    v1 = report.prompt_v1
    v2 = report.prompt_v2

    print("\nPrompt A/B Test")
    print("================")

    print("\nV1")
    print(f"Cases: {v1.total_cases}")
    print(f"Classification: {v1.metrics.classification_accuracy:.2%}")
    print(f"Extraction: {v1.metrics.extraction_accuracy:.2%}")
    print(f"Action required: {v1.metrics.action_required_accuracy:.2%}")
    print(f"Structured validity: {v1.metrics.structured_output_validity:.2%}")
    print(f"Response quality: {v1.metrics.response_quality:.2%}")

    print("\nV2")
    print(f"Cases: {v2.total_cases}")
    print(f"Classification: {v2.metrics.classification_accuracy:.2%}")
    print(f"Extraction: {v2.metrics.extraction_accuracy:.2%}")
    print(f"Action required: {v2.metrics.action_required_accuracy:.2%}")
    print(f"Structured validity: {v2.metrics.structured_output_validity:.2%}")
    print(f"Response quality: {v2.metrics.response_quality:.2%}")

    regression = check_regression(
        baseline=v1.metrics,
        current=v2.metrics,
    )

    print("\nRegression")
    print("===========")
    print(f"Passed: {regression.passed}")

    for failure in regression.failures:
        print(f"- {failure}")


if __name__ == "__main__":
    asyncio.run(main())
