import requests
import json

# Configuration
API_URL = "http://localhost:8000/observations"

def fetch_all_observations():
    print("Fetching all observations...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        observations = response.json()
        print(f"Retrieved {len(observations)} observations.")
        print(json.dumps(observations, indent=2))
    except Exception as e:
        print(f"Error fetching observations: {e}")

def fetch_by_station(station_id):
    print(f"Fetching observations for station: {station_id}...")
    try:
        response = requests.get(API_URL, params={"station_id": station_id})
        response.raise_for_status()
        observations = response.json()
        print(f"Retrieved {len(observations)} observations for {station_id}.")
        print(json.dumps(observations, indent=2))
    except Exception as e:
        print(f"Error fetching observations: {e}")

if __name__ == "__main__":
    # Example usage
    fetch_all_observations()
    # fetch_by_station("STATION_001")
