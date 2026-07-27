# Dhan AI Trading Bot — Step-by-Step Setup Guide

This guide walks you through setting up and running the Dhan AI Trading Bot from scratch.

---

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10 or higher** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/downloads))
- A **Dhan Trading Account** ([Open Account](https://www.dhan.co))
- An **OpenAI API Key** ([Get API Key](https://platform.openai.com/api-keys))
- Basic familiarity with terminal/command line

---

## Step 1: Clone the Repository

Open your terminal and run:

```bash
# Clone the repo
git clone https://github.com/dematprashant-ux/dhan-ai-trading-bot.git

# Navigate into the project
cd dhan-ai-trading-bot
```

---

## Step 2: Create a Virtual Environment

A virtual environment keeps dependencies isolated from your system Python:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# For Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt.

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- `openai` — AI decision engine
- `dhanhq` — Dhan Trading API SDK
- `pandas` — Data analysis (RSI, VWAP, Moving Averages)
- `pytz` — Timezone handling (IST market hours)

---

## Step 4: Get Your Dhan API Credentials

### 4a. Create/Log in to Your Dhan Account
1. Go to [https://www.dhan.co](https://www.dhan.co)
2. Create a new account or log in
3. Complete KYC verification (required for live trading)

### 4b. Get Your Client ID
1. Log in to the [Dhan Dashboard](https://www.dhan.co)
2. Navigate to **My Profile** or **Account Settings**
3. Find your **Client ID** (a numeric ID like `1000000001`)

### 4c. Generate Your Access Token
1. Go to **API Keys** or **Developer** section in the Dhan dashboard
2. Follow the OAuth flow or PIN+TOTP method to generate an **Access Token**
3. Copy the token — it's a long alphanumeric string

### 4d. Find Security IDs for Your Stocks
Every stock has a numeric Security ID on Dhan. You can find them by:
- Downloading the [Dhan Scrip Master CSV](https://images.dhan.co/api-data/api-scrip-master.csv)
- Searching the CSV for your stock's trading symbol

Common Security IDs (NSE):
| Symbol | Security ID | Company |
|--------|------------|---------|
| RELIANCE | 1333 | Reliance Industries |
| TCS | 11536 | Tata Consultancy Services |
| INFY | 1594 | Infosys |
| HDFCBANK | 42 | HDFC Bank |
| ICICIBANK | 496 | ICICI Bank |
| SBIN | 3045 | State Bank of India |
| ITC | 1624 | ITC Limited |
| BHARTIARTL | 1064 | Bharti Airtel |

---

## Step 5: Get Your OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in to your OpenAI account
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-...`)
5. Note: OpenAI charges per API call. Set usage limits in your dashboard.

---

## Step 6: Configure the Bot

```bash
# Copy the example config
cp config.py.example config.py
```

Now open `config.py` in any text editor and fill in your details:

```python
# ============================================
# YOUR API CREDENTIALS (fill these in)
# ============================================

# Dhan API Credentials
DHAN_CLIENT_ID = "YOUR_CLIENT_ID_HERE"          # From Step 4b
DHAN_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"    # From Step 4c

# OpenAI Credentials
OPENAI_API_KEY = "sk-YOUR_KEY_HERE"             # From Step 5

# ============================================
# TRADING MODE
# ============================================
# Choose ONE of: "demo", "manual", "auto"
MODE = "demo"

# ============================================
# TRADING PARAMETERS
# ============================================

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# How often to check the market (in seconds)
# 600 = every 10 minutes
RUN_INTERVAL_SECONDS = 600

# Exchange: NSE_EQ (equities), BSE_EQ, NSE_FNO (F&O)
DHAN_EXCHANGE_SEGMENT = "NSE_EQ"

# Product type: CNC = delivery, INTRADAY = intraday
DHAN_PRODUCT_TYPE = "CNC"

# ============================================
# WATCHLIST & EXCLUSIONS
# ============================================

# Stocks to watch and potentially buy
WATCHLIST_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "BHARTIARTL",
]

# Stocks to NEVER trade
TRADE_EXCEPTIONS = [
    # "TATASTEEL",   # Add symbols here to exclude them
]

# ============================================
# SECURITY ID MAPPING
# ============================================
# Map your stock symbols to Dhan's numeric security IDs
# Find IDs from: https://images.dhan.co/api-data/api-scrip-master.csv
SECURITY_ID_MAP = {
    "RELIANCE": "1333",
    "TCS": "11536",
    "INFY": "1594",
    "HDFCBANK": "42",
    "ICICIBANK": "496",
    "SBIN": "3045",
    "ITC": "1624",
    "BHARTIARTL": "1064",
}

# ============================================
# TRADING LIMITS (in INR)
# ============================================

MIN_SELLING_AMOUNT_USD = 1.0       # Min amount to sell (INR)
MAX_SELLING_AMOUNT_USD = 5000.0    # Max amount to sell (INR)
MIN_BUYING_AMOUNT_USD = 1.0        # Min amount to buy (INR)
MAX_BUYING_AMOUNT_USD = 10000.0    # Max amount to buy (INR)
PORTFOLIO_LIMIT = 10               # Max number of stocks to hold
WATCHLIST_OVERVIEW_LIMIT = 5       # Max watchlist stocks per AI analysis

# ============================================
# OPENAI MODEL
# ============================================
OPENAI_MODEL_NAME = "gpt-4o-mini"  # Cheapest GPT-4o model
```

---

## Step 7: Understand the Trading Modes

### 🟢 Demo Mode (`MODE = "demo"`)
- **No real trades** are executed
- The bot simulates all actions
- Perfect for testing configuration and understanding behavior
- **Start here!**

### 🟡 Manual Mode (`MODE = "manual"`)
- Real trades are executed, but **each trade requires your confirmation**
- You type `yes` or `no` for every buy/sell decision
- Good for learning how the AI thinks

### 🔴 Auto Mode (`MODE = "auto"`)
- Trades are executed **automatically** without confirmation
- Only use this after thorough testing in demo/manual mode
- The bot will buy and sell based on AI recommendations

---

## Step 8: Run the Bot

```bash
# Make sure your virtual environment is active (you see `(venv)` in the prompt)
# If not, run: source venv/bin/activate

python main.py
```

### What Happens Next:

1. **Config validation** — Checks that API keys are set
2. **Market hours check** — Verifies the Indian market is open (Mon-Fri, 9:15 AM - 3:30 PM IST)
3. **Data collection** — Fetches your portfolio holdings and watchlist stock data
4. **Technical analysis** — Calculates RSI, VWAP, and Moving Averages for each stock
5. **AI decision** — Sends data to OpenAI for buy/sell/hold recommendations
6. **Validation** — Filters out AI hallucinations (invalid quantities, impossible trades)
7. **Execution** — Executes trades (or simulates in demo mode)
8. **Repeat** — Waits `RUN_INTERVAL_SECONDS` and repeats

### Example Output:

```
[2025-07-26 09:15:01] [INFO]    Market is open, running trading bot in auto mode...
[2025-07-26 09:15:01] [INFO]    Getting account info...
[2025-07-26 09:15:05] [INFO]    Getting portfolio stocks...
[2025-07-26 09:15:05] [INFO]    Portfolio stocks to proceed: RELIANCE (45.12%), TCS (30.5%)
[2025-07-26 09:15:05] [INFO]    Prepare portfolio stocks for AI analysis...
[2025-07-26 09:15:10] [INFO]    Getting watchlist stocks...
[2025-07-26 09:15:11] [INFO]    Watchlist stocks to proceed: INFY, HDFCBANK, ICICIBANK
[2025-07-26 09:15:11] [INFO]    Prepare watchlist overview for AI analysis...
[2025-07-26 09:15:12] [INFO]    Making AI-based decision...
[2025-07-26 09:15:24] [INFO]    Executing decisions...
[2025-07-26 09:15:24] [INFO]    RELIANCE > Decision: sell of 5
[2025-07-26 09:15:24] [INFO]    RELIANCE > Sold 5 stocks
[2025-07-26 09:15:25] [INFO]    INFY > Decision: buy of 2
[2025-07-26 09:15:27] [INFO]    INFY > Bought 2 stocks
[2025-07-26 09:15:28] [INFO]    Sold: RELIANCE (5)
[2025-07-26 09:15:28] [INFO]    Bought: INFY (2)
[2025-07-26 09:15:28] [INFO]    Errors: None
[2025-07-26 09:15:28] [INFO]    Waiting for 600 seconds...
```

---

## Step 9: Monitoring and Adjustments

### Check Trade Logs
All activity is printed to the console. For persistent logging, set `LOG_LEVEL = "DEBUG"` in config.

### Common Scenarios

| Symptom | Solution |
|---------|----------|
| "Config error: DHAN_CLIENT_ID is empty" | Fill in credentials in `config.py` |
| "Market is closed" | Bot only runs during market hours (9:15 AM - 3:30 PM IST, Mon-Fri) |
| "No security ID mapping found for XYZ" | Add the stock's security ID to `SECURITY_ID_MAP` in config |
| "Not enough data to calculate RSI" | Normal for newly added stocks; data accumulates over time |
| AI returns empty decisions | Market conditions may not warrant any trades right now |
| Bot crashes on API error | Check internet connection; bot has built-in retry logic |

### Fine-Tuning Tips

1. **Start small** — Begin with 2-3 stocks in your watchlist
2. **Set conservative limits** — Use small `MAX_BUYING_AMOUNT_USD` values
3. **Monitor for a week** — Watch what the AI decides before enabling auto mode
4. **Adjust RSI thresholds** — The AI considers RSI > 70 overbought, < 30 oversold
5. **Use TRADE_EXCEPTIONS** — Exclude stocks you want to hold long-term

---

## Important Notes

### Market Hours
The bot automatically detects Indian market hours:
- **NSE/BSE**: 9:15 AM to 3:30 PM IST (Monday to Friday)
- The bot will **not** execute trades outside these hours
- It will wait and retry at the next interval

### eDIS / T-Pin Authorization
- For **CNC (delivery) sells**, Dhan requires eDIS T-Pin authorization
- The bot will attempt to sell, but you may need to authorize on the Dhan app
- Consider using `INTRADAY` product type to avoid this requirement

### AI Decision Making
- The bot sends stock data (RSI, VWAP, Moving Averages) to OpenAI
- OpenAI returns buy/sell/hold decisions with quantities
- The bot validates these decisions before executing (filters hallucinations)
- Each AI call costs a few cents (depending on the model)

### Cost Estimation
| Component | Cost |
|-----------|------|
| OpenAI API (gpt-4o-mini) | ~$0.001 per stock per cycle |
| Dhan API | Free (included with trading account) |
| Daily cost (10 stocks, every 10 min) | ~$0.20-0.50/day |

---

## Troubleshooting

### Bot won't start
```bash
# Make sure you're in the right directory
cd dhan-ai-trading-bot

# Make sure venv is active
source venv/bin/activate

# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt
```

### Import errors
```bash
# If you see "No module named 'dhanhq'"
pip install dhanhq

# If you see "No module named 'openai'"
pip install openai
```

### API errors from Dhan
1. Verify `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN` are correct
2. Check if your Dhan account is active and KYC is complete
3. Access tokens may expire — regenerate if needed
4. Check Dhan API status at [https://api.dhan.co](https://api.dhan.co)

### AI returning invalid data
The bot has a hallucination filter that catches:
- Zero quantities
- Symbols not in your portfolio/watchlist
- Buy orders for stocks with no security ID mapping
- Sell orders for stocks you don't own

---

## Quick Start Summary

```bash
# 1. Clone
git clone https://github.com/dematprashant-ux/dhan-ai-trading-bot.git
cd dhan-ai-trading-bot

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp config.py.example config.py
# Edit config.py with your credentials

# 5. Run (in demo mode first!)
python main.py
```

---

## ⚠️ Disclaimer

This bot is designed solely for **educational purposes**. Trading stocks involves significant risks.
- You should only invest money you can afford to lose
- The author is not liable for any financial losses
- Past performance does not guarantee future results
- Always do your own research before making investment decisions

---

*Last updated: July 2026*