from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Email(db.Model):
    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500))
    body = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(50))
    priority_score = db.Column(db.Integer)
    summary = db.Column(db.Text)
    action_items = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=True)
    keywords = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'subject': self.subject,
            'body': self.body,
            'category': self.category,
            'priority_score': self.priority_score,
            'summary': self.summary,
            'action_items': self.action_items,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat()
        }