"""Type stubs for dhanhq SDK."""
from typing import Any, Dict, List, Optional, Union

class DhanContext:
    def __init__(self, client_id: str, access_token: str) -> None: ...
    def get_client_id(self) -> str: ...
    def get_access_token(self) -> str: ...
    def get_dhan_http(self) -> Any: ...
    def get_dhan_login(self) -> Any: ...

class dhanhq:
    # Constants
    BUY: str
    SELL: str
    NSE: str
    NSE_EQ: str
    BSE: str
    BSE_EQ: str
    MCX: str
    MCX_COMM: str
    INDEX: str
    IDX_I: str
    FNO: str
    NSE_FNO: str
    BSE_FNO: str
    EQ: str
    MARGIN: str
    CNC: str
    INTRADAY: str
    INTRA: str
    MTF: str
    DAY: str
    IOC: str
    MARKET: str
    LIMIT: str
    STOP_LOSS: str
    STOP_LOSS_MARKET: str
    SL: str
    SLM: str
    CO: str
    BO: str
    OTP_SENT: str

    # Class methods
    @classmethod
    def convert_to_date_time(cls, epoch: Union[int, float]) -> str: ...

    def __init__(self, client_id: str, access_token: str, disable_ssl: bool = False) -> None: ...

    # Order methods
    def place_order(
        self,
        security_id: str,
        exchange_segment: str,
        transaction_type: str,
        quantity: int,
        order_type: str,
        product_type: str,
        price: float,
        trigger_price: float = 0,
        disclosed_quantity: int = 0,
        after_market_order: bool = False,
        validity: str = "DAY",
        amo_time: str = "OPEN",
        bo_profit_value: Optional[float] = None,
        bo_stop_loss_Value: Optional[float] = None,
        tag: Optional[str] = None,
        should_slice: bool = False,
    ) -> Dict[str, Any]: ...

    def place_super_order(
        self,
        security_id: str,
        exchange_segment: str,
        transaction_type: str,
        quantity: int,
        order_type: str,
        product_type: str,
        price: float,
        trigger_price: float = 0,
        disclosed_quantity: int = 0,
        after_market_order: bool = False,
        validity: str = "DAY",
        amo_time: str = "OPEN",
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        trailing_delta: Optional[float] = None,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]: ...

    def place_forever(
        self,
        security_id: str,
        exchange_segment: str,
        transaction_type: str,
        quantity: int,
        order_type: str,
        product_type: str,
        price: float,
        trigger_price: float = 0,
        disclosed_quantity: int = 0,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]: ...

    def place_slice_order(
        self,
        security_id: str,
        exchange_segment: str,
        transaction_type: str,
        quantity: int,
        order_type: str,
        product_type: str,
        price: float,
        trigger_price: float = 0,
        disclosed_quantity: int = 0,
        after_market_order: bool = False,
        validity: str = "DAY",
        tag: Optional[str] = None,
    ) -> Dict[str, Any]: ...

    def modify_order(
        self,
        order_id: str,
        order_type: str,
        leg_name: str,
        quantity: int,
        price: float,
        trigger_price: float,
        disclosed_quantity: int,
        validity: str,
    ) -> Dict[str, Any]: ...

    def cancel_order(self, order_id: str) -> Dict[str, Any]: ...

    def modify_forever(self, order_id: str, order_type: str, price: float, trigger_price: float, quantity: int, disclosed_quantity: int, validity: str) -> Dict[str, Any]: ...
    def cancel_forever(self, order_id: str) -> Dict[str, Any]: ...
    def modify_super_order(self, order_id: str, leg_name: str, order_type: str, price: float, trigger_price: float, quantity: int, disclosed_quantity: int) -> Dict[str, Any]: ...

    # Portfolio methods
    def get_fund_limits(self) -> Dict[str, Any]: ...
    def get_positions(self) -> Dict[str, Any]: ...
    def get_holdings(self) -> Dict[str, Any]: ...
    def get_order_list(self) -> Dict[str, Any]: ...
    def get_super_order_list(self) -> Dict[str, Any]: ...
    def get_trade_book(self, order_id: Optional[str] = None) -> Dict[str, Any]: ...
    def get_order_by_id(self, order_id: str) -> Dict[str, Any]: ...
    def get_order_by_correlationID(self, correlation_id: str) -> Dict[str, Any]: ...
    def get_trade_history(self, txn_type: str, from_date: str, to_date: str, page: int = 0) -> Dict[str, Any]: ...

    # Market data methods
    def quote_data(self, securities: Dict[str, List[int]]) -> Dict[str, Any]: ...
    def ohlc_data(self, security_id: str, exchange_segment: str, instrument_type: str, from_date: str, to_date: str, interval: int = 1) -> Dict[str, Any]: ...
    def ticker_data(self, securities: Dict[str, List[int]]) -> Dict[str, Any]: ...
    def expired_options_data(self, securities: Dict[str, List[int]]) -> Dict[str, Any]: ...
    def option_chain(self, security_id: str, exchange_segment: str, instrument_type: str, strike_price: float) -> Dict[str, Any]: ...
    def expiry_list(self, exchange_segment: str, instrument_type: str) -> Dict[str, Any]: ...

    # Chart data methods
    def intraday_minute_data(
        self,
        security_id: str,
        exchange_segment: str,
        instrument_type: str,
        from_date: str,
        to_date: str,
        interval: int = 1,
        oi: bool = False,
    ) -> Dict[str, Any]: ...

    def historical_daily_data(
        self,
        security_id: str,
        exchange_segment: str,
        instrument_type: str,
        from_date: str,
        to_date: str,
        expiry_code: int = 0,
        oi: bool = False,
    ) -> Dict[str, Any]: ...

    # Position conversion
    def convert_position(
        self,
        security_id: str,
        exchange_segment: str,
        transaction_type: str,
        product_type: str,
        quantity: int,
    ) -> Dict[str, Any]: ...

    # Security
    def fetch_security_list(self, exchange_segment: str = "ALL", segment: str = "ALL", security_type: str = "ALL") -> Dict[str, Any]: ...

    # e-DIS
    def generate_tpin(self) -> Dict[str, Any]: ...
    def edis_inquiry(self, inquiry_type: str, bo_order_id: Optional[str] = None, exchange_segment: Optional[str] = None, security_id: Optional[str] = None) -> Dict[str, Any]: ...
    def open_browser_for_tpin(self) -> None: ...

    # Kill switch
    def kill_switch(self, status: int) -> Dict[str, Any]: ...
    def status_kill_switch(self) -> Dict[str, Any]: ...

    # Ledger
    def ledger_report(self, from_date: str, to_date: str) -> Dict[str, Any]: ...

    # Margin calculator
    def margin_calculator(self, params: Dict[str, Any]) -> Dict[str, Any]: ...