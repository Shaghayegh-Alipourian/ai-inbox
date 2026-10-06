import json
from pathlib import Path

from app.domain.enums import EmailCategory, Priority

OUTPUT_PATH = Path("data/golden/emails.jsonl")

TEMPLATES = [
    (
        EmailCategory.PAYMENT_ISSUE,
        Priority.HIGH,
        "Payment failed for invoice INV-{number}",
        "Our payment for invoice INV-{number} failed. Please help us resolve it.",
        "INV-{number}",
        None,
        True,
    ),
    (
        EmailCategory.SUPPORT,
        Priority.NORMAL,
        "Need help with account access {number}",
        "I cannot access my account and need assistance.",
        None,
        None,
        True,
    ),
    (
        EmailCategory.SALES,
        Priority.NORMAL,
        "Pricing inquiry {number}",
        "Could you send me your pricing and available plans?",
        None,
        None,
        True,
    ),
    (
        EmailCategory.COMPLAINT,
        Priority.HIGH,
        "Complaint about service {number}",
        "I am unhappy with the service and would like this issue resolved.",
        None,
        None,
        True,
    ),
    (
        EmailCategory.INVOICE,
        Priority.NORMAL,
        "Invoice INV-{number}",
        "Please find invoice INV-{number}. The payment is due on 2026-10-15.",
        "INV-{number}",
        "2026-10-15",
        True,
    ),
    (
        EmailCategory.MEETING,
        Priority.LOW,
        "Meeting request {number}",
        "Would you be available for a meeting next week?",
        None,
        None,
        True,
    ),
    (
        EmailCategory.OTHER,
        Priority.LOW,
        "General information {number}",
        "I am sending some general information for your reference.",
        None,
        None,
        False,
    ),
]


def build_dataset() -> list[dict]:
    cases: list[dict] = []

    for index in range(100):
        template_index = index % len(TEMPLATES)

        (
            category,
            priority,
            subject_template,
            body_template,
            invoice_template,
            due_date,
            action_required,
        ) = TEMPLATES[template_index]

        number = f"{index + 1:04d}"

        invoice_id = (
            invoice_template.format(number=number) if invoice_template else None
        )

        cases.append(
            {
                "case_id": f"email-{index + 1:04d}",
                "subject": subject_template.format(number=number),
                "body": body_template.format(number=number),
                "expected_category": category.value,
                "expected_priority": priority.value,
                "expected_invoice_id": invoice_id,
                "expected_due_date": due_date,
                "expected_action_required": action_required,
            }
        )

    return cases


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cases = build_dataset()

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for case in cases:
            file.write(
                json.dumps(
                    case,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"Created {len(cases)} golden dataset cases.")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
