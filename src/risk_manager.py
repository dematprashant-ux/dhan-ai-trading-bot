"""Advanced Risk Management Module"""
from typing import Dict, Any, Optional

import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.daily_loss = 0.0
        self.positions: Dict[str, int] = {}
    
    def evaluate_risk(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluates risk for a trading signal and returns position sizing
        
        Args:
            signal: Trading signal from strategy
            
        Returns:
            Position dictionary with symbol and quantity, or None if rejected
        """
        try:
            # 1. Check daily loss limit
            if self.daily_loss >= self.config['MAX_DAILY_LOSS']:
                logger.warning("Daily loss limit exceeded - rejecting trade")
                return None
            
            # 2. Validate symbol against exceptions
            if signal['symbol'] in self.config.get('TRADE_EXCEPTIONS', []):
                logger.warning(f"Trade rejected: {signal['symbol']} in exceptions list")
                return None
            
            # 3. Calculate position size based on risk percentage
            capital = self.config['ACCOUNT_BALANCE']
            risk_percent = self.config['RISK_PER_TRADE']
            max_loss = capital * risk_percent
            
            # 4. Determine quantity based on stop-loss
            price = signal['price']
            stop_loss = signal['stop_loss']
            quantity = int(max_loss / (price - stop_loss))
            
            # 5. Apply lot size constraints
            quantity = max(1, quantity // self.config['LOT_SIZE']) * self.config['LOT_SIZE']
            
            # 6. Check position limits
            current_quantity = self.positions.get(signal['symbol'], 0)
            if current_quantity + quantity > self.config['MAX_POSITION_SIZE']:
                logger.warning("Position limit exceeded")
                return None
            
            return {
                'symbol': signal['symbol'],
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': signal['take_profit']
            }
            
        except Exception as e:
            logger.error(f"Risk evaluation failed: {e}")
            return None
    
    def update_daily_loss(self, loss_amount: float):
        """Update daily realized loss"""
        self.daily_loss += loss_amount
        logger.info(f"Daily loss updated: {self.daily_loss:.2f}")
    
    def update_position(self, symbol: str, quantity: int):
        """Update current position holdings"""
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        logger.info(f"Position updated: {symbol} x {quantity}")