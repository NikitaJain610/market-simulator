# core/market_engine.py

from canonical.messages import CanonicalExecution, Side
from core.orderbook import OrderBook
from core.validator import CanonicalValidator
from core.risk_manager import RiskManager


class MarketEngine:

    def __init__(self):
        self.validator = CanonicalValidator()
        self.risk = RiskManager()
        self.orderbooks = {}  # symbol → OrderBook

    # -------------------------------------------------
    def process_order(self, order):

        # -------------------------
        # 1️⃣ Validation
        # -------------------------
        self.validator.validate(order)

        # -------------------------
        # 2️⃣ Risk Check
        # -------------------------
        if not self.risk.check(order):
            print("❌ Risk Rejected Order")

            return CanonicalExecution(
                buy_order_id=order.order_id,
                sell_order_id="RISK_REJECT",
                price=order.price,
                quantity=0,
            )

        # -------------------------
        # 3️⃣ Get Symbol Book
        # -------------------------
        if order.symbol not in self.orderbooks:
            self.orderbooks[order.symbol] = OrderBook()

        book = self.orderbooks[order.symbol]

        # -------------------------
        # 4️⃣ Matching
        # -------------------------
        trades = book.match(order)

        if trades:
            resting, traded_qty, traded_price = trades[0]

            execution = CanonicalExecution(
                buy_order_id=order.order_id
                if order.side == Side.BUY
                else resting.order_id,
                sell_order_id=resting.order_id
                if order.side == Side.BUY
                else order.order_id,
                price=traded_price,
                quantity=traded_qty,
            )

            self.risk.update(execution)

            print(f"✅ Trade Executed on {order.symbol}")
            self._print_orderbook(order.symbol)

            return execution

        # -------------------------
        # 5️⃣ Add To Book
        # -------------------------
        book.add_order(order)

        print(f"📥 Order Added To Book ({order.symbol})")
        self._print_orderbook(order.symbol)

        return CanonicalExecution(
            buy_order_id=order.order_id,
            sell_order_id="BOOKED",
            price=order.price,
            quantity=0,
        )

    # -------------------------------------------------
    def get_orderbook_snapshot(self, symbol):
        if symbol in self.orderbooks:
            return self.orderbooks[symbol].snapshot()
        return {"bids": [], "asks": []}

    # -------------------------------------------------
    def _print_orderbook(self, symbol):

        snapshot = self.get_orderbook_snapshot(symbol)

        print(f"\n📘 ORDER BOOK SNAPSHOT ({symbol})")
        print("BIDS:")
        for bid in snapshot["bids"]:
            print(f"  {bid}")

        print("ASKS:")
        for ask in snapshot["asks"]:
            print(f"  {ask}")

        print("-" * 50)
