from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class OrderLeg:
    symbol: str
    instruction: str
    quantity: float


@dataclass(slots=True)
class Order:
    order_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str
    status: str
    price: float
    time_in_force: str
    legs: List[OrderLeg] = field(default_factory=list)