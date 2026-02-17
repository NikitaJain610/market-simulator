# core/orderbook.py

from canonical.messages import CanonicalOrder, Side


class OrderBook:

    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

    def match(self, incoming: CanonicalOrder):

        trades = []

        if incoming.side == Side.BUY:
            opposite = self.sell_orders
        else:
            opposite = self.buy_orders

        remaining_qty = incoming.quantity

        for resting in list(opposite):

            if remaining_qty <= 0:
                break

            # Simple price crossing logic
            if incoming.side == Side.BUY and incoming.price < resting.price:
                continue

            if incoming.side == Side.SELL and incoming.price > resting.price:
                continue

            traded_qty = min(remaining_qty, resting.quantity)

            trades.append((resting, traded_qty, resting.price))

            remaining_qty -= traded_qty
            resting.quantity -= traded_qty

            if resting.quantity == 0:
                opposite.remove(resting)

        incoming.quantity = remaining_qty

        return trades
    def snapshot(self):
        return {
            "bids": [(o.order_id, o.price, o.quantity) for o in self.buy_orders],
            "asks": [(o.order_id, o.price, o.quantity) for o in self.sell_orders],
        }


    def add_order(self, order: CanonicalOrder):

        if order.side == Side.BUY:
            self.buy_orders.append(order)
            self.buy_orders.sort(key=lambda x: -x.price)
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(key=lambda x: x.price)
