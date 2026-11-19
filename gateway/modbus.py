"""Local FC04 gateway. Source is an FPGA serial stream or an RTL CSV recording."""
import argparse
import csv
from functools import reduce
from operator import xor
import socketserver
import struct
import threading
import time


class Snapshot:
    def __init__(self):
        self.lock = threading.Lock()
        self.values = (0, 0, 0, 0)
        self.updated = None

    def update(self, event_id, event_tick, state):
        with self.lock:
            lost = self.values[3]
            if self.updated is not None and event_id > self.values[0] + 1:
                lost = min(65535, lost + event_id - self.values[0] - 1)
            self.values = (event_id, event_tick, state, lost)
            self.updated = time.monotonic()

    def registers(self):
        with self.lock:
            event_id, tick, state, lost = self.values
            fresh = self.updated is not None and time.monotonic() - self.updated < 2
            return (0x0201, int(fresh), event_id >> 16, event_id & 65535,
                    tick >> 16, tick & 65535, state, lost)


def serial_source(port, snapshot):
    import serial
    buffer = bytearray()
    with serial.Serial(port, 115200, timeout=0.2) as connection:
        while True:
            buffer.extend(connection.read(connection.in_waiting or 1))
            while len(buffer) >= 13:
                if buffer[:2] != b"\x02\x21" or reduce(xor, buffer[:13]) != 0:
                    del buffer[0]
                    continue
                snapshot.update(*struct.unpack_from("<IIH", buffer, 2))
                del buffer[:13]


def replay(path, snapshot):
    with open(path, newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    while True:
        for row in rows:
            item = {key: int(value) for key, value in row.items()}
            state = (item["timeout"] << 9 | item["mode"] << 7 | item["trip"] << 6
                     | item["bad"] << 3 | item["high"])
            snapshot.update(item["event_id"], item["event_tick"], state)
            time.sleep(0.6)


class ModbusHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(10)
        while True:
            header = self.rfile.read(7)
            if len(header) != 7:
                return
            transaction, protocol, length, unit = struct.unpack(">HHHB", header)
            if protocol or not 2 <= length <= 254:
                return
            pdu = self.rfile.read(length - 1)
            if len(pdu) != length - 1 or unit != 1:
                return
            reply = self.respond(pdu)
            self.wfile.write(struct.pack(">HHHB", transaction, 0, len(reply)+1, unit) + reply)

    def respond(self, pdu):
        function = pdu[0]
        if function != 4:
            return bytes((function | 128, 1))
        if len(pdu) != 5:
            return b"\x84\x03"
        start, count = struct.unpack(">HH", pdu[1:])
        if not 1 <= count <= 125:
            return b"\x84\x03"
        values = self.server.snapshot.registers()
        if start + count > len(values):
            return b"\x84\x02"
        return bytes((4, 2*count)) + struct.pack(f">{count}H", *values[start:start+count])


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--serial")
    source.add_argument("--replay")
    parser.add_argument("--port", type=int, default=1502)
    args = parser.parse_args()
    snapshot = Snapshot()
    target, path = (serial_source, args.serial) if args.serial else (replay, args.replay)
    threading.Thread(target=target, args=(path, snapshot), daemon=True).start()
    with Server(("127.0.0.1", args.port), ModbusHandler) as server:
        server.snapshot = snapshot
        print(f"Modbus TCP FC04, unit 1, 127.0.0.1:{args.port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
