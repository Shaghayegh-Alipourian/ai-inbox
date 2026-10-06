from pathlib import Path

from app.evaluation.adversarial import load_adversarial_dataset

DATASET_PATH = Path("data/adversarial/cases.jsonl")


def test_adversarial_dataset_is_not_empty() -> None:
    cases = load_adversarial_dataset(DATASET_PATH)

    assert cases


def test_adversarial_dataset_contains_required_categories() -> None:
    cases = load_adversarial_dataset(DATASET_PATH)

    categories = {case.category for case in cases}

    assert "incomplete" in categories
    assert "conflicting" in categories
    assert "prompt_injection" in categories
    assert "malicious" in categories


def test_adversarial_cases_have_expected_status() -> None:
    cases = load_adversarial_dataset(DATASET_PATH)

    for case in cases:
        assert case.expected_status.value in {
            "accepted",
            "retry",
            "rejected",
            "human_review",
        }
