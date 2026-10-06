# AI Inbox — Intelligent Email Assistant

AI-powered email analysis service built with **FastAPI**, **SQLAlchemy**, **Pydantic**, and **Groq**.

The system receives emails, stores them, analyzes them with an LLM, extracts structured information, assigns priority, detects required actions, and generates a suggested reply.

It also includes streaming analysis, evaluation, prompt A/B testing, regression checks, adversarial testing, and token/cost/latency tracking.

---

## Features

* Email creation and storage
* Email inbox listing
* Individual email inspection
* LLM-based email analysis
* Email classification
* Priority detection
* Invoice ID extraction
* Due-date extraction
* Action-required detection
* Suggested reply generation
* Structured JSON output
* Pydantic validation
* Prompt injection detection
* Human-review decision
* Streaming AI analysis with SSE
* Golden evaluation dataset
* Prompt V1 / V2 comparison
* Regression testing
* Adversarial test cases
* Token usage tracking
* Latency and TTFT tracking
* Estimated LLM cost calculation
* Evaluation API
* Web-based inbox and evaluation dashboard

---

## Architecture

```text
                    ┌─────────────────┐
                    │    Frontend     │
                    │    AI Inbox     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │      API        │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │ Email Service   │          │ Evaluation API  │
     └────────┬────────┘          └────────┬────────┘
              │                            │
              ▼                            ▼
     ┌─────────────────┐          ┌─────────────────┐
     │ Analysis        │          │ Evaluation      │
     │ Service         │          │ Runner          │
     └────────┬────────┘          └────────┬────────┘
              │                            │
              ▼                            ▼
     ┌─────────────────────────────────────────────┐
     │              LLM Provider Layer             │
     │                    Groq                     │
     └──────────────────────┬──────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Structured JSON  │
                  │ + Pydantic      │
                  │ Validation      │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Business Rules   │
                  └────────┬─────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          ACCEPT       HUMAN REVIEW    REJECT/RETRY
```

---

## Project Structure

```text
ai-inbox/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── emails.py
│   │       ├── analysis.py
│   │       └── evaluation.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── domain/
│   │   ├── enums.py
│   │   └── schemas.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── groq_provider.py
│   │   ├── prompts.py
│   │   ├── schemas.py
│   │   └── streaming.py
│   │
│   ├── services/
│   │   ├── email_service.py
│   │   ├── analysis_service.py
│   │   ├── validation_service.py
│   │   ├── evaluation_service.py
│   │   └── cost_service.py
│   │
│   ├── evaluation/
│   │   ├── dataset.py
│   │   ├── metrics.py
│   │   ├── runner.py
│   │   ├── ab_test.py
│   │   ├── regression.py
│   │   └── adversarial.py
│   │
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── evaluation/
│   └── adversarial/
│
├── data/
│   ├── golden/
│   │   └── emails.jsonl
│   └── adversarial/
│       └── cases.jsonl
│
├── prompts/
│   ├── v1/
│   │   └── email_analysis.txt
│   └── v2/
│       └── email_analysis.txt
│
├── scripts/
│   ├── run_evaluation.py
│   └── benchmark_llm.py
│
├── migrations/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── docker-compose.yml
```

---

## Main API

### Health

```http
GET /health
```

Checks whether the application is running.

### Create Email

```http
POST /api/v1/emails
```

Creates and stores an email.

### List Emails

```http
GET /api/v1/emails
```

Returns the inbox.

### Get Email

```http
GET /api/v1/emails/{email_id}
```

Returns a single email.

### Analyze Email

```http
POST /api/v1/emails/{email_id}/analyze
```

Runs the email through the LLM analysis pipeline.

### Stream Analysis

```http
GET /api/v1/emails/{email_id}/analyze/stream
```

Streams the LLM response to the browser using Server-Sent Events.

### Run Evaluation

```http
POST /api/v1/evaluation/run
```

Runs the evaluation dataset against the selected prompt version.

### Get Evaluation Run

```http
GET /api/v1/evaluation/runs/{run_id}
```

Returns a stored evaluation result.

### Compare Prompts

```http
GET /api/v1/evaluation/compare
```

Compares the latest V1 and V2 evaluation runs.

---

## Analysis Pipeline

```text
Email
  │
  ▼
FastAPI
  │
  ▼
Analysis Service
  │
  ▼
Prompt Engine
  │
  ▼
Groq Provider
  │
  ▼
Structured JSON
  │
  ▼
Pydantic Validation
  │
  ▼
Business Rules
  │
  ├── ACCEPT
  ├── HUMAN REVIEW
  ├── RETRY
  └── REJECT
```

