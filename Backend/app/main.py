from sqlalchemy import or_
from flask import Flask, request, jsonify
from pydantic import ValidationError
from collections import Counter
from flask_cors import CORS

from .database import init_db, db
from app.models import db, Email
from app.reply_generator import generate_reply

from app.schemas import (
    EmailIngestRequest,
    EmailResponse,
    EmailReplyRequest,
    EmailReplyResponse,
)

from app.ai_engine import (
    categorize_email,
    calculate_priority,
    extract_action_items,
    extract_deadline,
    summarize_email,
    extract_keywords,
    extract_named_entities
    
)

import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

app = Flask(
    __name__,
    instance_path=os.path.join(BASE_DIR, "instance"),
    instance_relative_config=True
)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["DEBUG"] = True

init_db(app)
import os

print("Instance Path:", app.instance_path)
print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
CORS(app)
with app.app_context():
    db.create_all()
    from app.seed import seed_database
    seed_database()
def process_email(sender, subject, body):
    category = categorize_email(subject, body)
    deadline = extract_deadline((subject or '') + ' ' + body)
    has_deadline = deadline is not None
    priority_score = calculate_priority(category, (subject or '') + ' ' + body, has_deadline)
    action_items = extract_action_items(body)
    summary = summarize_email(body)
    keywords = extract_keywords(body)
    entities = extract_named_entities((subject or "") + " " + body)

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
        'entities': entities,
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

@app.route('/emails/reply', methods=['POST'])
def generate_email_reply():
    raw_data = request.get_json(silent=True)

    if raw_data is None:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    try:
        validated = EmailReplyRequest(**raw_data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400

    category = categorize_email(validated.subject, validated.body)

    deadline = extract_deadline(
        (validated.subject or "") + " " + validated.body
    )

    action_items = extract_action_items(validated.body)

    reply = generate_reply(
        validated.subject,
        validated.body,
        category,
        deadline,
        action_items,
        validated.tone
    )

    response = EmailReplyResponse(reply=reply)

    return jsonify(response.model_dump()), 200

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

def get_entity_statistics():

    people_counter = Counter()
    organization_counter = Counter()
    location_counter = Counter()

    emails = Email.query.all()

    for email in emails:

        if not email.entities:
            continue

        for person in email.entities.get("people", []):
            people_counter[person] += 1

        for org in email.entities.get("organizations", []):
            organization_counter[org] += 1

        for location in email.entities.get("locations", []):
            location_counter[location] += 1

    return {
        "top_people": people_counter.most_common(5),
        "top_organizations": organization_counter.most_common(5),
        "top_locations": location_counter.most_common(5),
    }
@app.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    try:
        total_emails = Email.query.count()

        category_counts = {}
        results = db.session.query(
            Email.category,
            db.func.count(Email.id)
        ).group_by(Email.category).all()

        for category, count in results:
            category_counts[category] = count

        avg_priority = db.session.query(
            db.func.avg(Email.priority_score)
        ).scalar()

        avg_priority = round(avg_priority, 1) if avg_priority is not None else None

        upcoming = (
            Email.query
            .filter(Email.deadline.isnot(None))
            .order_by(Email.deadline.asc())
            .limit(5)
            .all()
        )

        upcoming_list = [
            {
                'id': e.id,
                'subject': e.subject,
                'deadline': e.deadline.isoformat()
            }
            for e in upcoming
        ]

        entity_stats = get_entity_statistics()

        urgent_emails = Email.query.filter(
            Email.category == 'Urgent'
        ).count()

        action_needed_emails = Email.query.filter(
            Email.category == 'Action Needed'
        ).count()

        spam_emails = Email.query.filter(
            Email.category == 'Spam-like'
        ).count()

        spam_percentage = (
            round((spam_emails / total_emails) * 100, 1)
            if total_emails > 0 else 0
        )

        top_sender_results = (
            db.session.query(
                Email.sender,
                db.func.count(Email.id)
            )
            .group_by(Email.sender)
            .order_by(db.func.count(Email.id).desc())
            .limit(5)
            .all()
        )

        top_senders = [
            {
                "sender": sender,
                "count": count
            }
            for sender, count in top_sender_results
        ]

        priority_distribution = {
            "0-20": Email.query.filter(Email.priority_score.between(0, 20)).count(),
            "21-40": Email.query.filter(Email.priority_score.between(21, 40)).count(),
            "41-60": Email.query.filter(Email.priority_score.between(41, 60)).count(),
            "61-80": Email.query.filter(Email.priority_score.between(61, 80)).count(),
            "81-100": Email.query.filter(Email.priority_score.between(81, 100)).count()
        }

        return jsonify({
            'total_emails': total_emails,
            'category_breakdown': category_counts,
            'average_priority': avg_priority,
            'upcoming_deadlines': upcoming_list,
            'urgent_emails': urgent_emails,
            'action_needed_emails': action_needed_emails,
            'spam_percentage': spam_percentage,
            'top_senders': top_senders,
            'priority_distribution': priority_distribution,
            **entity_stats
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/emails/<int:email_id>', methods=['GET'])
def get_email(email_id):
    email = Email.query.get(email_id)

    if not email:
        return jsonify({
            "error": "Email not found"
        }), 404

    return jsonify({
        "id": email.id,
        "sender": email.sender,
        "subject": email.subject,
        "body": email.body,
        "category": email.category,
        "priority_score": email.priority_score,
        "summary": email.summary,
        "action_items": email.action_items,
        "entities": email.entities
    }), 200

@app.route('/emails', methods=['GET'])
def get_all_emails():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        query = Email.query

        category = request.args.get('category')
        if category:
            query = query.filter(Email.category == category)

        min_priority = request.args.get('min_priority', type=int)
        if min_priority:
            query = query.filter(Email.priority_score >= min_priority)

        search = request.args.get("search")
        if search:
            query = query.filter(
                or_(
                    Email.subject.ilike(f"%{search}%"),
                    Email.sender.ilike(f"%{search}%"),
                    Email.summary.ilike(f"%{search}%"),
                    Email.category.ilike(f"%{search}%")
                )
            )

        sort = request.args.get("sort")

        if sort == "priority-high":
            query = query.order_by(Email.priority_score.desc())
        elif sort == "priority-low":
            query = query.order_by(Email.priority_score.asc())
        elif sort == "subject-asc":
            query = query.order_by(Email.subject.asc())
        elif sort == "subject-desc":
            query = query.order_by(Email.subject.desc())
        else:
            query = query.order_by(Email.id.desc())

        total_emails = query.count()

        emails = query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )

        email_list = []

        for email in emails.items:
            email_list.append({
                "id": email.id,
                "sender": email.sender,
                "subject": email.subject,
                "category": email.category,
                "priority_score": email.priority_score,
                "summary": email.summary
            })

        return jsonify({
            "page": page,
            "limit": limit,
            "total": total_emails,
            "emails": email_list
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500
    
@app.route('/emails/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    email = Email.query.get(email_id)

    if not email:
        return jsonify({
            "error": "Email not found"
        }), 404

    db.session.delete(email)
    db.session.commit()

    return jsonify({
        "message": "Email deleted successfully",
        "deleted_id": email_id
    }), 200

if __name__ == '__main__':
    app.run(debug=True)