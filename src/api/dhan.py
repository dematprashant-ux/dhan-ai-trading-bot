from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from pytz import timezone

from dhanhq import DhanContext
from dhanhq import dhanhq as DhanHQ

from ..utils import logger
from config import (
    MODE, DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN,
    DHAN_EXCHANGE_SEGMENT, DHAN_PRODUCT_TYPE,
    WATCHLIST_SYMBOLS, SECURITY_ID_MAP,
)

# Dhan product type strings (used directly in API payloads)
# SDK place_order sends .upper() on these values
DHAN_PRODUCT_CNC: str = 'CNC'
DHAN_PRODUCT_INTRADAY: str = 'INTRADAY'
DHAN_PRODUCT_MTF: str = 'MTF'


# Initialize Dhan client
_client: Optional[DhanHQ] = None


def get_product_type() -> str:
    """Get the Dhan product type string from config."""
    pt: str = DHAN_PRODUCT_TYPE.upper() if DHAN_PRODUCT_TYPE else 'CNC'
    valid_types: set[str] = {DHAN_PRODUCT_CNC, DHAN_PRODUCT_INTRADAY, DHAN_PRODUCT_MTF}
    if pt not in valid_types:
        logger.warning(f"Unknown product type '{pt}', defaulting to CNC")
        return DHAN_PRODUCT_CNC
    return pt


def get_client() -> DhanHQ:
    """Get or create the Dhan API client."""
    global _client
    if _client is None:
        context: DhanContext = DhanContext(
            client_id=DHAN_CLIENT_ID,
            access_token=DHAN_ACCESS_TOKEN,
        )
        _client = DhanHQ(context)
    return _client


# Run a Dhan function with retries and delay between attempts (to handle rate limits)
def dhan_run_with_retries(func: Any, *args: Any, max_retries: int = 3, delay: int = 10, **kwargs: Any) -> Any:
    for attempt in range(max_retries):
        result: Any = func(*args, **kwargs)
        msg: str = f"Function: {func.__name__}, Parameters: {args}, Attempt: {attempt + 1}/{max_retries}"
        logger.debug(msg)
        if result is not None:
            # Check if the response indicates success
            status: Optional[str] = result.get('status') if isinstance(result, dict) else None
            if status == 'success' or status is None:
                return result
            # Status is 'failure' — retry unless it's the last attempt
            if attempt < max_retries - 1:
                logger.warning(f"Function: {func.__name__} returned failure status, retrying...")
                time.sleep(delay)
                continue
            # Last attempt, return whatever we got
            return result
        logger.debug(f"Function: {func.__name__}, Parameters: {args}, Retrying in {delay} seconds...")
        time.sleep(delay)
    return None


# Check if the Indian market is open (NSE/BSE: 9:15 AM - 3:30 PM IST)
def is_market_open() -> bool:
    ist = timezone('Asia/Kolkata')
    now: datetime = datetime.now(ist)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    market_open: datetime = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close: datetime = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


# Round money (INR)
def round_money(price: Any, decimals: int = 2) -> Optional[float]:
    if price is None:
        return None
    return round(float(price), decimals)


# Round quantity
def round_quantity(quantity: Any, decimals: int = 0) -> Optional[int]:
    if quantity is None:
        return None
    # Dhan requires integer quantities for equity
    return int(float(quantity))


# Resolve stock symbol to Dhan security_id
def resolve_security_id(symbol: str) -> Optional[str]:
    """Map a stock ticker symbol to Dhan's numeric security ID."""
    if symbol in SECURITY_ID_MAP:
        return str(SECURITY_ID_MAP[symbol])
    logger.warning(f"No security ID mapping found for {symbol}")
    return None


# Get today's date string in YYYY-MM-DD format
def get_today_str() -> str:
    return datetime.now().strftime('%Y-%m-%d')


# Get date N days ago
def get_date_days_ago(days: int) -> str:
    return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')


