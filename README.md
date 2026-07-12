# AI Email Intelligence Platform

An AI-powered Email Intelligence Platform that automatically analyzes, prioritizes, and organizes emails using Natural Language Processing (NLP).

The platform transforms unstructured email content into actionable insights by classifying email intent, calculating priority, generating concise summaries, extracting named entities, identifying action items, tracking deadlines, and generating context-aware reply drafts.

## Project Overview

Manually triaging a large volume of email is time-consuming. This platform processes incoming email content automatically so the important information — who's involved, what's being asked, what's due and when, and how urgent it is — is surfaced immediately rather than requiring a full read-through.

The system provides:
- Rule-based email classification
- Priority scoring
- NLP-based named entity extraction (spaCy)
- Extractive email summarization (TF-IDF)
- Action item detection
- Deadline extraction
- Template-based reply drafting
- An analytics dashboard

## Key Features

- Intelligent email classification into five categories
- Priority scoring based on urgency and deadlines
- Automatic email summarization using TF-IDF
- Named entity extraction (People, Organizations, Locations, Dates, Money)
- Action item detection
- Deadline extraction and tracking
- Smart reply drafting with configurable tone
- Analytics dashboard with email insights
- Email filtering, search, and pagination

## Email Processing Pipeline

```
Incoming Email
      |
      v
Request Validation (Pydantic)
      |
      v
Processing Engine
      |
      ├── Email Classification
      ├── Priority Calculation
      ├── Named Entity Extraction (spaCy)
      ├── Extractive Summarization (TF-IDF)
      ├── Action Item Detection
      ├── Deadline Extraction
      |
      v
Database Storage (SQLite via Flask-SQLAlchemy)
```

## AI & NLP Capabilities

### 1. Email Classification

Categorizes each email into one of five categories, checked in this order: `Spam-like`, `Urgent`, `Meeting`, `Action Needed`, `Informational`.

**Example**

Input:
```
Production server is down. Please fix immediately.
```
Output:
```json
{ "category": "Urgent" }
```

### 2. Priority Scoring

Each email receives a 0–100 priority score based on its category, presence of urgency keywords, and whether a deadline was detected.

| Category | Typical Priority |
|---|---|
| Urgent | High |
| Action Needed | Medium-High |
| Meeting | Medium |
| Informational | Low |
| Spam-like | Lowest |

### 3. Extractive Summarization

Generates concise summaries from longer emails using TF-IDF-based extractive summarization — selecting the most information-dense sentences rather than generating new text.

**Example**

Original:
```
John from Microsoft requested Rs.45000 before 18 July. Please contact Alice in Bangalore regarding payment.
```
Summary:
```
John from Microsoft requested Rs.45000 before 18 July.
```

### 4. Named Entity Extraction

Uses spaCy (`en_core_web_sm`) to extract structured entities from each email, plus a regex pass tuned for Indian currency formats layered on top of spaCy's own money detection.

| Entity type | Example |
|---|---|
| People | John, Alice |
| Organizations | Microsoft, Infosys |
| Locations | Bangalore, Hyderabad |
| Dates | 18 July |
| Money | Rs.45000, ₹45,000 |

### 5. Action Item Detection

Identifies sentences that request a specific action, using a keyword/phrase-matching approach.

**Example**

Input:
```
Please complete the API documentation before Friday.
```
Extracted:
```
Complete the API documentation before Friday.
```

### 6. Deadline Extraction

Detects deadline phrases (e.g. "by", "before", "due") and resolves them to actual dates using regex + fuzzy date parsing.

**Example**

Input:
```
Please submit the invoice before 20 July.
```
Detected:
```
Deadline: 2026-07-20
```
Upcoming deadlines are surfaced on the analytics dashboard.

## Smart Reply Assistant

Generates a draft reply based on the email's subject, body, detected category, deadline, and action items.

Supported tones: `professional` (default), `friendly`, `formal`.

**Example**

Input:
```
Please submit the report before Friday.
```
Generated reply:
```
Hi,

Thank you for your email regarding "...".

I have noted the requested action.

I will take care of the following:
Please submit the report before Friday.

I will ensure this is completed before 17 July 2026.

Regards,
AI Email Intelligence Platform
```

## Analytics Dashboard

`GET /dashboard/stats` returns:

```json
{
  "total_emails": 20,
  "category_breakdown": { "Urgent": 4, "Meeting": 3, "Action Needed": 5 },
  "average_priority": 62.5,
  "upcoming_deadlines": [
    { "id": 12, "subject": "Payment Reminder", "deadline": "2026-07-18T00:00:00" }
  ],
  "top_people": [["John", 5], ["Alice", 3]],
  "top_organizations": [["Microsoft", 4], ["Infosys", 2]],
  "top_locations": [["Bangalore", 3]],
  "urgent_emails": 2,
  "action_needed_emails": 5,
  "spam_percentage": 10.0,
  "top_senders": [["john@microsoft.com",4]]
}
```

## REST API Endpoints

The email retrieval endpoint supports:

- Pagination (`page`, `limit`)
- Category filtering
- Sender search
- Minimum priority filtering


| Method | Endpoint | Description |
|---|---|---|
| POST | `/emails/ingest` | Process and store a single email |
| POST | `/emails/batch-ingest` | Process and store multiple emails; per-item validation, one bad item doesn't block the rest |
| GET | `/emails` | Retrieve emails with pagination and filtering |
| GET | `/emails/<id>` | Retrieve a processed email by ID |
| DELETE | `/emails/<id>` | Delete a processed email |
| POST | `/emails/reply` | Generate a draft reply for a given subject/body/tone (not persisted) |
| GET | `/dashboard/stats` | Aggregate statistics across all processed emails |

### Example: ingest a single email

```bash
curl -X POST http://127.0.0.1:5000/emails/ingest \
  -H "Content-Type: application/json" \
  -d "{\"sender\": \"john@microsoft.com\", \"subject\": \"Payment Reminder\", \"body\": \"Please process payment of Rs.45000 before 18 July.\"}"
```

### Example: generate a reply

```bash
curl -X POST http://127.0.0.1:5000/emails/reply \
  -H "Content-Type: application/json" \
  -d "{\"subject\": \"Payment Reminder\", \"body\": \"Please process payment before 18 July.\", \"tone\": \"formal\"}"

```
## REST API Endpoints

### Email Management

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/emails/ingest` | Process and store a single email |
| POST | `/emails/batch-ingest` | Process multiple emails |
| GET | `/emails` | Retrieve processed emails with search, filtering and pagination support |
| GET | `/emails/<id>` | Retrieve a processed email by ID |
| DELETE | `/emails/<id>` | Delete a processed email |

### Smart Reply

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/emails/reply` | Generate a context-aware reply draft |

### Analytics

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/dashboard/stats` | Retrieve email analytics and dashboard statistics |

### Search, Filtering & Pagination

The `GET /emails` endpoint supports flexible retrieval of processed emails using query parameters.

| Feature | Example |
|---------|---------|
| Pagination | `/emails?page=1&limit=10` |
| Category Filter | `/emails?category=Urgent` |
| Sender Search | `/emails?sender=microsoft` |
| Minimum Priority | `/emails?min_priority=70` |

These query parameters can also be combined.

Example:

GET /emails?category=Action%20Needed&min_priority=70&page=1&limit=10

## Technology Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy

**Database**
- SQLite

**NLP & AI**
- spaCy (`en_core_web_sm`) — named entity recognition
- scikit-learn — TF-IDF vectorization for summarization and keyword extraction
- python-dateutil — fuzzy date parsing
- Rule-based classification and priority engine

**Data Validation**
- Pydantic

## Project Structure

```
email_ai_platform/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask app and API routes
│   ├── ai_engine.py          # Categorization, priority, extraction, summarization, NER
│   ├── reply_generator.py    # Template-based reply drafting
│   ├── models.py             # Flask-SQLAlchemy database models
│   ├── schemas.py             # Pydantic request/response schemas
│   └── database.py           # Database configuration and initialization
├── sample_data/
│   └── sample_emails.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation & Setup

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
python -m spacy download en_core_web_sm
```

The spaCy language model is a separate download from the `spacy` package and is required before named entity recognition will work.

## Running the Application

```bash
python -m app.main
```

The API runs at `http://127.0.0.1:5000`.

## Future Improvements

Possible enhancements:
- React dashboard interface
- Gmail and Outlook integration
- PostgreSQL migration
- User authentication
- Advanced machine learning classifier
- Email attachment processing
- Production deployment
- Advanced AI assistant integration

## Project Highlights

This project demonstrates practical implementation of:
- REST API Development
- Backend System Design
- Natural Language Processing
- Text Classification
- Information Extraction
- Automated Summarization
- Email Intelligence Automation
- Analytics & Data Processing

## Author

Developed as an AI/NLP-based backend project demonstrating intelligent email automation and backend engineering capabilities.