The analysis returns structured information such as:

```json
{
  "category": "invoice",
  "priority": "high",
  "invoice_id": "INV-2026-001",
  "due_date": "2026-10-15",
  "action_required": true,
  "suggested_reply": "Thank you for your email...",
  "confidence": 0.94
}
```

---

## Evaluation

The project includes a golden dataset containing at least 100 email cases.

Evaluation metrics include:

* Classification Accuracy
* Priority Accuracy
* Extraction Accuracy
* Action Required Accuracy
* Structured Output Validity
* Response Quality
* Average Latency
* Average TTFT
* Average Input Tokens
* Average Output Tokens
* Estimated Cost

### Evaluation Flow

```text
Golden Dataset
      │
      ▼
Evaluation Runner
      │
      ├──────────────┐
      ▼              ▼
   Prompt V1      Prompt V2
      │              │
      └──────┬───────┘
             ▼
        Groq Provider
             │
             ▼
         Validation
             │
             ▼
           Metrics
             │
             ▼
      Evaluation Report
```

---

## Prompt A/B Testing

Two prompt versions are maintained:

```text
prompts/
├── v1/
│   └── email_analysis.txt
└── v2/
    └── email_analysis.txt
```

The same evaluation dataset can be executed against both versions to compare their performance.

---

## Adversarial Testing

The project includes adversarial cases such as:

* Prompt injection
* Conflicting information
* Invalid inputs
* Out-of-scope emails
* Incomplete emails
* Long inputs
* Malicious instructions

Prompt injection detection is applied before accepting the analysis result.

---

## Token, Latency and Cost Tracking

The LLM provider records:

```text
Input Tokens
Output Tokens
Total Tokens
Latency
TTFT
Estimated Cost
```

Cost is calculated using the configured model pricing.

Current provider:

```text
Groq
└── openai/gpt-oss-20b
```

---

## Tech Stack

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite
* Groq
* tiktoken
* pytest
* pytest-asyncio
* Ruff
* SSE
* Vanilla JavaScript
* HTML
* CSS

---

## Requirements

* Python 3.12+
* `uv`
* Groq API key

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd ai-inbox
```

Install dependencies:

```bash
uv sync
```

Create the environment file:

```bash
cp .env.example .env
```

Set your Groq API key in `.env`:

```env
GROQ_API_KEY=your_api_key_here
```

---

## Run the Application

```bash
uv run uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Run Tests

Run the complete test suite:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check .
```

Format the project:

```bash
uv run ruff format .
```

Verify formatting:

```bash
uv run ruff format --check .
```

Recommended full verification:

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run ruff format --check .
```

---

## Run Evaluation

The evaluation requires a valid Groq API key.

```bash
uv run python scripts/run_evaluation.py
```

The evaluation runs the golden dataset and reports the model's performance across the defined metrics.

---

## Environment Variables

Example:

```env
APP_NAME=AI Inbox
APP_VERSION=1.0.0
DEBUG=true

DATABASE_URL=sqlite+aiosqlite:///./ai_inbox.db

GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit `.env` or API keys to GitHub.

---

## Development Philosophy

The project is implemented incrementally with a production-minded approach.

For every change:

1. Identify the root cause.
2. Inspect the current implementation.
3. Make the smallest justified change.
4. Keep all layers compatible.
5. Run tests.
6. Run lint.
7. Run formatting checks.
8. Verify the result before continuing.

---

## Project Status

Current implementation includes:

* [x] FastAPI foundation
* [x] SQLite + SQLAlchemy
* [x] Email CRUD
* [x] Groq provider abstraction
* [x] Structured LLM output
* [x] Pydantic validation
* [x] Streaming analysis
* [x] Frontend inbox
* [x] Golden dataset
* [x] Evaluation runner
* [x] Prompt V1/V2
* [x] A/B evaluation
* [x] Regression checks
* [x] Adversarial dataset
* [x] Prompt injection detection
* [x] Token tracking
* [x] Latency / TTFT tracking
* [x] Cost estimation
* [x] Evaluation API
* [x] Evaluation dashboard
* [ ] LLM-as-Judge
* [ ] PostgreSQL production migration
* [ ] Complete Alembic migration workflow
* [ ] CI/CD pipeline
* [ ] Multi-provider production support

---

## License

This project is developed as an AI Engineering internship project.
