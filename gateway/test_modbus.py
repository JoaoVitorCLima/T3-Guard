import socket
import struct
import threading
import unittest

from modbus import ModbusHandler, Server, Snapshot


class GatewayTest(unittest.TestCase):
    def test_wire_protocol(self):
        with Server(("127.0.0.1", 0), ModbusHandler) as server:
            server.snapshot = Snapshot()
            server.snapshot.update(3, 123, 64)
            server.snapshot.update(5, 456, 65)
            worker = threading.Thread(target=server.serve_forever)
            worker.start()
            try:
                with socket.create_connection(server.server_address) as client, client.makefile("rb") as reply:
                    for request, expected in (
                        (b"\x04\x00\x00\x00\x08", b"\x04\x10" + struct.pack(">8H", 513, 1, 0, 5, 0, 456, 65, 1)),
                        (b"\x06\x00\x00\x00\x00", b"\x86\x01"),
                        (b"\x04\x00\x08\x00\x01", b"\x84\x02"),
                    ):
                        client.sendall(struct.pack(">HHHB", 19, 0, len(request)+1, 1) + request)
                        self.assertEqual(reply.read(7), struct.pack(">HHHB", 19, 0, len(expected)+1, 1))
                        self.assertEqual(reply.read(len(expected)), expected)
            finally:
                server.shutdown()
                worker.join()


if __name__ == "__main__":
    unittest.main()
