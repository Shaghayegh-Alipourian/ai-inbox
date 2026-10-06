from app.domain.schemas import EmailAnalysis
from app.llm.schemas import LLMEmailAnalysis


def validate_analysis(
    analysis: LLMEmailAnalysis,
) -> EmailAnalysis:
    return EmailAnalysis.model_validate(
        analysis.model_dump(),
    )
