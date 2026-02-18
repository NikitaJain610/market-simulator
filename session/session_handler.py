# session/session_handler.py

class SessionHandler:

    def __init__(self, plugin, engine):
        self.plugin = plugin
        self.session_logic = plugin.create_session_logic()
        self.engine = engine

    async def handle(self, raw_bytes, writer):

        msg = self.plugin.decode(raw_bytes)

        if msg is None:
            return

        state = self.session_logic.handle_session(msg)

        if state == "LOGON":
            response = self.plugin.encode_logon_ack()
            writer.write(response)
            await writer.drain()
            return

        canonical = self.plugin.map_to_canonical(msg)

        if canonical is None:
            return

        events = self.engine.process_order(canonical)

        for event in events:
            response = self.plugin.encode_event(event)
            if response:
                writer.write(response)
                await writer.drain()
