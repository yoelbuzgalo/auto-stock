from dataclasses import dataclass


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: float
    average_price: float
    market_value: float


@dataclass(slots=True)
class Account:
    account_id: str
    account_type: str
    cash_balance: float
    buying_power: float
    equity: float