import asyncio
from pathlib import Path

from app.evaluation.adversarial import (
    detect_prompt_injection,
    load_adversarial_dataset,
)
from app.llm.groq_provider import GroqProvider

DATASET_PATH = Path("data/adversarial/cases.jsonl")


async def main() -> None:
    cases = load_adversarial_dataset(DATASET_PATH)

    provider = GroqProvider()

    print("\nAdversarial Evaluation")
    print("======================")

    for case in cases:
        print(f"\n[{case.case_id}] {case.category}")
        print(f"Subject: {case.subject}")

        injection_detected = detect_prompt_injection(
            subject=case.subject,
            body=case.body,
        )

        if injection_detected:
            print("Result: HUMAN_REVIEW")
            print("Reason: prompt injection detected")
            continue

        try:
            result = await provider.analyze_email(
                subject=case.subject,
                body=case.body,
            )

            print(f"Confidence: {result.confidence:.2f}")
            print(f"Category: {result.category.value}")
            print(f"Priority: {result.priority.value}")

            if result.confidence < 0.6:
                print("Result: HUMAN_REVIEW")
            else:
                print("Result: ACCEPTED")

        except Exception as exc:
            print("Result: RETRY")
            print(f"Error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
