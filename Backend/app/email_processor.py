from app.ai_engine import (
    categorize_email,
    calculate_priority,
    extract_action_items,
    extract_deadline,
    summarize_email,
    extract_keywords,
    extract_named_entities
)


def process_email(sender, subject, body):
    category = categorize_email(subject, body)

    deadline = extract_deadline(
        (subject or "") + " " + body
    )

    has_deadline = deadline is not None

    priority_score = calculate_priority(
        category,
        (subject or "") + " " + body,
        has_deadline
    )

    action_items = extract_action_items(body)
    summary = summarize_email(body)
    keywords = extract_keywords(body)
    entities = extract_named_entities(
        (subject or "") + " " + body
    )

    return {
        "sender": sender,
        "subject": subject,
        "body": body,
        "category": category,
        "priority_score": priority_score,
        "deadline": deadline,
        "action_items": "; ".join(action_items) if action_items else None,
        "summary": summary,
        "keywords": ", ".join(keywords) if keywords else None,
        "entities": entities,
    }