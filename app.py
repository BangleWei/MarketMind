import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from market_data import get_ethical_markets

st.set_page_config(page_title="MarketMind AI", page_icon="🧠", layout="wide")

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
    
if "market_data" not in st.session_state:
    with st.spinner("Fetching live market data..."):
        st.session_state.market_data = get_ethical_markets()

st.sidebar.title("📊 Live Market Data")
st.sidebar.markdown("*(Filtered for Crypto, Tech, & Commodities)*")
st.sidebar.divider() 

for event in st.session_state.market_data:
    st.sidebar.subheader(event['title'])
    
    for contract in event["contracts"]:
        price = contract["prices"].get("buy", {}).get("yes", "N/A")
        if price != "N/A":
            probability = round(float(price) * 100)
            
            
            if probability > 70:
                color = "green"
            elif probability > 50:
                color = "orange"
            elif probability > 30:
                color = "gray"
            else:
                color = "red"
                
            st.sidebar.markdown(f"- **{contract['label']}**: :{color}[{probability}% YES]")
            
    st.sidebar.divider()

st.title("🧠 MarketMind AI")
st.write("Ask me anything about current prediction markets!")

for message in st.session_state.conversation_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask about a market... e.g., 'What's a strong YES?'"):
    
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    market_summary = ""
    for event in st.session_state.market_data:
        market_summary += f"\nMarket: {event['title']} (Category: {event['category']})\n"
        for contract in event["contracts"]:
            price = contract["prices"].get("buy", {}).get("yes", "N/A")
            if price != "N/A":
                prob = round(float(price) * 100)
                market_summary += f"  - {contract['label']}: {prob}% chance YES\n"

    SYSTEM_PROMPT = f"""You are MarketMind, an AI analyst specializing in prediction markets.
    You have access to live ethical market data (Crypto, Commodities, Tech only - no Sports).
    Use this data to answer user questions accurately and explain probabilities in plain English.

    When making recommendations, use this framework:
    - Probability > 70% → Strong YES signal
    - Probability 50-70% → Moderate YES signal
    - Probability 30-50% → Uncertain, high risk
    - Probability < 30% → Strong NO signal

    Always explain your reasoning in plain English so users understand WHY you're making a recommendation, not just what it is.

    LIVE MARKET DATA:
    {market_summary}
    """

    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.conversation_history

    with st.chat_message("assistant"):
        with st.spinner("Analyzing markets..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_api
            )
            assistant_response = response.choices[0].message.content
            st.markdown(assistant_response)
            
    st.session_state.conversation_history.append({"role": "assistant", "content": assistant_response})