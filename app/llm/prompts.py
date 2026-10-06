from pathlib import Path

PROMPT_ROOT = Path(__file__).resolve().parents[2] / "prompts"


USER_PROMPT_TEMPLATE = """
Analyze this email.

Subject:
{subject}

Body:
{body}
"""


def load_system_prompt(version: str) -> str:
    if version not in {"v1", "v2"}:
        raise ValueError(f"Unsupported prompt version: {version}")

    prompt_path = PROMPT_ROOT / version / "email_analysis.txt"

    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8").strip()
