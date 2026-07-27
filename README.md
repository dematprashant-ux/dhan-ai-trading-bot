# Dhan AI Trading Bot

## ⚡ Overview
The **Dhan AI Trading Bot** is a simple Python script
that combines **OpenAI's intelligence** with **Dhan's trading capabilities**
to help automate and optimize stock trading decisions on Indian stock exchanges (NSE/BSE).
By analyzing **Relative Strength Index (RSI)**, **Volume-Weighted Average Price (VWAP)**,
and **Moving Averages**, the bot generates buy, sell,
and hold recommendations — executing trades automatically based on your selected mode.

## 🤔 Why This Bot?
This project is an experiment
to explore how AI can enhance stock trading decisions — potentially outperforming human traders
(or at least me, The Bot Father).

## ⚠️ Important Considerations
- **Start in Demo or Manual Mode** before enabling Auto Mode.
- **Test thoroughly** to fine-tune AI decision-making.
- **Monitor trade logs** to understand AI-driven actions.
- **Note:** For CNC (delivery) sells, Dhan requires eDIS T-Pin authorization.

## 🛠 Features
✅ **AI-Driven Trading** – Smart, data-backed buy/sell decisions.  
✅ **Portfolio & Watchlist Integration** – Trade directly from your Dhan holdings.  
✅ **Configurable Strategy** – Set trading parameters to fit your risk profile.  
✅ **Exclusion List** – Prevent trading specific stocks.  
✅ **Logging & Analytics** – Track bot activity and trading history.  
✅ **Indian Market Hours** – Automatically aligns with NSE/BSE trading hours (9:15 AM - 3:30 PM IST).

## 🚀 Getting Started
1. **Connect Your Accounts**: Add your OpenAI API Key and Dhan API credentials.
2. **Choose a Mode**:
   - **Demo Mode**: Simulates trades without execution.
   - **Manual Mode**: Requires confirmation before executing trades.
   - **Auto Mode**: Executes trades automatically (recommended only after testing).
3. **Monitor and Adjust**: Review trade logs and fine-tune settings for optimal performance.

## 📊 How It Works
1. **Authenticate**: Connects to OpenAI and Dhan using your API credentials.
2. **Fetch Data**: Retrieves stocks from your **portfolio** (holdings) and **watchlist** (configured symbols).
3. **Analyze Market Conditions**:
   - **RSI**: Determines overbought/oversold conditions.
   - **VWAP**: Identifies undervalued/overvalued stocks.
   - **Moving Averages**: Evaluates price trends (50-day and 200-day).
4. **AI-Driven Decisions**: Uses OpenAI to generate trading recommendations.
5. **Trade Execution**: Buys, sells, or holds stocks based on AI insights.
6. **Continuous Monitoring**: Repeats analysis and trades as the market evolves.

## 📈 Analytical System
### **Relative Strength Index (RSI)**
- Measures momentum on a **0-100 scale**.
- **Above 70**: Overbought (potential sell signal).
- **Below 30**: Oversold (potential buy signal).

### **Volume-Weighted Average Price (VWAP)**
- Calculates the **average price** adjusted for volume.
- **Above VWAP**: Overvalued (potential sell signal).
- **Below VWAP**: Undervalued (potential buy signal).

### **Moving Averages**
- **50-day & 200-day moving averages** help detect trends.
- **Golden Cross (50-day crosses above 200-day)**: Bullish signal.
- **Death Cross (50-day crosses below 200-day)**: Bearish signal.

## 🤖 AI-Powered Decision Making
The bot formulates decisions using OpenAI based on:
- RSI, VWAP, and moving averages.
- User-defined constraints (e.g., budget, stock exclusions, portfolio size).

### **Example AI Prompt**:
``````
**Context:**
Today is 2025-07-26T12:23:02Z.
You are a short-term investment advisor managing an Indian stock portfolio.
You analyze market conditions every 600 seconds and make investment decisions on NSE/BSE.
All prices are in INR (Indian Rupees).

**Constraints:**
- Initial budget: 50000.00 INR
- Max portfolio size: 10 stocks
- Sell Amounts Guidelines: Minimum amount 1.0 INR, Maximum amount 10.0 INR
- Buy Amounts Guidelines: Minimum amount 1.0 INR, Maximum amount 10.0 INR
- Excluded stocks: VOO, SPY, IVV

**Stock Data:**
```json
{
 "RELIANCE": {
  "current_price": 2450.50,
  "my_quantity": 10,
  "my_average_buy_price": 2380.00,
  "rsi": 45.2,
  "vwap": 2445.30,
  "50_day_mavg_price": 2420.00,
  "200_day_mavg_price": 2350.00
 },
 ...
}
```

**Response Format:**
Return your decisions in a JSON array with this structure:
```json
[
  {"symbol": <symbol>, "decision": <decision>, "quantity": <quantity>},
  ...
]
```
- <symbol>: Stock symbol (NSE trading symbol).
- <decision>: One of `buy`, `sell`, or `hold`.
- <quantity>: Recommended transaction quantity (integer, in units of shares).

**Instructions:**
- Provide only the JSON output with no additional text.
- Return an empty array if no actions are necessary.
``````

