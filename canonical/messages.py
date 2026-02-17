# canonical/messages.py

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class CanonicalOrder:
    order_id: str
    side: Side
    symbol: str
    price: float
    quantity: int



@dataclass
class CanonicalExecution:
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int
