import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import threading
import websocket
import json
import plotly.graph_objects as go
import re
from market_data import get_ethical_markets

# --- 0. PROFESSIONAL THEMING ---
st.set_page_config(page_title="MarketMind Terminal", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');

    /* Global Foundation */
    .stApp { background-color: #0b0e14; color: #d1d5db; font-family: 'Inter', sans-serif; }
    
    /* Sidebar: Tight & Integrated */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
        min-width: 280px !important;
    }

    /* Live Ticker: High Contrast Glass */
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #38bdf8; /* Blue border to show it's "Active" */
        border-radius: 4px;
        padding: 15px !important;
    }
    div[data-testid="stMetric"] label { 
        color: #38bdf8 !important; 
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1px;
        font-size: 0.7rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #ffffff;
    }

    /* Main Header Styling */
    h1 { font-weight: 800; color: #ffffff !important; letter-spacing: -1.5px; }
    .stCaption { color: #8b949e !important; font-family: 'JetBrains Mono', monospace; }

    /* Buttons & Selectors */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }

    /* Remove Clutter */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- 1. STATE & GAUGE LOGIC ---
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "market_data" not in st.session_state:
    with st.spinner("Initializing Terminal..."):
        st.session_state.market_data = get_ethical_markets()
if "live_prices" not in st.session_state:
    st.session_state.live_prices = {}

def create_gauge_chart(probability):
    if probability >= 70: color = "#00cc96"
    elif probability >= 50: color = "#FFA15A"
    elif probability >= 30: color = "#FECB52"
    else: color = "#EF553B"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=probability,
        title={'text': "MarketMind Confidence", 'font': {'color': 'white', 'size': 16}},
        number={'suffix': "%", 'font': {'color': color}},
        gauge={'axis': {'range': [0, 100], 'tickcolor': "white"}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)"}
    ))
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

# --- 2. WEBSOCKET THREAD ---
def start_websocket(symbol):
    def on_message(ws, message):
        data = json.loads(message)
        if data.get("type") == "update":
            for event in data.get("events", []):
                if event.get("type") == "trade":
                    st.session_state.live_prices[symbol] = event.get("price")
    def run():
        websocket.WebSocketApp(f"wss://api.gemini.com/v1/marketdata/{symbol}", on_message=on_message).run_forever()
    if f"ws_thread_{symbol}" not in st.session_state:
        t = threading.Thread(target=run, daemon=True)
        t.start()
        st.session_state[f"ws_thread_{symbol}"] = True

# --- 3. SIDEBAR (Full & Stable) ---
with st.sidebar:
    st.title("📊 Terminal Data")
    st.markdown("*(Crypto, Tech, Commodities)*")
    st.divider()

    # --- 3. DYNAMIC SYMBOL SELECTION ---
if "active_symbol" not in st.session_state:
    try:
        # We grab the first high-liquidity market as the default
        market = st.session_state.market_data[0]
        contract = market['contracts'][0]
        st.session_state.active_symbol = contract.get("instrumentSymbol")
        st.session_state.active_title = contract.get("label")
        
        # Pre-fill live price with REST data so UI isn't empty on load
        initial_val = contract.get("prices", {}).get("buy", {}).get("yes", 0.5)
        st.session_state.live_prices[st.session_state.active_symbol] = initial_val
    except Exception as e:
        st.error(f"Sync Error: {e}")

# Kicks off the WebSocket for the dynamic symbol
if st.session_state.active_symbol:
    start_websocket(st.session_state.active_symbol)

# UI Display for the Ticker
with st.sidebar:
    st.subheader("⚡ LIVE TICKER")
    sym = st.session_state.active_symbol
    current_val = st.session_state.live_prices.get(sym, 0.5)
    st.metric(
        label=st.session_state.active_title, 
        value=f"{round(float(current_val)*100, 1)}% YES", 
        delta="LIVE STREAM"
    )
    
    st.divider()
    st.subheader("All Active Markets")
    for market in st.session_state.market_data:
        with st.expander(market['title']):
            for contract in market['contracts']:
                p = contract['prices'].get('buy', {}).get('yes', 'N/A')
                if p != 'N/A':
                    st.write(f"{contract['label']}: **{round(float(p)*100)}%**")

# --- 4. MAIN CHAT ---
st.title("🧠 MarketMind Terminal")
st.caption("Professional Prediction Market Analyst | Powered by Groq & Gemini")

for msg in st.session_state.conversation_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart_data" in msg: 
            st.plotly_chart(create_gauge_chart(msg["chart_data"]), use_container_width=True)

if user_input := st.chat_input("Analyze a market sector..."):
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    summary = ""
    for m in st.session_state.market_data:
        for c in m['contracts']:
            summary += f"{m['title']} - {c['label']}: {c['prices'].get('buy',{}).get('yes','N/A')}\n"

    prompt = f"""You are MarketMind, an institutional analyst for Gemini Prediction Markets.
    Explain 'WHY' probabilities move based on market dynamics.
    Framework: >70% Strong YES, 50-70% Moderate YES, <30% Strong NO.
    CRITICAL: End your response with [SIGNAL: XX] where XX is the 0-100 probability. 
    DATA: {summary}"""

    with st.chat_message("assistant"):
        with st.spinner("Crunching market data..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": prompt}] + st.session_state.conversation_history
            )
            raw = res.choices[0].message.content
            text = re.sub(r'\[SIGNAL:\s*\d+\]', '', raw).strip()
            st.markdown(text)
            
            entry = {"role": "assistant", "content": text}
            match = re.search(r'\[SIGNAL:\s*(\d+)\]', raw)
            if match:
                val = int(match.group(1))
                st.plotly_chart(create_gauge_chart(val), use_container_width=True)
                entry["chart_data"] = val
            st.session_state.conversation_history.append(entry)