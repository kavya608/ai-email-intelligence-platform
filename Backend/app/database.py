import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

    DB_PATH = os.path.join(
        BASE_DIR,
        "instance",
        "email_intelligence.db"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{DB_PATH}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return db