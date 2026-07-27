"""Omniroute API Client for AI Decision Making"""
import os
from typing import Dict, List, Any
import requests
import json
import logging

logger = logging.getLogger(__name__)

try:
    from config import OMNIROUTE_API_KEY, OMNIROUTE_MODEL
except ImportError:
    OMNIROUTE_API_KEY = os.environ.get("OMNIROUTE_API_KEY")
    OMNIROUTE_MODEL = os.environ.get("OMNIROUTE_MODEL", "command-r")

OMNIROUTE_API_URL = "https://api.omniroute.ai/v1/chat/completions"

def get_ai_decision(stock_data: Dict[str, Any], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetches trading decisions from Omniroute API.
    
    Args:
        stock_data: Dictionary containing stock metrics (RSI, VWAP, MA, etc.)
        constraints: User-defined trading constraints (budget, exclusions, etc.)
    
    Returns:
        List of decision dictionaries in the format:
        [{"symbol": "RELIANCE", "decision": "buy", "quantity": 5}, ...]
    """
    if not OMNIROUTE_API_KEY:
        logger.error("OMNIROUTE_API_KEY not configured in config.py")
        return []

    # Format prompt similar to OpenAI version
    prompt = f"""
    You are an AI stock trading advisor for Indian markets (NSE/BSE).
    Analyze the following stock data and generate trading decisions based on technical indicators and user constraints.

    **Context**:
    - Current time: {stock_data['current_time']}
    - Market status: {stock_data['market_status']}
    - All prices in INR

    **Constraints**:
    {json.dumps(constraints, indent=2)}

    **Stock Data**:
    {json.dumps(stock_data['stocks'], indent=2)}

    **Response Format**:
    Return ONLY a JSON array of decisions in this exact format:
    [
        {{
            "symbol": "<NSE_SYMBOL>",
            "decision": "buy|sell|hold",
            "quantity": <integer_units>
        }}
    ]
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OMNIROUTE_API_KEY}"
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(
            OMNIROUTE_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract decisions from response
        choices = result.get('choices', [])
        if not choices:
            return []
            
        raw_content = choices[0]['message']['content']
        return json.loads(raw_content)
        
    except Exception as e:
        logger.error(f"Omniroute API error: {str(e)}")
        return []