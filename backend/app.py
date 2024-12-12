from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create the Flask app
app = Flask(__name__)

# Configure the SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a table to store games
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each row
    match_id = db.Column(db.String(50), unique=True, nullable=False)  # Game ID
    date = db.Column(db.String(50), nullable=False)  # Game date
    queue_type = db.Column(db.String(20), nullable=False)  # Game mode
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
        db.create_all()  # Recreate tables with the new schema
    app.run(debug=True)
