# AI Email Intelligence Platform

An AI assistant for email management — instead of simply displaying emails,
it **understands** them and organizes the important information automatically.

## What it does

For every email ingested, the platform automatically:

- **Categorizes** it — Urgent, Action Needed, Meeting, Informational, or Spam-like
- **Scores priority** (0-100) based on category, urgency keywords, and deadlines
- **Extracts action items** — the actual sentences asking you to do something
- **Extracts deadlines** — phrases like "by Friday" or "before March 5th", resolved to real dates where possible
- **Summarizes** long emails down to their 2-3 most important sentences
- **Surfaces keywords** — the most distinctive terms in the email

It's built as a hybrid system: a fast, free, fully offline rule-based +
statistical layer runs by default, with an *optional* LLM enhancement layer
(Claude/Anthropic) that kicks in automatically if you configure an API key —
so the platform works with zero cost and zero setup, and gets smarter if you
want it to.

## Tech stack

- **Flask** — REST API layer
- **SQLAlchemy + SQLite** — data persistence (swappable for Postgres/MySQL)
- **Pydantic** — request/response validation and serialization
- **scikit-learn** — TF-IDF based extractive summarization & keyword extraction
- **python-dateutil** — deadline date resolution
- **Anthropic API** (optional) — LLM-enhanced categorization/summarization

## Project structure

```
email_ai_platform/
├── app/
│   ├── main.py          # Flask app & routes
│   ├── ai_engine.py     # The intelligence layer (categorization, extraction, summarization)
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response schemas
│   └── database.py      # DB session/config
├── sample_data/
│   └── sample_emails.json
├── demo.py              # Standalone script — see the AI engine work without the server
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) enable LLM-enhanced mode
export ANTHROPIC_API_KEY=your_key_here    # Windows: set ANTHROPIC_API_KEY=your_key_here
```

## Quick demo (no server needed)

```bash
python demo.py
```

This runs the AI engine directly on the sample emails and prints categorization,
priority scores, summaries, action items, and deadlines to your terminal —
the fastest way to see it working.

## Running the full API

```bash
python app/main.py
```

The API will be available at **http://127.0.0.1:5000**.

### Example: ingest an email

```bash
curl -X POST http://127.0.0.1:5000/emails/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "sender": "manager@company.com",
        "subject": "Urgent: Q3 report needed by Friday",
        "body": "Please send me the Q3 report by Friday EOD, this is urgent."
      }'
```

### Example: load all sample emails at once

```bash
curl -X POST http://127.0.0.1:5000/emails/batch-ingest \
  -H "Content-Type: application/json" \
  -d @sample_data/sample_emails.json
```

### Example: view dashboard stats

```bash
curl http://127.0.0.1:5000/dashboard/stats
```

## API Endpoints

| Method | Endpoint                | Description                              |
|--------|-------------------------|-------------------------------------------|
| POST   | `/emails/ingest`        | Ingest & process a single email           |
| POST   | `/emails/batch-ingest`  | Ingest & process multiple emails at once  |
| GET    | `/emails/`              | List processed emails (filter/sort)       |
| GET    | `/emails/{id}`          | Get a single processed email              |
| DELETE | `/emails/{id}`          | Delete an email                           |
| GET    | `/dashboard/stats`      | Aggregate stats — category breakdown, avg priority, upcoming deadlines |

## Design notes / possible extensions

- **IMAP ingestion**: swap the manual `/emails/ingest` calls for a scheduled
  job that pulls from a real inbox via `imaplib` and feeds emails into the
  same pipeline.
- **Better summarization**: the TF-IDF approach is intentionally lightweight
  and dependency-free; swapping in a transformer-based summarizer (e.g. via
  Hugging Face) would improve quality at the cost of needing a model download.
- **Auth**: add API key/JWT auth before deploying this anywhere beyond local
  development.
- **Frontend**: the API is fully decoupled from any UI — a React dashboard
  could consume `/dashboard/stats` and `/emails/` directly.
