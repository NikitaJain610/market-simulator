# transport/tcp_server.py

import asyncio


class TCPServer:

    def __init__(self, host, port, session_handler):
        self.host = host
        self.port = port
        self.session_handler = session_handler

    async def handle_client(self, reader, writer):
        print("Client connected")

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break

                await self.session_handler.handle(data, writer)

        except Exception as e:
            print("Server error:", e)

        finally:
            print("Client disconnected")
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )

        print(f"Server running on {self.host}:{self.port}")

        async with server:
            await server.serve_forever()
