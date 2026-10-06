from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EmailCategory, Priority


class LLMEmailAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: EmailCategory
    priority: Priority

    invoice_id: str | None
    due_date: str | None

    action_required: bool

    suggested_reply: str = Field(min_length=1)

    confidence: float = Field(ge=0.0, le=1.0)
