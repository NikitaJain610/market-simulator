import asyncio
from core.market_engine import MarketEngine


from plugins.fix_plugin import FixPlugin
from session.session_handler import SessionHandler
from transport.tcp_server import TCPServer


def main():
    engine = MarketEngine()

    plugin = FixPlugin()
    session_handler = SessionHandler(plugin, engine)

    server = TCPServer("127.0.0.1", 5001, session_handler)

    asyncio.run(server.start())


if __name__ == "__main__":
    main()
