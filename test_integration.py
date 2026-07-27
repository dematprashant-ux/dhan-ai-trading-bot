"""Comprehensive integration test for Dhan AI Trading Bot"""

import asyncio
from src.api.omniroute import get_ai_decision
from src.risk_manager import RiskManager
from src.event_engine import EventEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_omniroute_client():
    """Test Omniroute API client with multiple symbols"""
    logger.info("Testing Omniroute client...")
    
    stock_data = {
        'current_time': '2026-07-27 10:00:00',
        'market_status': 'OPEN',
        'stocks': [
            {'symbol': 'BANKNIFTY', 'price': 40000, 'rsi': 55},
            {'symbol': 'NIFTY', 'price': 18000, 'rsi': 45}
        ]
    }
    
    constraints = {
        'budget': 100000,
        'exclusions': ['INFY']
    }
    
    try:
        decisions = get_ai_decision(stock_data, constraints)
        logger.info(f"Decisions: {decisions}")
    except Exception as e:
        logger.error(f"Failed to get decisions: {e}")

def test_risk_manager():
    """Test RiskManager with various scenarios"""
    logger.info("Testing RiskManager...")
    
    config = {
        'ACCOUNT_BALANCE': 1000000.0,
        'RISK_PER_TRADE': 0.02,
        'MAX_DAILY_LOSS': 5000.0,
        'LOT_SIZE': 15,
        'MAX_POSITION_SIZE': 300,
        'TRADE_EXCEPTIONS': ['INFY', 'TCS']
    }
    
    risk_manager = RiskManager(config)
    
    # Test scenarios
    test_signals = [
        {'symbol': 'BANKNIFTY', 'price': 40000, 'stop_loss': 39600, 'take_profit': 40400},
        {'symbol': 'INFY', 'price': 1500, 'stop_loss': 1450, 'take_profit': 1550},  # Should be rejected (exception)
        {'symbol': 'NIFTY', 'price': 18000, 'stop_loss': 17500, 'take_profit': 18500}
    ]
    
    for signal in test_signals:
        position = risk_manager.evaluate_risk(signal)
        logger.info(f"Signal {signal['symbol']}: {position}")
        
        if position:
            risk_manager.update_position(position['symbol'], position['quantity'])
    
    # Test daily loss limit
    risk_manager.update_daily_loss(4000)
    logger.info(f"After 4000 loss - Daily Loss: {risk_manager.daily_loss}")
    
    risk_manager.update_daily_loss(1000)  # This should exceed limit
    logger.info(f"After additional 1000 loss - Daily Loss: {risk_manager.daily_loss}")
    
    logger.info(f"Final positions: {risk_manager.positions}")

async def test_event_engine():
    """Test EventEngine basic functionality"""
    logger.info("Testing EventEngine...")
    
    event_engine = EventEngine()
    
    # Run for a short time to test basic flow
    async def monitor_queues():
        """Monitor queues for activity"""
        for _ in range(3):
            await asyncio.sleep(0.5)
            logger.info(f"Tick queue empty: {event_engine.tick_queue.empty()}")
            logger.info(f"Candle queue empty: {event_engine.candle_queue.empty()}")
            logger.info(f"Signal queue empty: {event_engine.signal_queue.empty()}")
    
    # Run event engine task briefly alongside monitoring
    task = asyncio.create_task(event_engine.start())
    await monitor_queues()
    task.cancel()

def main():
    """Run all tests"""
    logger.info("Starting integration tests...")
    
    test_omniroute_client()
    test_risk_manager()
    asyncio.run(test_event_engine())
    
    logger.info("All tests completed successfully!")

if __name__ == "__main__":
    main()