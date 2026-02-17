# plugins/fix_plugin.py
# ki
import simplefix
import datetime
from canonical.messages import CanonicalOrder, Side
from plugins.base import ProtocolPlugin
from plugins.fix_session_logic import FixSessionLogic


class FixPlugin(ProtocolPlugin):

    def __init__(self):
        self.parser = simplefix.FixParser()
        self.sender_comp_id = None
        self.target_comp_id = None
        self.out_seq_num = 1

    # ---------------------------------
    # Session Logic
    # ---------------------------------
    def create_session_logic(self):
        return FixSessionLogic()

    # ---------------------------------
    # Decode Incoming FIX Message
    # ---------------------------------
    def decode(self, raw_bytes: bytes):
        self.parser.append_buffer(raw_bytes)
        msg = self.parser.get_message()

        if msg is not None:
            self.sender_comp_id = msg.get(49).decode().strip()
            self.target_comp_id = msg.get(56).decode().strip()

        return msg

    # ---------------------------------
    # Map FIX → Canonical
    # ---------------------------------
    def map_to_canonical(self, msg):

        if msg is None:
            return None

        msg_type = msg.get(35).decode()

        if msg_type != "D":
            return None

        side_value = msg.get(54).decode()
        side = Side.BUY if side_value == "1" else Side.SELL

        return CanonicalOrder(
            order_id=msg.get(11).decode(),
            side=side,
            symbol=msg.get(55).decode(),
            price=float(msg.get(44).decode()),
            quantity=int(msg.get(38).decode()),
        )

    # ---------------------------------
    # Encode ExecutionReport
    # ---------------------------------
    def encode_execution(self, execution):

        msg = simplefix.FixMessage()

        sending_time = datetime.datetime.utcnow().strftime(
            "%Y%m%d-%H:%M:%S.%f"
        )[:-3]

        msg.append_pair(8, "FIX.4.4")
        msg.append_pair(35, "8")
        msg.append_pair(34, str(self.out_seq_num))
        msg.append_pair(49, self.target_comp_id)
        msg.append_pair(56, self.sender_comp_id)
        msg.append_pair(52, sending_time)

        msg.append_pair(11, execution.buy_order_id)
        msg.append_pair(17, f"EXEC{self.out_seq_num}")

        if execution.sell_order_id == "RISK_REJECT":
            msg.append_pair(150, "8")
            msg.append_pair(39, "8")
            msg.append_pair(58, "Risk limit exceeded")

        elif execution.quantity == 0:
            msg.append_pair(150, "0")
            msg.append_pair(39, "0")

        else:
            msg.append_pair(150, "2")
            msg.append_pair(39, "2")
            msg.append_pair(38, str(execution.quantity))
            msg.append_pair(44, str(execution.price))

        self.out_seq_num += 1

        return msg.encode()

    # ---------------------------------
    # Encode Logon Ack
    # ---------------------------------
    def encode_logon_ack(self):

        msg = simplefix.FixMessage()

        sending_time = datetime.datetime.utcnow().strftime(
            "%Y%m%d-%H:%M:%S.%f"
        )[:-3]

        msg.append_pair(8, "FIX.4.4") # HARDCODED - FETCH from canonical order book. Execution report needs to be enriched. How to make it easy for a developer to make a market simulator with this 
        msg.append_pair(35, "A")
        msg.append_pair(34, str(self.out_seq_num))
        msg.append_pair(49, self.target_comp_id)
        msg.append_pair(56, self.sender_comp_id)
        msg.append_pair(52, sending_time)
        msg.append_pair(98, "0")
        msg.append_pair(108, "30")

        self.out_seq_num += 1

        return msg.encode()
