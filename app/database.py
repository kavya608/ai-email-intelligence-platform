from app.models import db

DATABASE_URL = "sqlite:///email_intelligence.db"


def init_db(app):
    """Configure the Flask app with the database and create tables if needed."""
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()