# core/risk_manager.py

class RiskManager:

    def __init__(self, max_position=1000):
        self.positions = {}
        self.max_position = max_position

    def check(self, order):

        current = self.positions.get(order.order_id, 0)

        if order.side == "BUY":
            projected = current + order.quantity
        else:
            projected = current - order.quantity

        if abs(projected) > self.max_position:
            return False

        return True

    def update(self, execution):

        # Simplified position tracking
        self.positions[execution.buy_order_id] = (
            self.positions.get(execution.buy_order_id, 0)
            + execution.quantity
        )
