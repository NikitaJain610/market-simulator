# plugins/fix_session_logic.py

class FixSessionLogic:
    def __init__(self):
        self.logged_in = False

    def handle_session(self, msg):
        if msg is None:
            return "IGNORE"

        msg_type = msg.get(35).decode()

        if msg_type == "A":  # Logon
            self.logged_in = True
            return "LOGON"

        if not self.logged_in:
            raise Exception("Client not logged in")

        return "APPLICATION"
