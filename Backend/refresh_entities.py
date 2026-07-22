from app.main import app
from app.models import db, Email
from app.ai_engine import extract_named_entities

with app.app_context():

    emails = Email.query.all()

    print(f"Found {len(emails)} emails")

    for email in emails:

        text = (email.subject or "") + " " + (email.body or "")

        email.entities = extract_named_entities(text)

    db.session.commit()

    print("✅ All entities refreshed successfully!")