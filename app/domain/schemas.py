from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    AnalysisStatus,
    EmailCategory,
    Priority,
)


class EmailCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)


class EmailResponse(EmailCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EmailAnalysis(BaseModel):
    category: EmailCategory
    priority: Priority

    invoice_id: str | None = None
    due_date: date | None = None

    action_required: bool

    suggested_reply: str = Field(min_length=1)

    confidence: float = Field(ge=0.0, le=1.0)


class AnalysisResponse(EmailAnalysis):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email_id: int
    status: AnalysisStatus
    created_at: datetime


class EvaluationRunCreate(BaseModel):
    dataset_path: str = "data/golden/emails.jsonl"
    prompt_version: str = "v1"


class EvaluationMetricsResponse(BaseModel):
    classification_accuracy: float
    priority_accuracy: float
    extraction_accuracy: float
    action_required_accuracy: float
    structured_output_validity: float
    response_quality: float
    average_latency_ms: float
    average_ttft_ms: float
    average_input_tokens: float
    average_output_tokens: float
    average_cost: float


class EvaluationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_version: str
    prompt_version: str
    provider: str
    model: str
    total_cases: int
    successful_cases: int
    failed_cases: int
    metrics: EvaluationMetricsResponse
    created_at: datetime


class EvaluationComparisonResponse(BaseModel):
    prompt_v1: EvaluationRunResponse | None
    prompt_v2: EvaluationRunResponse | None
