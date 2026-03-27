# MarketMind
PBC Hackathon 26'

# 🧠 MarketMind Terminal: For Gemini Prediction Markets

**An Institutional Analysis Engine built on the live Gemini WebSocket API, Groq, and a Deterministic Local Quant Engine.**

MarketMind is an advanced trading terminal designed to bridge the gap between high-speed Large Language Models and real-time **Gemini Prediction Markets**. 

Built directly on top of the **Gemini Crypto Exchange API**, MarketMind provides traders with a Bloomberg-style interface to track live contract probabilities, execute zero-latency sentiment analysis, and run institutional-grade quantitative simulations on Gemini order book data.

## ⚡ Core Architecture

### 1. Live Gemini WebSocket Integration
MarketMind does not rely on static data. It establishes a persistent, real-time WebSocket connection to `wss://api.gemini.com/v1/marketdata/`. As Gemini prediction market contracts tick up and down, the terminal updates instantly, injecting the live global state into the AI's context window.

### 2. Deterministic Quant Engine (Solving AI Hallucinations)
LLMs are excellent at qualitative analysis but notoriously unreliable at quantitative math. MarketMind solves this to provide safe, actionable data for Gemini traders:
* The system utilizes a **Zero-Latency Intent Router**. 
* When a user asks a complex quantitative question about a Gemini market, the prompt is intercepted by the backend.
* The system runs the math locally in Python via `numpy` (e.g., 10,000-step Monte Carlo simulations, Kelly Criterion risk sizing based on live Gemini probabilities).
* The deterministic, pre-calculated results are then fed to the LLM (Groq/LLaMA 3.3) for formatting and presentation.

### 3. Dynamic Context Sifting (Token Optimization)
To achieve sub-second inference speeds, MarketMind employs heuristic context filtering. Instead of dumping the entire state of the Gemini exchange into the LLM, the system scans the user's prompt for asset-specific keywords (e.g., "BTC", "ETH"). It dynamically trims the payload, sending *only* the relevant Gemini market data to the API, drastically reducing latency.

### 4. UI-Interceptor & Interactive Visuals
The frontend is a reactive terminal. The backend intercepts hidden data tags from the AI to dynamically generate interactive Plotly Gauge Charts, and automatically renders 100-path spaghetti charts for 50-step Kelly Bankroll Projections based on the active Gemini contract.

## 🚀 Features
* **Click-to-Analyze UI:** Built with custom Streamlit `@st.fragment` architecture, allowing the user to switch active Gemini sectors or trigger market analysis without disrupting the conversational state.
* **Glassmorphism Terminal Design:** Custom CSS overrides default aesthetics to create a dark, distraction-free institutional UI.
* **Agentic Alert Ready:** Architecture supports background monitoring of the Gemini WebSocket stream to proactively alert users to >5% probability swings.

## 🛠️ Installation & Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/marketmind.git](https://github.com/yourusername/marketmind.git)
   cd marketmind