# core/market_engine.py

from canonical.messages import (
    CanonicalOrder,
    OrderAccepted,
    OrderRejected,
    TradeExecuted,
    OrderRested,
    Side,
)
from core.orderbook import OrderBook
from core.validator import CanonicalValidator
from core.risk_manager import RiskManager


class MarketEngine:

    def __init__(self):
        self.validator = CanonicalValidator()
        self.risk = RiskManager()

        # Separate orderbook per symbol
        self.orderbooks = {}

    # -------------------------------------------------
    # Main Entry Point
    # -------------------------------------------------
    def process_order(self, order: CanonicalOrder):

        events = []

        # -------------------------
        # 1️⃣ Validation
        # -------------------------
        try:
            self.validator.validate(order)
        except Exception as e:
            events.append(OrderRejected(order.order_id, str(e)))
            return events

        # -------------------------
        # 2️⃣ Risk Check
        # -------------------------
        if not self.risk.check(order):
            events.append(OrderRejected(order.order_id, "RISK_REJECT"))
            return events

        # Order accepted
        events.append(OrderAccepted(order.order_id))

        # -------------------------
        # 3️⃣ Get/Create OrderBook
        # -------------------------
        if order.symbol not in self.orderbooks:
            self.orderbooks[order.symbol] = OrderBook()

        book = self.orderbooks[order.symbol]

        # -------------------------
        # 4️⃣ Matching
        # -------------------------
        trades = book.match(order)

        for resting, qty, price in trades:

            # Aggressor = incoming order
            events.append(
                TradeExecuted(
                    aggressor_id=order.order_id,
                    resting_id=resting.order_id,
                    symbol=order.symbol,
                    price=price,
                    quantity=qty,
                )
            )

        # -------------------------
        # 5️⃣ If leftover → Rest
        # -------------------------
        if order.quantity > 0:
            book.add_order(order)
            events.append(OrderRested(order.order_id))

        # -------------------------
        # 6️⃣ Debug OrderBook Print
        # -------------------------
        self._print_orderbook(order.symbol)

        return events

    # -------------------------------------------------
    # Debug Print Function
    # -------------------------------------------------
    def _print_orderbook(self, symbol):

        book = self.orderbooks[symbol]

        print("\n📘 ORDER BOOK SNAPSHOT:", symbol)
        print("=" * 60)

        total_bid_qty = sum(order.quantity for order in book.buy_orders)
        total_ask_qty = sum(order.quantity for order in book.sell_orders)

        # -------------------------
        # BIDS
        # -------------------------
        print("BIDS:")
        if book.buy_orders:
            for order in book.buy_orders:
                print(f"  ({order.order_id}, {order.price}, {order.quantity})")
        else:
            print("  None")

        print(f"→ Total Bid Quantity: {total_bid_qty}")

        # -------------------------
        # ASKS
        # -------------------------
        print("\nASKS:")
        if book.sell_orders:
            for order in book.sell_orders:
                print(f"  ({order.order_id}, {order.price}, {order.quantity})")
        else:
            print("  None")

        print(f"→ Total Ask Quantity: {total_ask_qty}")

        # -------------------------
        # Total Liquidity
        # -------------------------
        print("\n📊 TOTAL LIQUIDITY FOR SYMBOL")
        print(f"Total Outstanding Volume: {total_bid_qty + total_ask_qty}")

        print("=" * 60)
