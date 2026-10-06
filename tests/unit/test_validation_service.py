from app.domain.enums import EmailCategory, Priority
from app.llm.schemas import LLMEmailAnalysis
from app.services.validation_service import validate_analysis


def test_llm_analysis_is_converted_to_domain_schema() -> None:
    llm_analysis = LLMEmailAnalysis(
        category=EmailCategory.SUPPORT,
        priority=Priority.NORMAL,
        invoice_id=None,
        due_date=None,
        action_required=True,
        suggested_reply="We will look into this.",
        confidence=0.88,
    )

    result = validate_analysis(llm_analysis)

    assert result.category == EmailCategory.SUPPORT
    assert result.priority == Priority.NORMAL
    assert result.action_required is True
