from dataclasses import dataclass, field
import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pyrate_limiter import Duration, Rate, Limiter, InMemoryBucket, LimiterDelayException
from typing import Optional

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

    params = {
        "dateAfter": start_time.isoformat(),
        "dateBefore": end_time.isoformat(),
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
        all_games.extend(data['games'])

        more_pages = data.get('has_more', False)
        
        # Increment the offset to get the next set of data
        if more_pages:
            params["offset"] += config.max_limit

    return all_games

# Function to get games from the last hour
def get_last_hour_games():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    games = fetch_games(start_time, end_time)
    print(f"Retrieved {len(games)} games from the last hour.")
    return games

# Call on startup
if __name__ == "__main__":
    get_last_hour_games()