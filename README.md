# AI Email Intelligence Platform

An email processing API that automatically categorizes, prioritizes, summarizes, and extracts actionable information from emails. It combines rule-based logic and statistical NLP (TF-IDF) for fast, deterministic processing, with an optional LLM enhancement layer (Claude/Anthropic) that can refine results when configured.

## Overview

Rather than simply storing emails, this platform analyzes each one and surfaces what matters: urgency, required actions, deadlines, and a concise summary. The core pipeline runs entirely offline with no external dependencies or cost. An optional integration with the Anthropic API allows Claude to refine categorization and summarization when an API key is configured, with automatic fallback to the rule-based result if the key is missing, invalid, or the request fails for any reason.

## Features

- **Categorization** — classifies each email as Urgent, Action Needed, Meeting, Informational, or Spam-like
- **Priority scoring** — assigns a 0-100 score based on category, urgency language, and detected deadlines
- **Action item extraction** — identifies sentences that request a specific action
- **Deadline detection** — parses phrases such as "by Friday" or "before Friday's meeting" and resolves them to concrete dates
- **Extractive summarization** — condenses longer emails to their most informative sentences using TF-IDF
- **Keyword extraction** — surfaces the most distinctive terms in an email
- **Optional LLM enhancement** — refines categorization and summaries via the Anthropic API when configured
- **Dashboard statistics** — aggregate view of email volume by category, average priority, and upcoming deadlines

## Architecture

```
Email input
    |
    v
Categorize  ->  Extract deadline  ->  Calculate priority score
    |
    v
Extract action items  ->  Summarize  ->  Extract keywords
    |
    v
(Optional) Refine category and summary via Claude
    |
    v
Persist to database  ->  Return processed result as JSON
```

Every email passes through the same deterministic pipeline defined in `ai_engine.py`, making results fast, explainable, and reproducible.

## Tech Stack

- **Flask** — REST API framework
- **Flask-SQLAlchemy** with **SQLite** — ORM and persistence (the connection string can be swapped for PostgreSQL or MySQL in production)
- **Pydantic** — request and response validation and serialization
- **scikit-learn** — TF-IDF vectorization for summarization and keyword extraction
- **python-dateutil** — natural-language date parsing
- **Anthropic API** (optional) — LLM-based refinement of categorization and summaries

## Project Structure

```
email_ai_platform/
├── app/
│   ├── __init__.py       # Marks app/ as a Python package
│   ├── main.py            # Flask app and API routes
│   ├── ai_engine.py       # Categorization, extraction, summarization, and optional LLM layer
│   ├── models.py          # Flask-SQLAlchemy database models
│   ├── schemas.py         # Pydantic request/response schemas
│   └── database.py        # Database configuration and initialization
├── requirements.txt
├── .env                    # Local only; holds ANTHROPIC_API_KEY, never committed
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+

### Installation

Clone the repository:
```bash
git clone https://github.com/kavya608/ai-email-intelligence-platform.git email_ai_platform
cd email_ai_platform
```

Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Optional: enable LLM-enhanced mode

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
```
An API key can be generated at [console.anthropic.com](https://console.anthropic.com) under API Keys. This step is optional — the application runs fully without it and uses rule-based results only.

### Running the server

```bash
python -m app.main
```

The API is available at `http://127.0.0.1:5000`.

## API Reference

### `POST /emails/ingest`
Processes and stores a single email.

Request body:
```json
{
  "sender": "manager@company.com",
  "subject": "Urgent: Q3 report needed",
  "body": "Please send me the Q3 report by Friday EOD, this is urgent."
}
```

Response (`201 Created`):
```json
{
  "id": 1,
  "sender": "manager@company.com",
  "subject": "Urgent: Q3 report needed",
  "body": "Please send me the Q3 report by Friday EOD, this is urgent.",
  "category": "Urgent",
  "priority_score": 100,
  "summary": "Please send me the Q3 report by Friday EOD, this is urgent.",
  "action_items": "Please send me the Q3 report by Friday EOD, this is urgent.",
  "deadline": "2026-07-17T17:53:35.553726",
  "keywords": null,
  "created_at": "2026-07-11T12:23:35.557403"
}
```

### `POST /emails/batch-ingest`
Processes multiple emails in a single request. Validation failures are reported per item; one invalid email does not block the rest of the batch from processing.

Request body:
```json
[
  { "sender": "a@test.com", "subject": "Hi", "body": "Please send the invoice by Monday." },
  { "sender": "b@test.com", "subject": "Broken one" }
]
```

Response (`201 Created`):
```json
{
  "created": [ { "id": 7, "category": "Action Needed" } ],
  "errors": [ { "index": 1, "error": [ { "loc": ["body"], "msg": "Field required" } ] } ]
}
```

### `GET /emails/`
Lists processed emails, newest first.

Query parameters:
- `category` (optional) — filter by category, e.g. `?category=Urgent`

### `GET /emails/{id}`
Retrieves a single processed email by id. Returns `404` if not found.

### `DELETE /emails/{id}`
Deletes an email by id. Returns `404` if not found.

### `GET /dashboard/stats`
Returns aggregate statistics.

Response:
```json
{
  "total_emails": 6,
  "category_breakdown": { "Urgent": 2, "Meeting": 2, "Action Needed": 2 },
  "average_priority": 75.0,
  "upcoming_deadlines": [
    { "id": 6, "subject": "Test", "deadline": "2026-07-13T18:08:39.404219" }
  ]
}
```

## Example Usage

With the server running, in a separate terminal:

```bash
curl -X POST http://127.0.0.1:5000/emails/ingest \
  -H "Content-Type: application/json" \
  -d "{\"sender\": \"boss@company.com\", \"subject\": \"Urgent\", \"body\": \"Please review this before Friday's meeting, it's urgent.\"}"

curl http://127.0.0.1:5000/emails/
curl http://127.0.0.1:5000/dashboard/stats
```

## Known Limitations

- **Keyword extraction favors shorter sentences.** `extract_keywords()` computes TF-IDF per sentence with L2 normalization, which means a short, generic sentence can receive a higher aggregate score than a longer sentence with more distinctive vocabulary, simply because its score is concentrated across fewer words. A whole-document TF-IDF approach would reduce this effect.
- **Deadline parsing relies on regex pattern matching combined with fuzzy date parsing, rather than a full NLP-based date resolver.** It correctly handles common constructions, including possessives such as "Friday's meeting," but may not capture indirect or unusual phrasing.
- **Categorization is single-label and priority-ordered.** Each email receives exactly one category, with ties resolved by a fixed precedence: Urgent, then Meeting, then Action Needed, then Spam-like, then Informational.
- **Action items and keywords are persisted as delimited strings** rather than normalized relational data. This is sufficient at the current scale but would require a join table to support efficient querying by keyword.

## Possible Extensions

- Live inbox ingestion via IMAP, replacing manual API calls
- Transformer-based summarization as an upgrade to the TF-IDF approach
- Authentication (API key or JWT) prior to any deployment beyond local development
- A frontend dashboard consuming the existing API endpoints directly
- Full-text search across stored emails
