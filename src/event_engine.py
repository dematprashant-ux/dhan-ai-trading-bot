"""Async event processing engine for decoupled trading components"""
import asyncio
from asyncio import Queue
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class EventEngine:
    def __init__(self):
        self.tick_queue: Queue = Queue()
        self.candle_queue: Queue = Queue()
        self.signal_queue: Queue = Queue()
        self.position_queue: Queue = Queue()
        
        self.producers: Dict[str, Callable] = {
            'market_feed': self._produce_ticks,
            'candle_builder': self._produce_candles,
            'strategy': self._produce_signals
        }
        
        self.consumers: Dict[str, Callable] = {
            'candle_builder': self._consume_ticks,
            'strategy': self._consume_candles,
            'risk_manager': self._consume_signals,
            'order_executor': self._consume_positions
        }
    
    async def start(self):
        """Start all event processing tasks"""
        tasks = [
            self._run_producer('market_feed'),
            self._run_producer('candle_builder'),
            self._run_producer('strategy'),
            self._run_consumer('candle_builder'),
            self._run_consumer('strategy'),
            self._run_consumer('risk_manager'),
            self._run_consumer('order_executor')
        ]
        await asyncio.gather(*tasks)
    
    async def _run_producer(self, producer_name: str):
        """Run a data producer task"""
        producer = self.producers[producer_name]
        while True:
            try:
                await producer()
                await asyncio.sleep(0.1)  # Prevent CPU overload
            except Exception as e:
                logger.error(f"Producer {producer_name} failed: {e}")
                await asyncio.sleep(1)
    
    async def _run_consumer(self, consumer_name: str):
        """Run a data consumer task"""
        consumer = self.consumers[consumer_name]
        while True:
            try:
                await consumer()
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Consumer {consumer_name} failed: {e}")
                await asyncio.sleep(1)
    
    # Producer methods
    async def _produce_ticks(self):
        """Simulated tick producer (replace with WebSocket integration)"""
        # In production: market_feed.get_next_tick()
        self.tick_queue.put_nowait({'timestamp': datetime.now(), 'price': 100.0})
    
    async def _produce_candles(self):
        """Candle builder producer"""
        while not self.tick_queue.empty():
            tick = await self.tick_queue.get()
            # Candle building logic here
            candle = {'open': tick['price'], 'close': tick['price']}
            self.candle_queue.put_nowait(candle)
            self.tick_queue.task_done()
    
    async def _produce_signals(self):
        """Strategy signal producer"""
        while not self.candle_queue.empty():
            candle = await self.candle_queue.get()
            # Strategy logic here
            signal = {'symbol': 'BANKNIFTY', 'decision': 'buy'}
            self.signal_queue.put_nowait(signal)
            self.candle_queue.task_done()
    
    # Consumer methods
    async def _consume_ticks(self):
        """Candle builder consumer"""
        # Implemented in candle_builder module
    
    async def _consume_candles(self):
        """Strategy consumer"""
        # Implemented in strategy module
    
    async def _consume_signals(self):
        """Risk manager consumer"""
        while not self.signal_queue.empty():
            signal = await self.signal_queue.get()
            # Risk management logic here
            position = {'symbol': signal['symbol'], 'quantity': 1}
            self.position_queue.put_nowait(position)
            self.signal_queue.task_done()
    
    async def _consume_positions(self):
        """Order executor consumer"""
        while not self.position_queue.empty():
            position = await self.position_queue.get()
            # Order execution logic here
            logger.info(f"Executing {position}")
            self.position_queue.task_done()