from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate
import os

# Define the base directory (where games.db goes)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the Flask app
app = Flask(__name__)

# Configure the SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'games.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)  # Add this line

# Association table for many-to-many relationship between Game and Player
match_players = db.Table(
    'match_players',
    db.Column('match_id', db.String, db.ForeignKey('game.match_id'), primary_key=True),
    db.Column('player_id', db.String, db.ForeignKey('player.player_id'), primary_key=True)
)

# Define a table to store games
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String, unique=True, nullable=False)
    date = db.Column(db.String, nullable=False)
    queue_type = db.Column(db.String, nullable=False)
    player_count = db.Column(db.Integer, nullable=False)
    human_count = db.Column(db.Integer, nullable=False)
    game_length = db.Column(db.Integer, nullable=False)

    # Many-to-Many Relationship
    players = db.relationship('Player', secondary=match_players, backref='matches')

    def __repr__(self):
        return f"<Game {self.match_id}>"

# Define a table to store players
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String, unique=True, nullable=False)
    player_name = db.Column(db.String, nullable=False)
    player_slot = db.Column(db.Integer, nullable=False)
    legion = db.Column(db.String, nullable=False)
    game_result = db.Column(db.String, nullable=False)
    overall_elo = db.Column(db.Float, nullable=False)
    classic_elo = db.Column(db.Float, nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    eco = db.Column(db.Float, nullable=False)
    legion_elo = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Player {self.player_id}>"

# Route to check the app is working
@app.route('/healthz')
def healthz():
    return 'Healthy', 200

if __name__ == '__main__':
    app.run(debug=True)
