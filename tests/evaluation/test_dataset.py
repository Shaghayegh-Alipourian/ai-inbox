from pathlib import Path

from app.evaluation.dataset import load_dataset

DATASET_PATH = Path("data/golden/emails.jsonl")


def test_golden_dataset_has_at_least_100_cases() -> None:
    cases = load_dataset(DATASET_PATH)

    assert len(cases) >= 100


def test_dataset_case_has_required_fields() -> None:
    cases = load_dataset(DATASET_PATH)

    case = cases[0]

    assert case.case_id
    assert case.subject
    assert case.body
    assert case.expected_category
    assert case.expected_priority
    assert isinstance(case.expected_action_required, bool)
