from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Create SQLAlchemy object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configure the SQLite database path
    instance_path = os.path.expanduser('~/td2stats_instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(instance_path, 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app instance
    db.init_app(app)

    @app.route('/healthz')
    def healthz():
        return '', 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
