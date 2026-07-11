"""
Quick standalone demo — runs the AI intelligence engine directly on the
sample emails and prints the results. No server, no database needed.

Run with:
    python demo.py
"""
import json
from app.ai_engine import process_email


def main():
    with open("sample_data/sample_emails.json") as f:
        emails = json.load(f)

    for i, email in enumerate(emails, 1):
        result = process_email(email["sender"], email["subject"], email["body"])
        print(f"\n{'='*70}")
        print(f"Email #{i}: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"{'-'*70}")
        print(f"Category:        {result['category']}")
        print(f"Priority Score:  {result['priority_score']}/100")
        print(f"Summary:         {result['summary']}")
        print(f"Keywords:        {', '.join(result['keywords'])}")
        if result["action_items"]:
            print("Action Items:")
            for item in result["action_items"]:
                print(f"   - {item}")
        if result["deadlines"]:
            print("Deadlines:")
            for d in result["deadlines"]:
                print(f"   - {d['text']}  (resolved: {d['date']})")


if __name__ == "__main__":
    main()
