import json
import os

from app.models import Email
from app.email_processor import process_email
from app.database import db


def seed_database():
    if Email.query.count() > 0:
        print("Database already contains data.")
        return

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sample_file = os.path.join(base_dir, "sample_data", "sample_emails.json")

    with open(sample_file, "r", encoding="utf-8") as f:
        emails = json.load(f)

    for email in emails:
        processed = process_email(
            email["sender"],
            email["subject"],
            email["body"]
        )

        db.session.add(Email(**processed))

    db.session.commit()

    print(f"Inserted {len(emails)} sample emails.")