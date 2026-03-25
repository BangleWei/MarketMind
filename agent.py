from groq import Groq
from dotenv import load_dotenv
from market_data import get_ethical_markets
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("📡 Fetching live market data...")
markets = get_ethical_markets()

market_summary = ""
for market in markets:
    market_summary += f"\nMarket: {market['title']} (Category: {market['category']})\n"
    for contract in market["contracts"]:
        price = contract["prices"].get("buy", {}).get("yes", "N/A")
        if price != "N/A":
            probability = round(float(price) * 100)
            market_summary += f"  - {contract['label']}: {probability}% chance YES\n"

SYSTEM_PROMPT = f"""You are MarketMind, an AI analyst specializing in prediction markets.
    You have access to live ethical market data (Crypto, Commodities, Tech only - no Sports).
    Use this data to answer user questions accurately and explain probabilities in plain English.

    When making recommendations, use this framework:
    - Probability > 70% → Strong YES signal
    - Probability 50-70% → Moderate YES signal
    - Probability 30-50% → Uncertain, high risk
    - Probability < 30% → Strong NO signal

    Always explain your reasoning in plain English. 
    
    CRITICAL: If you find a "Strong YES" or "Strong NO" signal and recommend taking action, you MUST include this exact tag at the very end of your response:
    [EXECUTE_TRADE: Exact Name of the Market]

    LIVE MARKET DATA:
    {market_summary}
    """

conversation_history = []

print("🧠 MarketMind ready! Ask me anything about prediction markets.")
print("   Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
    )

    assistant_message = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    print(f"\nMarketMind: {assistant_message}\n")
