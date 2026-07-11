"""
AI Email Intelligence Platform — Flask application.

Run with:
    python app/main.py
    (or: flask --app app.main run --debug)

Then the API is available at http://127.0.0.1:5000
"""
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from pydantic import ValidationError
from sqlalchemy import func

from app.database import Base, engine, SessionLocal
from app import models, schemas
from app.ai_engine import process_email

# Create tables on startup (fine for SQLite/dev; use Alembic migrations in prod)
Base.metadata.create_all(bind=engine)

app = Flask(__name__)


def get_db():
    """Return a new DB session. Caller is responsible for closing it."""
    return SessionLocal()


def email_to_dict(email: models.Email) -> dict:
    """Serialize a SQLAlchemy Email row using the Pydantic output schema."""
    return schemas.EmailOut.model_validate(email).model_dump(mode="json")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return jsonify({"status": "ok", "service": "AI Email Intelligence Platform"})


# ---------------------------------------------------------------------------
# Ingest a single email
# ---------------------------------------------------------------------------
@app.post("/emails/ingest")
def ingest_email():
    db = get_db()
    try:
        try:
            payload = schemas.EmailIngest(**(request.get_json(force=True) or {}))
        except ValidationError as e:
            return jsonify({"error": "validation_error", "details": e.errors()}), 422

        intelligence = process_email(payload.sender, payload.subject, payload.body)

        db_email = models.Email(
            sender=payload.sender,
            subject=payload.subject,
            body=payload.body,
            received_at=payload.received_at or datetime.utcnow(),
            category=intelligence["category"],
            priority_score=intelligence["priority_score"],
            summary=intelligence["summary"],
            action_items=intelligence["action_items"],
            deadlines=intelligence["deadlines"],
            keywords=intelligence["keywords"],
            processed_at=datetime.utcnow(),
        )
        db.add(db_email)
        db.commit()
        db.refresh(db_email)
        return jsonify(email_to_dict(db_email)), 201
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Ingest multiple emails at once (e.g. sample/demo data)
# ---------------------------------------------------------------------------
@app.post("/emails/batch-ingest")
def batch_ingest():
    db = get_db()
    try:
        raw_list = request.get_json(force=True) or []
        if not isinstance(raw_list, list):
            return jsonify({"error": "expected a JSON array of emails"}), 422

        results = []
        for raw in raw_list:
            try:
                payload = schemas.EmailIngest(**raw)
            except ValidationError as e:
                return jsonify({"error": "validation_error", "details": e.errors()}), 422

            intelligence = process_email(payload.sender, payload.subject, payload.body)
            db_email = models.Email(
                sender=payload.sender,
                subject=payload.subject,
                body=payload.body,
                received_at=payload.received_at or datetime.utcnow(),
                category=intelligence["category"],
                priority_score=intelligence["priority_score"],
                summary=intelligence["summary"],
                action_items=intelligence["action_items"],
                deadlines=intelligence["deadlines"],
                keywords=intelligence["keywords"],
                processed_at=datetime.utcnow(),
            )
            db.add(db_email)
            results.append(db_email)

        db.commit()
        for r in results:
            db.refresh(r)

        return jsonify([email_to_dict(r) for r in results]), 201
    finally:
        db.close()


# ---------------------------------------------------------------------------
# List emails, with optional filters
# ---------------------------------------------------------------------------
@app.get("/emails/")
def list_emails():
    db = get_db()
    try:
        category = request.args.get("category")
        min_priority = request.args.get("min_priority", type=float)
        limit = min(request.args.get("limit", default=50, type=int), 200)

        q = db.query(models.Email)
        if category:
            q = q.filter(models.Email.category == category)
        if min_priority is not None:
            q = q.filter(models.Email.priority_score >= min_priority)
        q = q.order_by(models.Email.priority_score.desc()).limit(limit)

        return jsonify([email_to_dict(e) for e in q.all()])
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Get a single email
# ---------------------------------------------------------------------------
@app.get("/emails/<int:email_id>")
def get_email(email_id):
    db = get_db()
    try:
        db_email = db.query(models.Email).filter(models.Email.id == email_id).first()
        if not db_email:
            return jsonify({"error": "Email not found"}), 404
        return jsonify(email_to_dict(db_email))
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Delete an email
# ---------------------------------------------------------------------------
@app.delete("/emails/<int:email_id>")
def delete_email(email_id):
    db = get_db()
    try:
        db_email = db.query(models.Email).filter(models.Email.id == email_id).first()
        if not db_email:
            return jsonify({"error": "Email not found"}), 404
        db.delete(db_email)
        db.commit()
        return jsonify({"status": "deleted", "id": email_id})
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------
@app.get("/dashboard/stats")
def dashboard_stats():
    db = get_db()
    try:
        total = db.query(models.Email).count()

        by_category_rows = (
            db.query(models.Email.category, func.count(models.Email.id))
            .group_by(models.Email.category)
            .all()
        )
        by_category = {cat: count for cat, count in by_category_rows}

        avg_priority = db.query(func.avg(models.Email.priority_score)).scalar() or 0.0
        high_priority_count = (
            db.query(models.Email).filter(models.Email.priority_score >= 70).count()
        )

        upcoming_cutoff = (datetime.utcnow() + timedelta(days=7)).date().isoformat()
        today = datetime.utcnow().date().isoformat()
        upcoming_deadlines = []
        for email in db.query(models.Email).filter(models.Email.deadlines.isnot(None)).all():
            for deadline in (email.deadlines or []):
                if deadline.get("date") and today <= deadline["date"] <= upcoming_cutoff:
                    upcoming_deadlines.append({
                        "email_id": email.id,
                        "subject": email.subject,
                        "deadline_text": deadline["text"],
                        "date": deadline["date"],
                    })

        stats = schemas.DashboardStats(
            total_emails=total,
            by_category=by_category,
            avg_priority_score=round(float(avg_priority), 2),
            high_priority_count=high_priority_count,
            upcoming_deadlines=upcoming_deadlines,
        )
        return jsonify(stats.model_dump(mode="json"))
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
