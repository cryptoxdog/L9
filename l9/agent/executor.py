import webbrowser
from .packet_types import CommandPacket


class Executor:
    def __init__(self):
        self.map = {
            "open_url": self._open_url,
        }

    def execute(self, packet: CommandPacket):
        handler = self.map.get(packet.op)
        if handler:
            handler(packet)

    def _open_url(self, packet: CommandPacket):
        url = packet.args.get("url")
        if url:
            webbrowser.open(url)

