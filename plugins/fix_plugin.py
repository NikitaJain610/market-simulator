# plugins/fix_plugin.py

import simplefix
import datetime
from plugins.base import ProtocolPlugin
from plugins.fix_session_logic import FixSessionLogic

from canonical.messages import (
    OrderAccepted,
    OrderRejected,
    TradeExecuted,
)


class FixPlugin(ProtocolPlugin):

    def __init__(self):
        self.parser = simplefix.FixParser()
        self.sender_comp_id = None
        self.target_comp_id = None
        self.out_seq_num = 1

        self.exec_counter = 1
        self.exchange_order_id_counter = 1

        # clOrdID → state
        self.order_state = {}

    # --------------------------------------------------
    def create_session_logic(self):
        return FixSessionLogic()

    # --------------------------------------------------
    def decode(self, raw_bytes: bytes):
        self.parser.append_buffer(raw_bytes)
        msg = self.parser.get_message()

        if msg is not None:
            self.sender_comp_id = msg.get(49).decode().strip()
            self.target_comp_id = msg.get(56).decode().strip()

        return msg

    # --------------------------------------------------
    def map_to_canonical(self, msg):

        if msg is None:
            return None

        if msg.get(35).decode() != "D":
            return None

        cl_ord_id = msg.get(11).decode()
        order_qty = int(msg.get(38).decode())
        price = float(msg.get(44).decode())
        symbol = msg.get(55).decode()
        side_value = msg.get(54).decode()

        # Store original order state
        if cl_ord_id not in self.order_state:
            self.order_state[cl_ord_id] = {
                "order_id": f"EXCH{self.exchange_order_id_counter}",
                "order_qty": order_qty,
                "cum_qty": 0,
                "avg_px": 0.0,
                "symbol": symbol,
                "side": side_value,
                "price": price,
            }
            self.exchange_order_id_counter += 1

        from canonical.messages import CanonicalOrder, Side

        side = Side.BUY if side_value == "1" else Side.SELL

        return CanonicalOrder(
            order_id=cl_ord_id,
            side=side,
            symbol=symbol,
            price=price,
            quantity=order_qty,
        )

    # ==================================================
    # EVENT ENCODER ENTRY POINT
    # ==================================================
    def encode_event(self, event):

        if isinstance(event, OrderAccepted):
            return self._encode_new(event.order_id)

        if isinstance(event, OrderRejected):
            return self._encode_reject(event.order_id)

        if isinstance(event, TradeExecuted):
            return self._encode_trade(event)

        return None

    # ==================================================
    # FIX ENCODERS
    # ==================================================

    def _base_header(self, msg):

        sending_time = datetime.datetime.utcnow().strftime(
            "%Y%m%d-%H:%M:%S.%f"
        )[:-3]

        msg.append_pair(8, "FIX.4.4")
        msg.append_pair(35, "8")
        msg.append_pair(34, str(self.out_seq_num))
        msg.append_pair(49, self.target_comp_id)
        msg.append_pair(56, self.sender_comp_id)
        msg.append_pair(52, sending_time)

        return sending_time

    # --------------------------------------------------
    # NEW ORDER ACCEPTED
    # --------------------------------------------------
    def _encode_new(self, cl_ord_id):

        state = self.order_state[cl_ord_id]

        msg = simplefix.FixMessage()
        sending_time = self._base_header(msg)

        msg.append_pair(37, state["order_id"])
        msg.append_pair(17, f"EXEC{self.exec_counter}")
        msg.append_pair(11, cl_ord_id)
        msg.append_pair(150, "0")  # ExecType = NEW
        msg.append_pair(39, "0")   # OrdStatus = NEW
        msg.append_pair(55, state["symbol"])
        msg.append_pair(54, state["side"])
        msg.append_pair(38, state["order_qty"])
        msg.append_pair(44, state["price"])
        msg.append_pair(14, 0)  # CumQty
        msg.append_pair(151, state["order_qty"])  # LeavesQty
        msg.append_pair(6, 0)  # AvgPx
        msg.append_pair(60, sending_time)

        self.exec_counter += 1
        self.out_seq_num += 1

        return msg.encode()

    # --------------------------------------------------
    # ORDER REJECTED
    # --------------------------------------------------
    def _encode_reject(self, cl_ord_id):

        msg = simplefix.FixMessage()
        sending_time = self._base_header(msg)

        msg.append_pair(37, "NONE")
        msg.append_pair(17, f"EXEC{self.exec_counter}")
        msg.append_pair(11, cl_ord_id)
        msg.append_pair(150, "8")  # Rejected
        msg.append_pair(39, "8")
        msg.append_pair(60, sending_time)

        self.exec_counter += 1
        self.out_seq_num += 1

        return msg.encode()

    # --------------------------------------------------
    # TRADE EXECUTED
    # --------------------------------------------------
    def _encode_trade(self, event):

        cl_ord_id = event.aggressor_id
        state = self.order_state[cl_ord_id]

        state["cum_qty"] += event.quantity

        # Weighted average price
        total_value = state["avg_px"] * (state["cum_qty"] - event.quantity)
        total_value += event.quantity * event.price
        state["avg_px"] = total_value / state["cum_qty"]

        leaves_qty = state["order_qty"] - state["cum_qty"]

        if state["cum_qty"] < state["order_qty"]:
            ord_status = "1"  # Partial
        else:
            ord_status = "2"  # Filled

        msg = simplefix.FixMessage()
        sending_time = self._base_header(msg)

        msg.append_pair(37, state["order_id"])
        msg.append_pair(17, f"EXEC{self.exec_counter}")
        msg.append_pair(11, cl_ord_id)
        msg.append_pair(150, "F")  # Trade
        msg.append_pair(39, ord_status)
        msg.append_pair(55, state["symbol"])
        msg.append_pair(54, state["side"])
        msg.append_pair(38, state["order_qty"])
        msg.append_pair(44, state["price"])
        msg.append_pair(14, state["cum_qty"])
        msg.append_pair(151, leaves_qty)
        msg.append_pair(6, round(state["avg_px"], 4))
        msg.append_pair(32, event.quantity)
        msg.append_pair(31, event.price)
        msg.append_pair(60, sending_time)

        self.exec_counter += 1
        self.out_seq_num += 1

        return msg.encode()

    # --------------------------------------------------
    def encode_logon_ack(self):

        msg = simplefix.FixMessage()

        sending_time = datetime.datetime.utcnow().strftime(
            "%Y%m%d-%H:%M:%S.%f"
        )[:-3]

        msg.append_pair(8, "FIX.4.4")
        msg.append_pair(35, "A")
        msg.append_pair(34, str(self.out_seq_num))
        msg.append_pair(49, self.target_comp_id)
        msg.append_pair(56, self.sender_comp_id)
        msg.append_pair(52, sending_time)
        msg.append_pair(98, "0")
        msg.append_pair(108, "30")

        self.out_seq_num += 1

        return msg.encode()
