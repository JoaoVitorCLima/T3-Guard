"""Read-only FC04 gateway for FPGA serial, RTL replay, or pressure CSV."""
import argparse
import csv
from functools import reduce
from ipaddress import IPv4Address
from operator import xor
from pathlib import Path
import socketserver
import struct
import threading
import time


class Snapshot:
    def __init__(self):
        self.lock = threading.Lock()
        self.values = (0, 0, 0, 0)
        self.updated = None
        self.pressure = None

    def update_pressure(self, sequence, values, flagged):
        missing = sum(1 << i for i, value in enumerate(values) if value is None)
        with self.lock:
            self.pressure = (sequence, *[65535 if v is None else v for v in values],
                             missing, flagged)
            self.updated = time.monotonic()

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
            if self.pressure is not None:
                sequence, a, b, c, missing, flagged = self.pressure
                return (0x0301, int(fresh), sequence >> 16, sequence & 65535,
                        a, b, c, missing, flagged, 1)
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
    source.add_argument("--pressao", type=Path, metavar="CSV")
    source.add_argument("--demo-integridade", action="store_true")
    parser.add_argument("--bind", type=IPv4Address, default=IPv4Address("127.0.0.1"))
    parser.add_argument("--port", type=int, default=1502)
    args = parser.parse_args()
    if args.bind.is_unspecified or args.bind.is_multicast:
        parser.error("--bind exige um endereço IPv4 específico da bancada")
    snapshot = Snapshot()
    if args.demo_integridade:
        from gateway.integridade import ACCEPTED, make_scenario

        snapshot, stages = make_scenario()

        def replay_integrity():
            for title, frames in stages:
                for frame in frames:
                    status = snapshot.accept(frame)
                    if status != ACCEPTED:
                        print(f"Entrada rejeitada, código={status}", flush=True)
                print(title, flush=True)
                time.sleep(1)

        worker = threading.Thread(target=replay_integrity, daemon=True)
    elif args.pressao:
        from diagnostico.offline import baseline, read_csv, WINDOW
        try:
            samples = read_csv(args.pressao)
        except (OSError, ValueError, csv.Error) as error:
            parser.error(str(error))

        def replay_pressure():
            for end in range(WINDOW, len(samples) + 1):
                window = [values for _, values in samples[end-WINDOW:end]]
                flagged = sum(1 << i for i in range(3) if baseline(window, i))
                snapshot.update_pressure(end, window[-1], flagged)
                time.sleep(0.6)

        snapshot.pressure = (0, 65535, 65535, 65535, 7, 0)
        worker = threading.Thread(target=replay_pressure, daemon=True)
    else:
        target, path = (serial_source, args.serial) if args.serial else (replay, args.replay)
        worker = threading.Thread(target=target, args=(path, snapshot), daemon=True)
    with Server((str(args.bind), args.port), ModbusHandler) as server:
        server.snapshot = snapshot
        worker.start()
        print(f"Modbus TCP FC04, unit 1, {args.bind}:{server.server_address[1]}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
