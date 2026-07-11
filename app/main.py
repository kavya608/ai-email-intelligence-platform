from flask import Flask, request, jsonify
from pydantic import ValidationError

from app.database import init_db
from app.models import db, Email
from app.schemas import EmailIngestRequest, EmailResponse
from app.ai_engine import (
    categorize_email,
    calculate_priority,
    extract_action_items,
    extract_deadline,
    summarize_email,
    extract_keywords,
    enhance_categorization,
    enhance_summary,
    is_llm_enabled,
)

app = Flask(__name__)
init_db(app)
def process_email(sender, subject, body):
    category = categorize_email(subject, body)
    deadline = extract_deadline((subject or '') + ' ' + body)
    has_deadline = deadline is not None
    priority_score = calculate_priority(category, (subject or '') + ' ' + body, has_deadline)
    action_items = extract_action_items(body)
    summary = summarize_email(body)
    keywords = extract_keywords(body)

    return {
        'sender': sender,
        'subject': subject,
        'body': body,
        'category': category,
        'priority_score': priority_score,
        'deadline': deadline,
        'action_items': '; '.join(action_items) if action_items else None,
        'summary': summary,
        'keywords': ', '.join(keywords) if keywords else None,
    }

@app.route('/emails/ingest', methods=['POST'])
def ingest_email():
    raw_data = request.get_json(silent=True)
    if raw_data is None:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    try:
        validated = EmailIngestRequest(**raw_data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    processed = process_email(validated.sender, validated.subject, validated.body)
    email = Email(**processed)
    db.session.add(email)
    db.session.commit()

    response = EmailResponse.model_validate(email)
    return jsonify(response.model_dump(mode='json')), 201
@app.route('/emails/batch-ingest', methods=['POST'])
def batch_ingest_emails():
    raw_data = request.get_json(silent=True)
    if raw_data is None or not isinstance(raw_data, list):
        return jsonify({'error': 'Request body must be a JSON array of emails'}), 400

    created = []
    errors = []

    for index, item in enumerate(raw_data):
        try:
            validated = EmailIngestRequest(**item)
        except ValidationError as e:
            errors.append({'index': index, 'error': e.errors()})
            continue

        processed = process_email(validated.sender, validated.subject, validated.body)
        email = Email(**processed)
        db.session.add(email)
        created.append(email)

    db.session.commit()

    response = [EmailResponse.model_validate(e).model_dump(mode='json') for e in created]
    return jsonify({'created': response, 'errors': errors}), 201
@app.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    total_emails = Email.query.count()

    category_counts = {}
    results = db.session.query(Email.category, db.func.count(Email.id)).group_by(Email.category).all()
    for category, count in results:
        category_counts[category] = count

    avg_priority = db.session.query(db.func.avg(Email.priority_score)).scalar()
    avg_priority = round(avg_priority, 1) if avg_priority is not None else None

    upcoming = (
        Email.query
        .filter(Email.deadline.isnot(None))
        .order_by(Email.deadline.asc())
        .limit(5)
        .all()
    )
    upcoming_list = [
        {'id': e.id, 'subject': e.subject, 'deadline': e.deadline.isoformat()}
        for e in upcoming
    ]

    return jsonify({
        'total_emails': total_emails,
        'category_breakdown': category_counts,
        'average_priority': avg_priority,
        'upcoming_deadlines': upcoming_list,
    }), 200
if __name__ == '__main__':
    app.run(debug=True)