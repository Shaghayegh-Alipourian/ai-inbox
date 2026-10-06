from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.domain.enums import AnalysisStatus, EmailCategory, Priority


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="email",
        cascade="all, delete-orphan",
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_id: Mapped[int] = mapped_column(ForeignKey("emails.id"))

    category: Mapped[EmailCategory] = mapped_column(String(50))
    priority: Mapped[Priority] = mapped_column(String(20))

    invoice_id: Mapped[str | None] = mapped_column(String(100))
    due_date: Mapped[date | None] = mapped_column(Date)

    action_required: Mapped[bool] = mapped_column(Boolean)

    suggested_reply: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column()

    status: Mapped[AnalysisStatus] = mapped_column(String(30))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    email: Mapped[Email] = relationship(back_populates="analyses")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_version: Mapped[str] = mapped_column(
        String(100),
        default="v1",
    )
    prompt_version: Mapped[str] = mapped_column(
        String(20),
        default="v1",
    )
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))

    total_cases: Mapped[int] = mapped_column(Integer)
    successful_cases: Mapped[int] = mapped_column(Integer)
    failed_cases: Mapped[int] = mapped_column(Integer)

    classification_accuracy: Mapped[float] = mapped_column()
    priority_accuracy: Mapped[float] = mapped_column()
    extraction_accuracy: Mapped[float] = mapped_column()
    action_required_accuracy: Mapped[float] = mapped_column()
    structured_output_validity: Mapped[float] = mapped_column()
    response_quality: Mapped[float] = mapped_column()

    average_latency_ms: Mapped[float] = mapped_column(default=0.0)
    average_ttft_ms: Mapped[float] = mapped_column(default=0.0)
    average_input_tokens: Mapped[float] = mapped_column(default=0.0)
    average_output_tokens: Mapped[float] = mapped_column(default=0.0)
    average_cost: Mapped[float] = mapped_column(default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    results: Mapped[list["EvaluationResult"]] = relationship(
        back_populates="evaluation_run",
        cascade="all, delete-orphan",
    )


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    evaluation_run_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_runs.id"),
    )

    case_id: Mapped[str] = mapped_column(String(100))
    valid_output: Mapped[bool] = mapped_column(Boolean)

    classification_accuracy: Mapped[float] = mapped_column()
    priority_accuracy: Mapped[float] = mapped_column()
    extraction_accuracy: Mapped[float] = mapped_column()
    action_required_accuracy: Mapped[float] = mapped_column()
    structured_output_validity: Mapped[float] = mapped_column()
    response_quality: Mapped[float] = mapped_column()

    error: Mapped[str | None] = mapped_column(Text)

    evaluation_run: Mapped["EvaluationRun"] = relationship(
        back_populates="results",
    )
