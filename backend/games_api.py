from dataclasses import dataclass, field
import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pyrate_limiter import Duration, Rate, Limiter, InMemoryBucket, LimiterDelayException
from typing import Optional
from app import db, Game

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
    more_pages = True

    while more_pages:
        try:
            config.limiter.try_acquire("api_call")
            config.burst_limiter.try_acquire("burst_api_call")
        except LimiterDelayException as e:
            # If delay exceeds max_delay, print message and retry.
            print(f"Rate limit delay exceeded: {e}. Backing off.")
            continue

        # Make the API call
        response = requests.get(config.api_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()
        
        if isinstance(data, list):
            all_games.extend(data)
        else:
            print("Unexpected response format")
            break  # Exit loop if data format is incorrect

        more_pages = data.get('has_more', False)
        
        # Increment the offset to get the next set of data
        if more_pages:
            params["offset"] += config.max_limit

    return all_games

def save_games_to_db(games):
    for game in games:
        # Avoid duplicates by checking match_id
        existing_game = Game.query.filter_by(match_id=game["match_id"]).first()
        if existing_game:
            continue

        # Create a new Game instance
        new_game = Game(
            match_id=game["match_id"],
            date=game["date"],
            queue_type=game["queue_type"],
            player_count=game["player_count"],
            human_count=game["human_count"],
            game_length=game["game_length"]
        )

        db.session.add(new_game)  # Add to the session
    db.session.commit()  # Save to the database

# Function to get games from the last hour
def get_last_hour_games():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    games = fetch_games(start_time, end_time)
    save_games_to_db(games)
    print(f"Saved {len(games)} games to the database.")
    return games

# Call on startup
if __name__ == "__main__":
    get_last_hour_games()