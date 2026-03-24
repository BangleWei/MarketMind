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