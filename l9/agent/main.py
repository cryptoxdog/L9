import asyncio
from .websocket_client import AgentClient


def main():
    asyncio.run(AgentClient().run())


if __name__ == "__main__":
    main()

