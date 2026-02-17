# session/session_handler.py

class SessionHandler:

    def __init__(self, plugin, engine):
        self.plugin = plugin
        self.session_logic = plugin.create_session_logic()
        self.engine = engine

    async def handle(self, raw_bytes, writer):

        print("\n" + "=" * 60)
        print("[SERVER] Raw message received:")
        print(self._pretty(raw_bytes))
        print("=" * 60)

        msg = self.plugin.decode(raw_bytes)

        if msg is None:
            print("[SERVER] Decode returned None")
            return

        state = self.session_logic.handle_session(msg)

        # -------------------------
        # LOGON HANDLING
        # -------------------------
        if state == "LOGON":

            print("[SERVER] LOGON received")

            response = self.plugin.encode_logon_ack()

            print("[SERVER] Sending Logon Ack:")
            print(self._pretty(response))

            writer.write(response)
            await writer.drain()
            return

        # -------------------------
        # APPLICATION MESSAGE
        # -------------------------
        if state == "APPLICATION":

            canonical = self.plugin.map_to_canonical(msg)

            if canonical is None:
                print("[SERVER] Canonical mapping returned None")
                return

            print("\n[SERVER] Canonical Order:")
            print(canonical)

            execution = self.engine.process_order(canonical)

            print("\n[SERVER] Execution Generated:")
            print(execution)

            response = self.plugin.encode_execution(execution)

            print("\n[SERVER] Sending Execution Report:")
            print(self._pretty(response))
            print("=" * 60 + "\n")

            writer.write(response)
            await writer.drain()

    def _pretty(self, raw):
        try:
            return raw.decode().replace("\x01", "|")
        except:
            return raw
