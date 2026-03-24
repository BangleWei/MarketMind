import requests

ALLOWED_CATEGORIES = ["Crypto", "Commodities", "Tech"]
API_URL = "https://api.gemini.com/v1/prediction-markets/events"

def fetch_markets():
    response = requests.get(API_URL)
    data = response.json()
    events = data["data"]
    return events

def filter_markets(events):
    filtered = []
    for event in events:
        if event["category"] in ALLOWED_CATEGORIES:
            filtered.append(event)
    return filtered
def get_ethical_markets():
    events = fetch_markets()
    filtered = filter_markets(events)
    return filtered
def display_markets(events):
    for event in events:
        print(f"\n📊 {event['title']}")
        print(f"   Category: {event['category']}")
        
        for contract in event["contracts"]:
            price = contract["prices"].get("buy", {}).get("yes", "N/A")
            if price != "N/A":
                probability = round(float(price) * 100)
                print(f"   {contract['label']} → {probability}% chance YES")
if __name__ == "__main__":
    print("🔍 Fetching ethical prediction markets...\n")
    events = fetch_markets()
    filtered = filter_markets(events)
    print(f"Found {len(filtered)} ethical markets out of {len(events)} total\n")
    display_markets(filtered)
