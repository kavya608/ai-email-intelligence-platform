# 📧 AI Email Intelligence Platform

An AI-powered full-stack email intelligence platform that transforms raw emails into structured insights.

The system automatically:
- Classifies email intent
- Calculates priority scores
- Generates summaries
- Extracts named entities
- Identifies action items and deadlines
- Generates context-aware reply suggestions
- Provides analytics through an interactive dashboard

Built with a **React + Flask** full-stack architecture and a classical **NLP pipeline** (spaCy, scikit-learn, TF-IDF, rule-based intent detection) rather than an LLM. See [Why Classical NLP Instead of an LLM?](#-why-classical-nlp-instead-of-an-llm) for the reasoning.

---

## Table of Contents

- [Live Demo](#-live-demo)
- [Project Status](#-project-status)
- [Features](#-features)
- [System Architecture](#️-architecture)
- [Database Design](#️-database-design)
- [Tech Stack](#-tech-stack)
- [Why Classical NLP Instead of an LLM?](#-why-classical-nlp-instead-of-an-llm)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Deployment](#-deployment)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-endpoints)
- [Screenshots](#-screenshots)
- [Engineering Highlights](#-engineering-highlights)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## 🌐 Live Demo

**Frontend:** [https://ai-email-intelligence-platform.vercel.app](https://ai-email-intelligence-platform.vercel.app/)

**Backend API:** [https://ai-email-intelligence-platform.onrender.com](https://ai-email-intelligence-platform.onrender.com/emails)

**Repository:** [https://github.com/kavya608/ai-email-intelligence-platform](https://github.com/kavya608/ai-email-intelligence-platform)

> Note: the Render free tier spins down after inactivity, so the first request after idling may take up to a minute to respond.

---

## 📌 Project Status

🚀 Deployed — Backend on Render, Frontend on Vercel

**Implemented:**
- Backend REST APIs
- NLP processing pipeline (classification, priority, summary, entities)
- React dashboard
- Email analytics
- Full-stack deployment (Render + Vercel)

**Planned:**
- Gmail/Outlook integration
- LLM-based enhancement
- Authentication and user accounts

---

## ✨ Features

### Backend
✅ Email ingestion API
✅ Batch email processing
✅ NLP-based classification
✅ Priority scoring
✅ Spam detection
✅ Email summarization (TF-IDF)
✅ Named entity extraction (people, orgs, locations, dates, money)
✅ Action item & deadline detection
✅ Reply generation API
✅ Dashboard statistics API

### Frontend
✅ React dashboard
✅ Email listing interface
✅ Search and filtering
✅ Sorting and pagination
✅ Email details view
✅ Analytics cards & charts
✅ Responsive UI

---

## 🏗️ Architecture

```
React Frontend (Vercel)
      │
      │  Axios REST API
      ▼
Flask Backend API (Render)
      │
      ▼
AI Processing Engine
      │
      ├─────────────┬─────────────┬─────────────┐
      ▼             ▼             ▼             ▼
  Intent        Priority      Summary        Entity
Classification   Scoring     Generation    Extraction
      │             │             │             │
      └─────────────┴─────────────┴─────────────┘
                          │
                          ▼
                   SQLite Database
```

---

## 🔄 Email Processing Workflow

1. User submits an email
2. Flask API receives the request
3. NLP pipeline processes the content:
   - Intent classification
   - Priority calculation
   - Summary generation
   - Entity extraction
   - Action detection
4. Results are stored in SQLite
5. React dashboard displays insights

---

## 🗄️ Database Design

Processed email intelligence is stored using SQLAlchemy ORM. Each email record includes:

- Sender information
- Subject and content
- Category
- Priority score
- NLP-generated summary
- Extracted entities
- Action items
- Deadlines
- Spam classification

---

## 🛠 Tech Stack

### Frontend
- React
- Vite
- React Router
- Axios
- Recharts
- Lucide React
- CSS

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Pydantic

### AI / NLP
- spaCy
- Scikit-learn
- TF-IDF based summarization
- Rule-based classification engine

### Database
- SQLite

### Deployment
- Render (Backend)
- Vercel (Frontend)

---

## 🧠 Why Classical NLP Instead of an LLM?

The first version of this platform uses classical NLP techniques (spaCy, scikit-learn, TF-IDF, rule-based logic) instead of an external LLM API.

Reasons:
- Zero API dependency
- Faster inference
- Deterministic, reproducible results
- No usage cost
- Easier debugging and testing

The architecture is designed so an LLM-based understanding layer can be added later without a rewrite (see [Future Improvements](#-future-improvements)).

---

## 📁 Project Structure

```
AI_Email_Intelligence_Platform/
│
├── Backend/
│   ├── app/
│   │   ├── ai_engine.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── instance/
│   │   └── email_intelligence.db
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   └── StatCard.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Emails.jsx
│   │   │   ├── EmailDetails.jsx
│   │   │   └── Analytics.jsx
│   │   ├── routes/
│   │   │   └── routes.jsx
│   │   ├── styles/
│   │   │   ├── Dashboard.css
│   │   │   ├── Emails.css
│   │   │   ├── EmailDetails.css
│   │   │   ├── Analytics.css
│   │   │   └── SideBar.css
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── screenshots/
│
└── README.md
```

---

## ⚙️ Installation & Setup

Run the project locally for development:

### 1. Clone the Repository

```bash
git clone https://github.com/kavya608/ai-email-intelligence-platform.git
cd ai-email-intelligence-platform
```

### 2. Backend Setup

Navigate to the backend directory:
```bash
cd Backend
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the environment (Windows):
```bash
venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the Flask server:
```bash
python -m app.main
```

Backend runs on:
```
http://127.0.0.1:5000
```

### 3. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
```

Install packages:
```bash
npm install
```

Start the React application:
```bash
npm run dev
```

Frontend runs on:
```
http://localhost:5173
```

---

## 🚀 Deployment

The live version of this project is deployed as follows:

### Backend — Render

```bash
cd Backend
pip install -r requirements.txt
python -m app.main
```

- Hosted as a Web Service on [Render](https://render.com)
- Uses the `requirements.txt` for build and `python -m app.main` (or a configured start command) to run
- Note: free-tier Render services spin down when idle and cold-start on the next request

### Frontend — Vercel

```bash
cd frontend
npm install
npm run build
```

- Hosted on [Vercel](https://vercel.com)
- Framework preset: Vite
- The frontend's Axios base URL is configured to point at the deployed Render backend API

---

## 🔐 Environment Variables

The project currently runs on SQLite by default (`instance/email_intelligence.db`).

Optional `.env` configuration inside `Backend/`:

```
DATABASE_URL=sqlite:///instance/email_intelligence.db
```

For the deployed frontend, configure the backend API base URL (e.g. in `frontend/.env`):

```
VITE_API_BASE_URL=https://ai-email-intelligence-platform.onrender.com
```

*(the `/emails` path shown in the Live Demo link above is one specific endpoint — the frontend should point at the base URL without the path)*

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/emails/ingest` | Process and store a single email |
| POST | `/emails/batch-ingest` | Process multiple emails together |
| GET | `/emails/` | Fetch emails (pagination, search, filtering, sorting) |
| GET | `/emails/<id>` | Fetch complete email intelligence for one email |
| DELETE | `/emails/<id>` | Delete an email |
| POST | `/emails/reply` | Generate a context-aware reply suggestion |
| GET | `/dashboard/stats` | Fetch dashboard analytics and statistics |

### Get Emails
```
GET /emails/?page=1&limit=10
```
Supports pagination, search, filtering, and sorting.

### Get Email Details
```
GET /emails/<id>
```
Returns complete email intelligence: category, priority, summary, entities, and action items.

**Example Response:**
```json
{
  "category": "Work",
  "priority": 8,
  "summary": "Meeting scheduled for project discussion",
  "entities": {
    "people": ["John"],
    "organizations": ["Google"]
  },
  "action_items": ["Confirm attendance", "Prepare project update"]
}
```

---

## 📸 Screenshots

| Dashboard | Emails |
|---|---|
| ![Dashboard](screenshots/dashboard.png) | ![Emails](screenshots/emails-list.png) |

| Email Details |
|---|
| ![Email Details](screenshots/email.png) |

**Analytics**

| ![Analytics 1](screenshots/analytics-1.png) | ![Analytics 2](screenshots/analytics-2.png) | ![Analytics 3](screenshots/analytics-3.png) |
|---|---|---|

---

## 🧩 Engineering Highlights

- Designed and deployed REST APIs using Flask, hosted on Render
- Implemented a modular AI processing pipeline (classification, priority scoring, summarization, entity extraction)
- Used SQLAlchemy ORM for database management
- Integrated the React frontend with the Flask backend via Axios, deployed on Vercel
- Implemented pagination and filtering for scalable email retrieval
- Built analytics endpoints for dashboard visualization
- Built reusable React components, routing structure, and API-driven frontend workflows using Axios

## 🌍 Future Improvements

- 🤖 LLM-based email understanding
- 📧 Gmail API integration
- 📬 Outlook integration
- 🔔 Smart notifications
- 🧠 Advanced AI reply generation
- 🔐 User authentication
- 📱 Mobile application

---

## 👩‍💻 Author

**G M Kavya**
Frontend Developer | Full Stack Developer

GitHub: [github.com/kavya608](https://github.com/kavya608)

---

⭐ If you find this project useful, consider giving it a star!
