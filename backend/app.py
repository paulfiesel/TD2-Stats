from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

# Define a table to store games
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String, unique=True, nullable=False)  # Match ID
    date = db.Column(db.String, nullable=False)  # Date of the match
    queue_type = db.Column(db.String, nullable=False)  # Queue type
    player_count = db.Column(db.Integer, nullable=False)  # Total players
    human_count = db.Column(db.Integer, nullable=False)  # Human players
    game_length = db.Column(db.Integer, nullable=False)  # Duration in seconds

    def __repr__(self):
        return f"<Game {self.match_id}>"

# Route to check the app is working
@app.route('/healthz')
def healthz():
    return 'Healthy', 200

if __name__ == '__main__':
    # Create the database file and table structure
    with app.app_context():
        print("Initializing database and creating tables...")
        db.create_all()  # Recreate tables with the new schema
        print("Tables have been created.")
    app.run(debug=True)
