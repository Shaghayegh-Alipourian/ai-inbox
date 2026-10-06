import asyncio
from pathlib import Path

from app.evaluation.dataset import load_dataset
from app.evaluation.runner import EvaluationRunner
from app.llm.groq_provider import GroqProvider


DATASET_PATH = Path("data/golden/emails.jsonl")


async def main() -> None:
    cases = load_dataset(DATASET_PATH)
    provider = GroqProvider()

    report = await EvaluationRunner(provider).run(cases)

    print("\nEvaluation Report")
    print("=================")
    print(f"Total cases: {report.total_cases}")
    print(f"Successful: {report.successful_cases}")
    print(f"Failed: {report.failed_cases}")
    print(f"Classification accuracy: {report.metrics.classification_accuracy:.2%}")
    print(f"Priority accuracy: {report.metrics.priority_accuracy:.2%}")
    print(f"Extraction accuracy: {report.metrics.extraction_accuracy:.2%}")
    print(f"Action required accuracy: {report.metrics.action_required_accuracy:.2%}")
    print(
        f"Structured output validity: {report.metrics.structured_output_validity:.2%}"
    )
    print(f"Response quality: {report.metrics.response_quality:.2%}")
    print(f"Average latency: {report.metrics.average_latency_ms:.2f} ms")
    print(f"Average TTFT: {report.metrics.average_ttft_ms:.2f} ms")
    print(f"Average input tokens: {report.metrics.average_input_tokens:.2f}")
    print(f"Average output tokens: {report.metrics.average_output_tokens:.2f}")
    print(f"Average cost: ${report.metrics.average_cost:.8f}")

    failures = [result for result in report.results if not result.valid_output]

    if failures:
        print("\nFirst failures")
        print("==============")
        for result in failures[:5]:
            print(f"{result.case_id}: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
