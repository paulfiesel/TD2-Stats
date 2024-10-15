import os
import requests
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pyrate_limiter import Duration, Rate, Limiter, InMemoryBucket

# Load environment variables from the .env file
load_dotenv()

# API details
API_URL = "https://apiv2.legiontd2.com/games"
API_KEY = os.getenv("API_KEY")
MAX_LIMIT = 50  # Adjusted based on the API's maximum limit of 50

# Set up rate limiting
rate = Rate(5, Duration.SECOND)
burst_rate = Rate(100, Duration.MINUTE)
limiter = Limiter(InMemoryBucket([rate]))
burst_limiter = Limiter(InMemoryBucket([burst_rate]))

# Function to call the API and fetch games
def fetch_games(start_time, end_time):
    headers = {
        "x-api-key": API_KEY
    }

    params = {
        "dateAfter": start_time.isoformat(),
        "dateBefore": end_time.isoformat(),
        "limit": MAX_LIMIT  # Use the corrected limit of 50
    }

    all_games = []
    more_pages = True

    while more_pages:
        limiter.try_acquire("api_call")
        burst_limiter.try_acquire("burst_api_call")

        # Make the API call
        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()

        all_games.extend(data['games'])

        more_pages = data.get('has_more', False)

        # Respect API rate limits with a delay
        time.sleep(1)

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
