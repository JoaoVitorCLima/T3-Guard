"""Demonstração em loopback com leitura real dos registradores FC04."""

import argparse
import json
import socket
import struct
import threading

from gateway.integridade import REGISTER_COUNT, make_scenario
from gateway.modbus import ModbusHandler, Server


def collect_fc04(snapshot, stages, count):
    results = []
    with Server(("127.0.0.1", 0), ModbusHandler) as server:
        server.snapshot = snapshot
        worker = threading.Thread(target=server.serve_forever)
        worker.start()
        try:
            with socket.create_connection(server.server_address, timeout=2) as client:
                with client.makefile("rb") as response:
                    for tid, title in enumerate(stages, 1):
                        client.sendall(struct.pack(">HHHBBHH", tid, 0, 6, 1, 4, 0, count))
                        expected = struct.pack(">HHHBBB", tid, 0, 3+2*count, 1, 4, 2*count)
                        if response.read(len(expected)) != expected:
                            raise RuntimeError("Resposta FC04 inesperada")
                        registers = struct.unpack(f">{count}H", response.read(2*count))
                        results.append({"stage": title, "registers": registers})
        finally:
            server.shutdown()
            worker.join()
    return results


def collect_demo():
    monitor, stages = make_scenario()

    def run():
        for title, frames in stages:
            for frame in frames:
                monitor.accept(frame)
            yield title

    return collect_fc04(monitor, run(), REGISTER_COUNT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    records = collect_demo()
    if args.json:
        print(json.dumps(records))
        return
    for record in records:
        _, fresh, a, b, c, suspect, accepted, invalid, integrity, repeat, status, channel = record["registers"]
        print(f'{record["stage"]}: A/B/C={a}/{b}/{c} kPa, '
              f'frescor={fresh:03b}, suspeitos={suspect:03b}, aceitas={accepted}, '
              f'inválidas={invalid}, integridade={integrity}, repetição={repeat}, '
              f'estado={status}, canal={channel}')


if __name__ == "__main__":
    main()