# Extract data from portfolio holdings (Dhan format)
def extract_my_stocks_data(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant data from Dhan holding entry.
    Dhan holding fields: securityId, tradingSymbol, netQuantity, averagePrice, ltp, etc.
    """
    return {
        "current_price": round_money(stock_data.get('ltp', 0)),
        "my_quantity": round_quantity(stock_data.get('netQuantity', 0)),
        "my_average_buy_price": round_money(stock_data.get('averagePrice', 0)),
    }


# Extract data from watchlist stocks
def extract_watchlist_data(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "current_price": round_money(stock_data.get('ltp', 0)),
        "my_quantity": round_quantity(0),
        "my_average_buy_price": round_money(0),
    }


# Extract sell response data
def extract_sell_response_data(order_resp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "quantity": round_quantity(order_resp.get('quantity', 0)),
        "price": round_money(order_resp.get('averageTradedPrice', 0)),
    }


# Extract buy response data
def extract_buy_response_data(order_resp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "quantity": round_quantity(order_resp.get('quantity', 0)),
        "price": round_money(order_resp.get('averageTradedPrice', 0)),
    }


# Enrich stock data with Relative Strength Index (RSI)
def enrich_with_rsi(stock_data: Dict[str, Any], historical_data: Optional[List[Dict[str, Any]]], symbol: str) -> Dict[str, Any]:
    if historical_data is None or len(historical_data) < 14:
        logger.debug(f"Not enough data to calculate RSI for {symbol}")
        return stock_data

    prices: List[Optional[float]] = [round_money(day.get('close', day.get('close_price', 0))) for day in historical_data]
    prices = [p for p in prices if p is not None]
    if len(prices) < 14:
        logger.debug(f"Not enough valid prices to calculate RSI for {symbol}")
        return stock_data

    delta: pd.Series = pd.Series(prices).diff()
    gain: pd.Series = delta.where(delta > 0, 0)
    loss: pd.Series = -delta.where(delta < 0, 0)
    avg_gain = float(gain.rolling(window=14).mean().iloc[-1])
    avg_loss = float(loss.rolling(window=14).mean().iloc[-1])
    if avg_loss == 0:
        rs: float = 100
    else:
        rs = avg_gain / avg_loss
    rsi: float = 100 - (100 / (1 + rs))
    stock_data["rsi"] = round(float(rsi), 2)
    return stock_data


# Enrich stock data with Volume-Weighted Average Price (VWAP)
def enrich_with_vwap(stock_data: Dict[str, Any], historical_data: Optional[List[Dict[str, Any]]], symbol: str) -> Dict[str, Any]:
    if historical_data is None or len(historical_data) < 1:
        logger.debug(f"Not enough data to calculate VWAP for {symbol}")
        return stock_data

    stock_history_df: pd.DataFrame = pd.DataFrame(historical_data)

    # Dhan historical data uses 'open', 'high', 'low', 'close', 'volume' keys
    close_col: str = 'close' if 'close' in stock_history_df.columns else 'close_price'
    high_col: str = 'high' if 'high' in stock_history_df.columns else 'high_price'
    low_col: str = 'low' if 'low' in stock_history_df.columns else 'low_price'

    stock_history_df[close_col] = pd.to_numeric(stock_history_df[close_col], errors="coerce")
    stock_history_df[high_col] = pd.to_numeric(stock_history_df[high_col], errors="coerce")
    stock_history_df[low_col] = pd.to_numeric(stock_history_df[low_col], errors="coerce")
    stock_history_df["volume"] = pd.to_numeric(stock_history_df["volume"], errors="coerce")

    # Drop rows where volume is zero or NaN
    stock_history_df = stock_history_df[stock_history_df["volume"] > 0]

    # Compute the Typical Price
    stock_history_df["typical_price"] = (
        stock_history_df[high_col] + stock_history_df[low_col] + stock_history_df[close_col]
    ) / 3

    # Compute VWAP
    sum_of_volumes: float = stock_history_df["volume"].sum()
    dot_product: float = stock_history_df["volume"].dot(stock_history_df["typical_price"])

    if sum_of_volumes == 0:
        logger.debug(f"Total volume is zero for {symbol}, cannot compute VWAP")
        return stock_data

    vwap: float = dot_product / sum_of_volumes
    stock_data["vwap"] = round_money(vwap)
    return stock_data


# Enrich stock data with Moving Averages (MA)
def enrich_with_moving_averages(stock_data: Dict[str, Any], historical_data: Optional[List[Dict[str, Any]]], symbol: str) -> Dict[str, Any]:
    if historical_data is None or len(historical_data) < 200:
        logger.debug(f"Not enough data to calculate moving averages for {symbol} (have {len(historical_data) if historical_data else 0} days)")
        return stock_data

    close_col: str = 'close' if isinstance(historical_data[0], dict) and 'close' in historical_data[0] else 'close_price'
    prices: List[Optional[float]] = [round_money(day.get(close_col, 0)) for day in historical_data]
    prices = [p for p in prices if p is not None]
    if len(prices) < 200:
        logger.debug(f"Not enough valid prices for moving averages for {symbol}")
        return stock_data

    moving_avg_50: float = pd.Series(prices).rolling(window=50).mean().iloc[-1]
    moving_avg_200: float = pd.Series(prices).rolling(window=200).mean().iloc[-1]
    stock_data["50_day_mavg_price"] = round_money(moving_avg_50)
    stock_data["200_day_mavg_price"] = round_money(moving_avg_200)
    return stock_data


# Get account info (buying power / available funds)
def get_account_info() -> Dict[str, Any]:
    client: DhanHQ = get_client()
    resp: Any = dhan_run_with_retries(client.get_fund_limits)
    if resp is None or resp.get('status') != 'success':
        raise Exception(f"Error getting fund limits: {resp}")

    data: Dict[str, Any] = resp.get('data', {})
    # Dhan fund limits response: availableMargin is in paise (1/100 INR)
    # but may also be returned in INR depending on API version
    available_margin: float = float(data.get('availableMargin', 0))
    # If value looks like paise (very large), convert to INR
    if available_margin > 100000:  # More than 1 lakh paise = 1000 INR threshold
        available_margin = available_margin / 100
    return {
        "buying_power": round_money(available_margin),
        "data": data,
    }


# Get portfolio stocks (holdings)
def get_portfolio_stocks() -> Dict[str, Any]:
    """
    Get current holdings from Dhan.
    Returns a dict keyed by trading symbol with holding details.
    """
    client: DhanHQ = get_client()
    resp: Any = dhan_run_with_retries(client.get_holdings)
    if resp is None or resp.get('status') != 'success':
        raise Exception(f"Error getting holdings: {resp}")

    holdings: List[Dict[str, Any]] = resp.get('data', [])
    portfolio: Dict[str, Any] = {}
    for holding in holdings:
        symbol: str = holding.get('tradingSymbol', '')
        if symbol:
            portfolio[symbol] = holding
    return portfolio


# Get watchlist stocks (from configured security ID list)
def get_watchlist_stocks() -> List[Dict[str, str]]:
    """
    Get watchlist stocks based on configured SECURITY_ID_MAP.
    Returns a list of dicts with 'symbol' and 'securityId'.
    """
    watchlist: List[Dict[str, str]] = []
    for symbol in WATCHLIST_SYMBOLS:
        security_id: Optional[str] = resolve_security_id(symbol)
        if security_id:
            watchlist.append({
                'symbol': symbol,
                'securityId': security_id,
            })
    return watchlist


# Get historical intraday data (minute candles)
def get_intraday_data(symbol: str, interval: int = 5) -> List[Dict[str, Any]]:
    """
    Get intraday minute candle data for the last trading day.
    interval: 1, 5, 15, 25, or 60 minutes
    """
    security_id: Optional[str] = resolve_security_id(symbol)
    if not security_id:
        return []

    client: DhanHQ = get_client()
    exchange: str = DHAN_EXCHANGE_SEGMENT
    from_date: str = get_date_days_ago(7)  # Get last 7 days to ensure we have data
    to_date: str = get_today_str()

    resp: Any = dhan_run_with_retries(
        client.intraday_minute_data,
        security_id, exchange, 'EQ', from_date, to_date, interval=interval
    )
    if resp is None or resp.get('status') != 'success':
        logger.warning(f"Error getting intraday data for {symbol}: {resp}")
        return []

    # Dhan charts API returns: {"open": [...], "high": [...], "low": [...], "close": [...], "volume": [...], "startUnix": [...]}
    # SDK wraps this as: {'status': 'success', 'data': <raw_api_response>}
    candles: Any = resp.get('data', {})
    if not isinstance(candles, dict):
        return []

    return _parse_chart_data(candles)


# Get historical daily data
def get_historical_data_daily(symbol: str, days: int = 365) -> List[Dict[str, Any]]:
    """
    Get daily candle data for the specified number of days.
    """
    security_id: Optional[str] = resolve_security_id(symbol)
    if not security_id:
        return []

    client: DhanHQ = get_client()
    exchange: str = DHAN_EXCHANGE_SEGMENT
    from_date: str = get_date_days_ago(days)
    to_date: str = get_today_str()

    resp: Any = dhan_run_with_retries(
        client.historical_daily_data,
        security_id, exchange, 'EQ', from_date, to_date
    )
    if resp is None or resp.get('status') != 'success':
        logger.warning(f"Error getting daily data for {symbol}: {resp}")
        return []

    candles: Any = resp.get('data', {})
    if not isinstance(candles, dict):
        return []

    return _parse_chart_data(candles)


def _parse_chart_data(candles: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse Dhan chart API response into list of OHLCV dicts.
    Dhan API returns: {"open": [...], "high": [...], "low": [...], "close": [...], "volume": [...], "startUnix": [...]}
    """
    result: List[Dict[str, Any]] = []
    opens: List[Any] = candles.get('open', [])
    highs: List[Any] = candles.get('high', [])
    lows: List[Any] = candles.get('low', [])
    closes: List[Any] = candles.get('close', [])
    volumes: List[Any] = candles.get('volume', [])
    count: int = len(closes)  # Use close length as the canonical count

    for i in range(count):
        result.append({
            'close_price': closes[i] if i < len(closes) else 0,
            'open_price': opens[i] if i < len(opens) else 0,
            'high_price': highs[i] if i < len(highs) else 0,
            'low_price': lows[i] if i < len(lows) else 0,
            'volume': volumes[i] if i < len(volumes) else 0,
        })
    return result


# Get current quote/price for a stock
def get_stock_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """Get current market quote for a stock using the SDK's quote_data method."""
    security_id: Optional[str] = resolve_security_id(symbol)
    if not security_id:
        return None

    client: DhanHQ = get_client()
    try:
        # quote_data expects: {"NSE_EQ": [11536]} format
        securities: Dict[str, List[int]] = {DHAN_EXCHANGE_SEGMENT: [int(security_id)]}
        resp: Any = client.quote_data(securities)
        if resp and resp.get('status') == 'success':
            return resp.get('data', {})
    except Exception as e:
        logger.warning(f"Error getting quote for {symbol}: {e}")
    return None


# Place a sell order
def sell_stock(symbol: str, quantity: int) -> Dict[str, Any]:
    if MODE == "demo":
        return {"id": "demo"}

    if MODE == "manual":
        confirm: str = input(f"Confirm sell for {symbol} of {quantity}? (yes/no): ")
        if confirm.lower() != "yes":
            return {"id": "cancelled"}

    security_id: Optional[str] = resolve_security_id(symbol)
    if not security_id:
        raise Exception(f"Cannot resolve security ID for {symbol}")

    client: DhanHQ = get_client()

    product_type: str = get_product_type()

    resp: Any = dhan_run_with_retries(
        client.place_order,
        security_id=security_id,
        exchange_segment=DHAN_EXCHANGE_SEGMENT,
        transaction_type=DhanHQ.SELL,
        quantity=int(quantity),
        order_type=DhanHQ.MARKET,
        product_type=product_type,
        price=0,  # Market order, price 0
        validity=DhanHQ.DAY,
    )
    if resp is None:
        raise Exception(f"Error selling {symbol}: No response")

    if resp.get('status') != 'success':
        raise Exception(f"Error selling {symbol}: {resp}")

    order_data: Dict[str, Any] = resp.get('data', {})
    return {
        'id': order_data.get('orderId', 'unknown'),
        'quantity': quantity,
        'price': order_data.get('averageTradedPrice', 0),
    }


# Place a buy order
def buy_stock(symbol: str, quantity: int) -> Dict[str, Any]:
    if MODE == "demo":
        return {"id": "demo"}

    if MODE == "manual":
        confirm: str = input(f"Confirm buy for {symbol} of {quantity}? (yes/no): ")
        if confirm.lower() != "yes":
            return {"id": "cancelled"}

    security_id: Optional[str] = resolve_security_id(symbol)
    if not security_id:
        raise Exception(f"Cannot resolve security ID for {symbol}")

    client: DhanHQ = get_client()
    product_type: str = get_product_type()

    resp: Any = dhan_run_with_retries(
        client.place_order,
        security_id=security_id,
        exchange_segment=DHAN_EXCHANGE_SEGMENT,
        transaction_type=DhanHQ.BUY,
        quantity=int(quantity),
        order_type=DhanHQ.MARKET,
        product_type=product_type,
        price=0,  # Market order, price 0
        validity=DhanHQ.DAY,
    )
    if resp is None:
        raise Exception(f"Error buying {symbol}: No response")

    if resp.get('status') != 'success':
        raise Exception(f"Error buying {symbol}: {resp}")

    order_data: Dict[str, Any] = resp.get('data', {})
    return {
        'id': order_data.get('orderId', 'unknown'),
        'quantity': quantity,
        'price': order_data.get('averageTradedPrice', 0),
    }