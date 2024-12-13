from dataclasses import dataclass, field
import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pyrate_limiter import Duration, Rate, Limiter, InMemoryBucket, LimiterDelayException
from typing import Optional
from app import db, Game, app

@dataclass
class APIConfig:
    api_url: str = "https://apiv2.legiontd2.com/games"
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("API_KEY"))
    max_limit: int = 50
    rate: Rate = Rate(5, Duration.SECOND)
    burst_rate: Rate = Rate(100, Duration.MINUTE)
    limiter: Limiter = field(init=False)
    burst_limiter: Limiter = field(init=False)

    def __post_init__(self):
        # Load environment variables here as part of the initialization
        load_dotenv()

        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY environment variable is not set")
        self.limiter = Limiter(InMemoryBucket([self.rate]), max_delay=200)
        self.burst_limiter = Limiter(InMemoryBucket([self.burst_rate]), max_delay=200)

# Instantiate the config
config = APIConfig()

# Function to call the API and fetch games
def fetch_games(start_time, end_time):
    headers = {
        "x-api-key": config.api_key
    }

    # Format the start and end times to match "YYYY-MM-DD HH:MM:SS"
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "dateAfter": start_time_str,
        "dateBefore": end_time_str,
        "limit": config.max_limit,  # Use the corrected limit of 50
        "offset": 0  # Start offset at 0 for the first call
    }

    all_games = []

    while True:
        try:
            config.limiter.try_acquire("api_call")
            config.burst_limiter.try_acquire("burst_api_call")
        except LimiterDelayException as e:
            print(f"Rate limit delay exceeded: {e}. Backing off.")
            continue

        response = requests.get(config.api_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()

        # If the response is a list, append the results
        if isinstance(data, list):
            all_games.extend(data)

            # Stop if fewer results than the limit are returned
            if len(data) < config.max_limit:
                break
        else:
            print("Unexpected response format.")
            break # Exit loop if data format is incorrect

        # Increment offset to fetch the next batch of results
        params["offset"] += config.max_limit

    return all_games

def save_games_to_db(games):
    for game in games:
        # Avoid duplicates by checking `_id` (match ID in the schema)
        existing_game = Game.query.filter_by(match_id=game["_id"]).first()
        if existing_game:
            continue

        # Create a new Game instance with correct fields from the schema
        new_game = Game(
            match_id=game["_id"],  # Unique match ID
            date=game["date"],  # Timestamp of the game
            queue_type=game["queueType"],  # Queue type (e.g., Classic)
            player_count=game["playerCount"],  # Total players
            human_count=game.get("humanCount", 0),  # Human players, default to 0 if missing
            game_length=game["gameLength"]  # Duration in seconds
        )

        db.session.add(new_game)  # Add to the session

        # Save players for the game
        save_players_to_db(game["players"], game["_id"])  # Assume `game["players"]` contains player data

    db.session.commit()  # Save to the database

def save_players_to_db(players, match_id):
    for player in players:
        # Check if the player already exists (prevent duplicates)
        existing_player = Player.query.filter_by(player_id=player["_id"], match_id=match_id).first()
        if existing_player:
            continue

        # Create a new Player instance
        new_player = Player(
            player_id=player["_id"],
            match_id=match_id,
            player_name=player.get("name", "Unknown"),  # Default to "Unknown" if name is missing
            player_slot=player["slot"],
            legion=player["legion"],
            game_result=player["result"],
            overall_elo=player["overallElo"],
            classic_elo=player["classicElo"],
            party_size=player["partySize"],
            eco=player["eco"],
            legion_elo=player["legionElo"]
        )

        db.session.add(new_player)  # Add to the session
    db.session.commit()  # Save to the database

# Function to get games from the last hour
def get_last_hour_games():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    games = fetch_games(start_time, end_time)

    # Wrap save_games_to_db in the application context
    with app.app_context():
        save_games_to_db(games)
        print(f"Saved {len(games)} games to the database.")
    return games

# Call on startup
if __name__ == "__main__":
    get_last_hour_games()