AI-response example:
```
[
    {"symbol": "RELIANCE", "decision": "sell", "quantity": 5},
    {"symbol": "TCS", "decision": "hold", "quantity": 0},
    {"symbol": "INFY", "decision": "buy", "quantity": 2},
    ...
]
```

## 📝 Logging System
The bot logs its activity and trading decisions in a console log.

### **Example Log Output**:
```
Are you sure you want to run the bot in auto mode? (yes/no): yes
[2025-07-26 11:06:58] [INFO]    Market is open, running trading bot in auto mode...
[2025-07-26 11:06:58] [INFO]    Getting account info...
[2025-07-26 11:07:02] [INFO]    Getting portfolio stocks...
[2025-07-26 11:07:02] [INFO]    Portfolio stocks to proceed: RELIANCE (45.12%), TCS (30.5%), ...
[2025-07-26 11:07:02] [INFO]    Prepare portfolio stocks for AI analysis...
[2025-07-26 11:07:07] [INFO]    Getting watchlist stocks...
[2025-07-26 11:07:08] [INFO]    Watchlist stocks to proceed: INFY, HDFCBANK, ICICIBANK, ...
[2025-07-26 11:07:08] [INFO]    Prepare watchlist overview for AI analysis...
[2025-07-26 11:07:09] [INFO]    Making AI-based decision...
[2025-07-26 11:07:21] [INFO]    Executing decisions...
[2025-07-26 11:07:21] [INFO]    RELIANCE > Decision: sell of 5
[2025-07-26 11:07:21] [INFO]    RELIANCE > Sold 5 stocks
[2025-07-26 11:07:21] [INFO]    INFY > Decision: buy of 2
[2025-07-26 11:07:23] [INFO]    INFY > Bought 2 stocks
[2025-07-26 11:07:24] [INFO]    Sold: RELIANCE (5)
[2025-07-26 11:07:24] [INFO]    Bought: INFY (2)
[2025-07-26 11:07:24] [INFO]    Errors: None
[2025-07-26 11:07:24] [INFO]    Waiting for 600 seconds...
```

## 🛠️ Setup Guide
### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/dhan-ai-trading-bot.git
    cd dhan-ai-trading-bot
    ```

2. Install dependencies (requires Python 3.10+):
    ```sh
    pip install -r requirements.txt
    ```

### Configuration
Copy the example config and update it with your details:
   ```sh
   cp config.py.example config.py
   ```

Fill in config.py with the required parameters:
```python
# Dhan API Credentials
DHAN_CLIENT_ID = ""                            # Dhan Client ID (from https://www.dhan.co)
DHAN_ACCESS_TOKEN = ""                         # Dhan Access Token

# OpenAI Credentials
OPENAI_API_KEY = "..."                         # OpenAI API key

# Basic config parameters
MODE = "demo"                                  # Trading mode (demo, auto, manual)
LOG_LEVEL = "INFO"                             # Log level (DEBUG, INFO)
RUN_INTERVAL_SECONDS = 600                     # Trading interval in seconds

# Dhan exchange and product settings
DHAN_EXCHANGE_SEGMENT = "NSE_EQ"               # Exchange segment (NSE_EQ, BSE_EQ, etc.)
DHAN_PRODUCT_TYPE = "CNC"                      # Product type (CNC = Delivery, INTRADAY)

# Dhan trading config parameters
TRADE_EXCEPTIONS = []                          # Stocks to exclude from trading
WATCHLIST_SYMBOLS = []                         # Stock symbols to watch (e.g. ["RELIANCE", "TCS"])

# Security ID Map: Maps ticker symbols to Dhan's numeric security IDs
SECURITY_ID_MAP = {
    # "RELIANCE": "1333",
    # "TCS": "11536",
    # "INFY": "1594",
}

# Trading limits (in INR)
MIN_SELLING_AMOUNT_USD = 1.0                   # Minimum sell amount in INR
MAX_SELLING_AMOUNT_USD = 10.0                  # Maximum sell amount in INR
MIN_BUYING_AMOUNT_USD = 1.0                    # Minimum buy amount in INR
MAX_BUYING_AMOUNT_USD = 10.0                   # Maximum buy amount in INR
PORTFOLIO_LIMIT = 10                           # Max stocks in portfolio
WATCHLIST_OVERVIEW_LIMIT = 5                   # Max watchlist stocks to analyze per run

# OpenAI config params
OPENAI_MODEL_NAME = "gpt-4o-mini"              # OpenAI model name
```

#### Dhan API Setup
1. Create a Dhan account at [dhan.co](https://www.dhan.co) if you don't have one.
2. Get your **Client ID** from the Dhan dashboard.
3. Generate an **Access Token** via Dhan's OAuth flow or PIN+TOTP method.
4. Find **Security IDs** for your stocks from the [Dhan Scrip Master CSV](https://images.dhan.co/api-data/api-scrip-master.csv).

### Running the Bot
Start the bot with:
   ```sh
   python main.py
   ```

## ⚠️ Disclaimer
Please note: This bot is designed solely for educational purposes.
Trading stocks involves significant risks, and you should only invest money you can afford to lose.
The author is not liable for any financial losses incurred through the use of this bot.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are highly encouraged and welcomed!
Whether you're looking to enhance the logging system, optimize AI-prompt strategies,
or enrich stock data — there's always room for fresh ideas and improvements.
Feel free to submit pull requests or open issues to share your suggestions and expertise!