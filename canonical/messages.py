# canonical/messages.py

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# ---------------------------
# Canonical Order
# ---------------------------

@dataclass
class CanonicalOrder:
    order_id: str
    side: Side
    symbol: str
    price: float
    quantity: int


# ---------------------------
# Domain Events (API Agnostic)
# ---------------------------

@dataclass
class OrderAccepted:
    order_id: str


@dataclass
class OrderRejected:
    order_id: str
    reason: str


@dataclass
class TradeExecuted:
    aggressor_id: str
    resting_id: str
    symbol: str
    price: float
    quantity: int


@dataclass
class OrderRested:
    order_id: str
