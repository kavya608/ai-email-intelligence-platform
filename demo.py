"""
AI Email Intelligence Platform - Standalone Demo

Runs the email intelligence engine directly on sample emails
without requiring the Flask server or database.

Usage:
    python demo.py
"""

import json
from app.ai_engine import process_email


def main():
    with open("sample_data/sample_emails.json", "r", encoding="utf-8") as f:
        emails = json.load(f)

    print("=" * 80)
    print("AI EMAIL INTELLIGENCE PLATFORM - DEMO")
    print("=" * 80)

    for i, email in enumerate(emails, start=1):
        result = process_email(
            email["sender"],
            email["subject"],
            email["body"]
        )

        print(f"\n{'=' * 80}")
        print(f"Email #{i}")
        print("=" * 80)

        print(f"From            : {result['sender']}")
        print(f"Subject         : {result['subject']}")
        print(f"Category        : {result['category']}")
        print(f"Priority Score  : {result['priority_score']}/100")
        print(f"Summary         : {result['summary']}")

        if result["keywords"]:
            print(f"Keywords        : {result['keywords']}")

        if result["action_items"]:
            print(f"Action Items    : {result['action_items']}")

        if result["deadline"]:
            print(f"Deadline        : {result['deadline']}")

        print("\nExtracted Entities:")
        entities = result["entities"]

        for entity_type, values in entities.items():
            if values:
                print(f"  {entity_type.title():15}: {', '.join(values)}")

    print("\n" + "=" * 80)
    print("Demo completed successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()