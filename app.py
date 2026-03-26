import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import threading
import websocket
import json
import plotly.graph_objects as go
import re
import numpy as np
from market_data import get_ethical_markets

# ─── 0. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MarketMind Terminal", 
    page_icon="🧠", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
}

[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #21262d !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
/* Apply font to sidebar, but exempt Streamlit's icon fonts */
/* Apply font to sidebar, but exempt Streamlit's icon fonts */
[data-testid="stSidebar"] *:not(.material-symbols-rounded) { 
    font-family: 'JetBrains Mono', monospace !important; 
}

/* Completely hide the ghost text / collapse button for a cleaner terminal */
[data-testid="stSidebarCollapseButton"] { 
    display: none !important; 
}[data-testid="stSidebar"] *:not(.material-symbols-rounded):not(svg) { 
    font-family: 'JetBrains Mono', monospace !important; 
}

/* Style the sidebar toggle arrow */
[data-testid="stSidebarCollapseButton"] {
    color: #8b949e !important;
    background-color: transparent !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    color: #f0a732 !important;
}
[data-testid="stSidebar"] h1 {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    color: #f0a732 !important;
    text-transform: uppercase !important;
    margin-bottom: 0 !important;
}
[data-testid="stSidebar"] .stCaption p {
    color: #484f58 !important;
    font-size: 10px !important;
    letter-spacing: 1px;
}
[data-testid="stSidebar"] hr { border-color: #21262d !important; margin: 8px 0 !important; }
[data-testid="stSidebar"] h3 {
    font-size: 9px !important;
    font-weight: 700 !important;
    color: #484f58 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}

div[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #f0a732;
    border-radius: 2px;
    padding: 10px 12px !important;
    margin-bottom: 4px;
}
div[data-testid="stMetric"] label {
    color: #f0a732 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetricValue"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: -0.5px;
}
div[data-testid="stMetricDelta"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    color: #39d353 !important;
}

.stSelectbox label {
    font-size: 9px !important;
    color: #484f58 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: #c9d1d9 !important;
}
.stSelectbox div[data-baseweb="select"] > div:hover { border-color: #f0a732 !important; }

.stApp h1 {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #f0a732 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase;
    margin-bottom: 0 !important;
}
.stApp .stCaption p {
    color: #484f58 !important;
    font-size: 10px !important;
    letter-spacing: 1px;
}

.stat-block {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 2px;
    padding: 8px 12px;
}
.stat-label { font-size: 9px; color: #484f58; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px; }
.stat-value { font-size: 16px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.up   { color: #39d353; }
.down { color: #f85149; }
.neu  { color: #f0a732; }

.prob-bar-wrap { display: flex; align-items: center; gap: 6px; }
.prob-bar { height: 4px; background: #21262d; flex: 1; border-radius: 0; overflow: hidden; }
.prob-fill { height: 100%; background: #f0a732; }
.badge { font-size: 9px; font-weight: 700; padding: 2px 5px; border-radius: 1px; letter-spacing: .5px; }
.badge-yes { background: #0f2d0f; color: #39d353; }
.badge-no  { background: #2d0f0f; color: #f85149; }

/* Analyze button */
div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #30363d !important;
    border-radius: 2px !important;
    color: #484f58 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    padding: 2px 8px !important;
    height: 24px !important;
    line-height: 1 !important;
    transition: all 0.1s !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #f0a732 !important;
    color: #f0a732 !important;
    background: rgba(240,167,50,0.05) !important;
}

/* Sidebar Specific Buttons */
div[data-testid="stSidebar"] button {
    background-color: transparent !important;
    border: 1px solid #21262d !important;
    color: #8b949e !important;
    text-align: left !important;
    padding: 2px 8px !important;
    font-size: 10px !important;
}
div[data-testid="stSidebar"] button:hover {
    border-color: #f0a732 !important;
    color: #f0a732 !important;
}

.stChatMessage {
    background-color: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 2px !important;
    padding: 12px !important;
}
.stChatMessage p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    line-height: 1.7 !important;
    color: #c9d1d9 !important;
}

.stChatInputContainer {
    background: #0d1117 !important;
    border: 1px solid #21262d !important;
    border-radius: 2px !important;
}
.stChatInputContainer textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: #c9d1d9 !important;
    background: transparent !important;
}
.stChatInputContainer textarea::placeholder { color: #30363d !important; }
.stChatInputContainer:focus-within { border-color: #30363d !important; }

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stChatFloatingInputContainer {
    background: #0d1117 !important;
    border-top: 1px solid #21262d !important;
}
.stChatFloatingInputContainer { padding: 8px 0 !important; }

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── 1. INIT ───────────────────────────────────────────────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if "conversation_history"  not in st.session_state: st.session_state.conversation_history  = []
if "pending_query"         not in st.session_state: st.session_state.pending_query         = None
if "active_query"          not in st.session_state: st.session_state.active_query          = None
if "cached_response"       not in st.session_state: st.session_state.cached_response       = None
if "market_data"           not in st.session_state:
    with st.spinner("INITIALIZING TERMINAL..."):
        st.session_state.market_data = get_ethical_markets()
if "live_prices"           not in st.session_state: st.session_state.live_prices           = {}

# ─── 2. GAUGE CHART ────────────────────────────────────────────────────────────
def create_gauge_chart(probability):
    if   probability >= 70: color = "#39d353"
    elif probability >= 50: color = "#f0a732"
    elif probability >= 30: color = "#FFA15A"
    else:                   color = "#f85149"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        title={'text': "AI CONFIDENCE SIGNAL", 'font': {'color': '#484f58', 'size': 11, 'family': 'JetBrains Mono'}},
        number={'suffix': "%", 'font': {'color': color, 'family': 'JetBrains Mono', 'size': 36}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#30363d", 'tickfont': {'color': '#484f58', 'size': 9, 'family': 'JetBrains Mono'}},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': "rgba(0,0,0,0)",
            'bordercolor': "#21262d",
            'steps': [
                {'range': [0,  30],  'color': '#2d0f0f'},
                {'range': [30, 50],  'color': '#2a1d0f'},
                {'range': [50, 70],  'color': '#1d1a0f'},
                {'range': [70, 100], 'color': '#0f2d0f'},
            ]
        }
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#c9d1d9", 'family': 'JetBrains Mono'}
    )
    return fig
def create_mc_chart(top_p, kelly_pct):
    # Simulate bankroll growth: 100 alternate realities, 50 trades each
    paths = 100
    steps = 50
    bankroll = np.zeros((paths, steps + 1))
    bankroll[:, 0] = 1000 # Starting bankroll: $1,000

    # Convert Kelly percentage to a decimal fraction
    f = kelly_pct / 100.0 if kelly_pct > 0 else 0.05 # Minimum 5% bet if Kelly is 0 just to visualize variance
    b = (1 / top_p) - 1 if top_p > 0 else 1 # Implied odds

    # Generate the simulated price paths
    for i in range(paths):
        outcomes = np.random.binomial(1, top_p, steps)
        for t in range(steps):
            bet_size = bankroll[i, t] * f
            if outcomes[t] == 1:
                bankroll[i, t+1] = bankroll[i, t] + bet_size * b
            else:
                bankroll[i, t+1] = bankroll[i, t] - bet_size

    fig = go.Figure()
    
    # Plot all 100 alternate reality paths
    for i in range(paths):
        fig.add_trace(go.Scatter(
            x=list(range(steps + 1)), y=bankroll[i], mode='lines',
            line=dict(color='rgba(240, 167, 50, 0.03)', width=1),
            showlegend=False, hoverinfo='skip'
        ))
    
    # Plot the Mean Expected path
    mean_path = np.mean(bankroll, axis=0)
    fig.add_trace(go.Scatter(
        x=list(range(steps + 1)), y=mean_path, mode='lines',
        line=dict(color='#39d353', width=3), name='Mean Bankroll Projection'
    ))

    fig.update_layout(
        title={'text': "MONTE CARLO: 50-STEP KELLY BANKROLL PROJECTION", 'font': {'color': '#484f58', 'size': 11, 'family': 'JetBrains Mono'}},
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#c9d1d9", 'family': 'JetBrains Mono'},
        xaxis=dict(showgrid=True, gridcolor='#21262d', title="Trades Executed"),
        yaxis=dict(showgrid=True, gridcolor='#21262d', title="Projected Capital ($)"),
        height=320, margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)")
    )
    return fig
# ─── 3. WEBSOCKET ──────────────────────────────────────────────────────────────
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
        threading.Thread(target=run, daemon=True).start()
        st.session_state[f"ws_thread_{symbol}"] = True

# ─── 4. SIDEBAR (FRAGMENT) ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("MKTMIND")
    st.caption("v1.0.8-live  |  Golden Matrix")
    st.divider()

    @st.fragment
    def render_interactive_sidebar():
        market_titles = [m['title'] for m in st.session_state.market_data]
        selected_market_name = st.selectbox("ACTIVE SECTOR", market_titles)
        selected_market = next(m for m in st.session_state.market_data if m['title'] == selected_market_name)

        first_contract = selected_market['contracts'][0]
        st.session_state.active_symbol = first_contract.get("instrumentSymbol")
        st.session_state.active_title  = first_contract.get("label")

        if st.session_state.active_symbol:
            start_websocket(st.session_state.active_symbol)
            current_val = st.session_state.live_prices.get(
                st.session_state.active_symbol,
                first_contract.get("prices", {}).get("buy", {}).get("yes", 0.5)
            )
            st.divider()
            st.subheader("⚡ LIVE TICKER")
            st.metric(label=st.session_state.active_title, value=f"{round(float(current_val)*100,1)}%", delta="LIVE STREAM")

        st.divider()
        st.subheader("ALL MARKETS (CLICK TO ANALYZE)")
        for contract in selected_market['contracts']:
            p = contract['prices'].get('buy', {}).get('yes', None)
            if p is not None:
                pct = round(float(p) * 100)
                label = contract['label']
                badge_color = "#39d353" if pct >= 50 else "#f85149"
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"{label}", key=f"btn_{contract['instrumentSymbol']}", use_container_width=True):
                        st.session_state.pending_query = f"Provide a complete analysis on the {label} market. Is this a strong position?"
                        st.rerun()
                with col2:
                    st.markdown(f"<div style='color:{badge_color}; font-weight:bold; padding-top:8px;'>{pct}%</div>", unsafe_allow_html=True)
    
    render_interactive_sidebar()

# ─── 5. MAIN AREA ──────────────────────────────────────────────────────────────
st.title("MARKETMIND TERMINAL")
st.caption("INSTITUTIONAL ANALYSIS ENGINE")

all_contracts = [c for m in st.session_state.market_data for c in m['contracts']]
total_markets = len(all_contracts)
valid_prices  = [float(c['prices'].get('buy',{}).get('yes',0)) for c in all_contracts if c['prices'].get('buy',{}).get('yes') is not None]
top_prob      = round(max(valid_prices)*100,1) if valid_prices else 0
avg_prob      = round(sum(valid_prices)/len(valid_prices)*100,1) if valid_prices else 0
strong_yes    = sum(1 for p in valid_prices if p >= 0.7)

col1,col2,col3,col4 = st.columns(4)
for col, label, value, cls in [
    (col1,"MARKETS",str(total_markets),"neu"),
    (col2,"TOP PROBABILITY",f"{top_prob}%","up"),
    (col3,"AVG PROBABILITY",f"{avg_prob}%","neu"),
    (col4,"STRONG YES",str(strong_yes),"up"),
]:
    with col:
        st.markdown(f'<div class="stat-block"><div class="stat-label">{label}</div><div class="stat-value {cls}">{value}</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

hcols = st.columns([3,3,1,2,1])
for hcol, lbl in zip(hcols, ["SECTOR","CONTRACT","SIGNAL","PROBABILITY",""]):
    hcol.markdown(f"<div style='font-size:9px;color:#484f58;letter-spacing:1px;padding:4px 0;border-bottom:1px solid #21262d'>{lbl}</div>", unsafe_allow_html=True)

for m in st.session_state.market_data:
    for c in m['contracts']:
        sym = c.get("instrumentSymbol")
        p   = st.session_state.live_prices.get(sym, c['prices'].get('buy',{}).get('yes'))
        if p is None:
            continue
        pct   = round(float(p)*100)
        badge = '<span class="badge badge-yes">YES</span>' if pct >= 50 else '<span class="badge badge-no">NO</span>'
        bar   = f'<div class="prob-bar-wrap"><div class="prob-bar"><div class="prob-fill" style="width:{pct}%"></div></div><span style="color:#f0a732;font-weight:700;min-width:32px">{pct}%</span></div>'

        c1,c2,c3,c4,c5 = st.columns([3,3,1,2,1])
        c1.markdown(f"<div style='font-size:11px;color:#8b949e;padding:5px 0;border-bottom:1px solid #161b22'>{m['title']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='font-size:11px;color:#c9d1d9;padding:5px 0;border-bottom:1px solid #161b22'>{c['label']}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='padding:5px 0;border-bottom:1px solid #161b22'>{badge}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='padding:5px 0;border-bottom:1px solid #161b22'>{bar}</div>", unsafe_allow_html=True)
        with c5:
            if st.button("▶", key=f"analyze_{sym}", help=f"Analyze {c['label']}"):
                st.session_state.pending_query = f"Analyze this contract: {m['title']} — {c['label']} is currently at {pct}% probability. Why is it priced here and what's your signal?"
                st.rerun()

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ─── 6. CHAT ───────────────────────────────────────────────────────────────────
for msg in st.session_state.conversation_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart_data" in msg:
            st.plotly_chart(create_gauge_chart(msg["chart_data"]), use_container_width=True)
        if "mc_chart" in msg:
            st.plotly_chart(msg["mc_chart"], use_container_width=True)

if user_input := st.chat_input("Ask about any market or run quant analysis..."):
    pass
else:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None

if user_input:
    summary = "\n".join(
        f"{m['title']} — {c['label']}: "
        f"{st.session_state.live_prices.get(c.get('instrumentSymbol'), c['prices'].get('buy',{}).get('yes','N/A'))}"
        for m in st.session_state.market_data for c in m['contracts']
    )

    is_new_query = (user_input != st.session_state.active_query)

    if is_new_query:
        st.session_state.active_query    = user_input
        st.session_state.cached_response = None 
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

    if st.session_state.cached_response:
        with st.chat_message("assistant"):
            entry = st.session_state.cached_response
            st.markdown(entry["content"])
            if "chart_data" in entry:
                st.plotly_chart(create_gauge_chart(entry["chart_data"]), use_container_width=True)
    else:
        # INVISIBLE ROUTER -> LOCAL NUMPY MATH + GROQ
        quant_keywords = ["kelly","monte carlo","simulate","simulation","correlation","matrix","optimal bet","calculate","math","quant"]
        is_quant = any(kw in user_input.lower() for kw in quant_keywords)

        if is_quant:
            with st.chat_message("assistant"):
                with st.spinner("INITIATING QUANT ENGINE (LOCAL MATH × GROQ)..."):
                    try:
                        # --- LOCAL MATH ENGINE (0 Latency, 100% Free) ---
                        top_p = max(valid_prices) if valid_prices else 0.50
                        
                        # 1. Kelly Criterion Math
                        b = (1 / top_p) - 1 if top_p > 0 else 1
                        kelly_pct = round(max(0, ((top_p * b - (1-top_p)) / b) * 100), 2) if b > 0 else 0
                        
                        # 2. Monte Carlo Simulation (10,000 runs)
                        simulations = 10000
                        outcomes = np.random.binomial(1, top_p, simulations) 
                        sim_mean = np.mean(outcomes)
                        sim_std = np.std(outcomes)

                        math_context = f"""
                        SYSTEM PRE-CALCULATED MATH (RUN LOCALLY IN PYTHON):
                        - Target Probability: {top_p * 100}%
                        - Optimal Kelly Allocation: {kelly_pct}%
                        - Monte Carlo ({simulations} runs) Mean Value: {sim_mean:.4f}
                        - Monte Carlo Standard Deviation: {sim_std:.4f}
                        """

                        sandbox_prompt = f"""You are the MarketMind Quant Engine.
TASK: {user_input}
LIVE MARKET DATA: {summary}
{math_context}

INSTRUCTIONS:
1. You act as a quantitative analyst. 
2. The system has already run the Python math for you. Use the PRE-CALCULATED MATH provided above to answer the user's specific question.
3. If asked about the Monte Carlo simulation, explain what Standard Deviation means in this context (risk/volatility) and cite the exact pre-calculated number.
4. If asked about Kelly Criterion, explain the logic and provide the exact pre-calculated percentage.
5. Format cleanly using markdown. Do NOT use the [SIGNAL: XX] tag here.
"""
                        res = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role":"system","content":sandbox_prompt}]
                        )
                        text = res.choices[0].message.content
                        st.markdown(text)
                        
                        # Generate the dynamic visual!
                        fig_mc = create_mc_chart(top_p, kelly_pct)
                        st.plotly_chart(fig_mc, use_container_width=True)
                        
                        # Save the visual state so it doesn't disappear on refresh
                        entry = {"role": "assistant", "content": text, "mc_chart": fig_mc}
                        st.session_state.cached_response = entry
                        st.session_state.conversation_history.append(entry)
                    except Exception as e:
                        st.error(f"Quant Engine Error: {e}")
        else:
            with st.chat_message("assistant"):
                with st.spinner("EXECUTING ANALYTICAL PASS (GROQ)..."):
                    prompt = f"""You are MarketMind Terminal. Analyse LIVE Gemini prediction market prices.
DATA:
{summary}
RULES:
- Institutional-grade, concise, no filler.
- Framework: >70% = STRONG YES | 50–70% = MODERATE YES | <30% = STRONG NO
- Always end with [SIGNAL: XX] where XX is 0–100."""
                    res  = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"system","content":prompt}]
                                 + [m for m in st.session_state.conversation_history if "chart_data" not in m]
                    )
                    raw  = res.choices[0].message.content
                    text = re.sub(r'\[SIGNAL:\s*\d+\]', '', raw).strip()
                    st.markdown(text)

                    entry = {"role": "assistant", "content": text}
                    match = re.search(r'\[SIGNAL:\s*(\d+)\]', raw)
                    if match:
                        val = int(match.group(1))
                        st.plotly_chart(create_gauge_chart(val), use_container_width=True)
                        entry["chart_data"] = val

                    st.session_state.cached_response = entry
                    st.session_state.conversation_history.append(entry)