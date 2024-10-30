from app import create_app, db
from models import Game

def init_db():
    app = create_app()

    with app.app_context():
        db.create_all()  # Create all tables defined in models.py
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
