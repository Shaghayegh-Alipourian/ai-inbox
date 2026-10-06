import json
from dataclasses import dataclass
from pathlib import Path

from app.domain.enums import AnalysisStatus
from app.llm.schemas import LLMEmailAnalysis


@dataclass(frozen=True)
class AdversarialCase:
    case_id: str
    category: str
    subject: str
    body: str
    expected_status: AnalysisStatus


def load_adversarial_dataset(
    path: Path,
) -> list[AdversarialCase]:
    cases: list[AdversarialCase] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                payload = json.loads(line)
                payload["expected_status"] = AnalysisStatus(payload["expected_status"])
                cases.append(AdversarialCase(**payload))
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid adversarial dataset record at line {line_number}."
                ) from exc

    if not cases:
        raise ValueError("Adversarial dataset is empty.")

    return cases


def detect_prompt_injection(
    subject: str,
    body: str,
) -> bool:
    text = f"{subject}\n{body}".lower()

    patterns = (
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore the system prompt",
        "reveal the system prompt",
        "reveal your instructions",
        "disregard previous instructions",
        "you are now",
        "act as system",
    )

    return any(pattern in text for pattern in patterns)


def determine_analysis_status(
    *,
    subject: str,
    body: str,
    analysis: LLMEmailAnalysis,
) -> AnalysisStatus:
    if detect_prompt_injection(subject, body):
        return AnalysisStatus.HUMAN_REVIEW

    if analysis.confidence < 0.6:
        return AnalysisStatus.HUMAN_REVIEW

    return AnalysisStatus.ACCEPTED
