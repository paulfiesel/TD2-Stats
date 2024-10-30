from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime

# Define Game model
class Game(db.Model):
    __tablename__ = 'game'

    # Define all columns as per acceptance criteria
    match_id = db.Column(db.String, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    queue_type = db.Column(db.String, nullable=False)
    player_count = db.Column(db.Integer, nullable=False)
    human_count = db.Column(db.Integer, nullable=False)
    game_length = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Game {self.match_id}>"
