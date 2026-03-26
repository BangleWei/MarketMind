import websocket
import json

SOCKET_URL = "wss://api.gemini.com/v1/marketdata/GEMI-FEDJAN26-DN25"

def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "update":
        for event in data.get("events", []):
            if event.get("type") == "trade":
                price = event.get("price")
                amount = event.get("amount")
                side = event.get("makerSide")
                print(f"🚨 LIVE TRADE: {amount} shares traded at ${price} (Maker was {side})")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket Closed ###")

def on_open(ws):
    print("🌐 Connected to Gemini WebSocket Firehose!")
    print("Waiting for live trades on GEMI-FEDJAN26-DN25... (Press Ctrl+C to stop)")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(SOCKET_URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()