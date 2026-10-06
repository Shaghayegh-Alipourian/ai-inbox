from enum import StrEnum


class EmailCategory(StrEnum):
    PAYMENT_ISSUE = "payment_issue"
    SUPPORT = "support"
    SALES = "sales"
    COMPLAINT = "complaint"
    INVOICE = "invoice"
    MEETING = "meeting"
    OTHER = "other"


class Priority(StrEnum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class AnalysisStatus(StrEnum):
    ACCEPTED = "accepted"
    RETRY = "retry"
    REJECTED = "rejected"
    HUMAN_REVIEW = "human_review"
