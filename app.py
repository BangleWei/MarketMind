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

# --- 0. PROFESSIONAL THEMING (High-Contrast Terminal) ---
st.set_page_config(page_title="MarketMind Terminal", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');

    /* Global Foundation */
    .stApp { background-color: #0b0e14; color: #d1d5db; font-family: 'Inter', sans-serif; }
    
    /* Sidebar: Integrated Design */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
        min-width: 300px !important;
    }

    /* Live Ticker: High Contrast Glass */
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #38bdf8;
        border-radius: 8px;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    div[data-testid="stMetric"] label { 
        color: #38bdf8 !important; 
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1.5px;
        font-size: 0.75rem !important;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] > div {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #ffffff !important;
    }

    /* Chat Styling */
    .stChatMessage { background-color: #161b22 !important; border: 1px solid #30363d; border-radius: 12px; }
    
    /* Input Field */
    .stChatInputContainer { padding-bottom: 30px !important; }

    /* Buttons & Selectors */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1c2128 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 4px;
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
    colors = {70: "#00cc96", 50: "#FFA15A", 30: "#FECB52", 0: "#EF553B"}
    color = next(v for k, v in sorted(colors.items(), reverse=True) if probability >= k)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=probability,
        title={'text': "AI Confidence Score", 'font': {'color': 'white', 'size': 16}},
        number={'suffix': "%", 'font': {'color': color, 'family': 'JetBrains Mono'}},
        gauge={'axis': {'range': [0, 100], 'tickcolor': "white"}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)"}
    ))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
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

# --- 3. THE SIDEBAR (Interactive Product UI) ---
with st.sidebar:
    st.title("📊 Terminal")
    st.caption("v1.0.5-live | MarketMind Systems")
    st.divider()

    # Dynamic Sector Selector
    market_titles = [m['title'] for m in st.session_state.market_data]
    selected_market_name = st.selectbox("🎯 Select Active Sector", market_titles)
    selected_market = next(m for m in st.session_state.market_data if m['title'] == selected_market_name)
    
    # Update Active Contract
    first_contract = selected_market['contracts'][0]
    st.session_state.active_symbol = first_contract.get("instrumentSymbol")
    st.session_state.active_title = first_contract.get("label")
    
    # Ensure background websocket is running
    if st.session_state.active_symbol:
        start_websocket(st.session_state.active_symbol)
        
        # Display High-Contrast Ticker
        st.subheader("⚡ Live Stream")
        current_val = st.session_state.live_prices.get(st.session_state.active_symbol, 
                      first_contract.get("prices", {}).get("buy", {}).get("yes", 0.5))
        
        st.metric(
            label=f"CONTRACT: {st.session_state.active_title}",
            value=f"{round(float(current_val)*100, 1)}% YES",
            delta="ACTIVE WEBSOCKET"
        )

    st.divider()
    st.subheader("Inventory: " + selected_market_name)
    for contract in selected_market['contracts']:
        p = contract['prices'].get('buy', {}).get('yes', 'N/A')
        prob = f"{round(float(p)*100)}%" if p != 'N/A' else 'N/A'
        st.write(f"• {contract['label']}: **{prob}**")

# --- 4. MAIN CHAT INTERFACE ---
st.title("🧠 MarketMind Terminal")
st.caption("Institutional Analysis Engine | Powered by Groq LLaMA 3.3 & Gemini Data")

for msg in st.session_state.conversation_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart_data" in msg: 
            st.plotly_chart(create_gauge_chart(msg["chart_data"]), use_container_width=True)

if user_input := st.chat_input("Enter market query..."):
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    # UNIFIED DATA SUMMARY: Prioritizes live prices for the AI
    summary_list = []
    for m in st.session_state.market_data:
        for c in m['contracts']:
            sym = c.get("instrumentSymbol")
            price = st.session_state.live_prices.get(sym, c['prices'].get('buy',{}).get('yes','N/A'))
            summary_list.append(f"{m['title']} - {c['label']}: {price}")
    
    summary = "\n".join(summary_list)

    prompt = f"""You are MarketMind Terminal. Analyze LIVE Gemini prices:
    {summary}
    
    Professional Persona:
    - Institutional-grade analysis.
    - Framework: >70% Strong YES, 50-70% Moderate YES, <30% Strong NO.
    - End response with [SIGNAL: XX].
    """

    with st.chat_message("assistant"):
        with st.spinner("Executing analytical pass..."):
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