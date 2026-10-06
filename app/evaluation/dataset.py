import json
from dataclasses import dataclass
from pathlib import Path

from app.domain.enums import EmailCategory, Priority


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    subject: str
    body: str
    expected_category: EmailCategory
    expected_priority: Priority
    expected_invoice_id: str | None
    expected_due_date: str | None
    expected_action_required: bool


def load_dataset(path: Path) -> list[EvaluationCase]:
    cases: list[EvaluationCase] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                payload = json.loads(line)

                payload["expected_category"] = EmailCategory(
                    payload["expected_category"]
                )
                payload["expected_priority"] = Priority(payload["expected_priority"])

                cases.append(EvaluationCase(**payload))

            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid dataset record at line {line_number}."
                ) from exc

    if not cases:
        raise ValueError("Evaluation dataset is empty.")

    return cases
