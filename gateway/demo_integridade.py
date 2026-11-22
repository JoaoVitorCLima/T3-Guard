"""Demonstração em loopback com leitura real dos registradores FC04."""

import argparse
import json
import socket
import struct
import threading

from gateway.integridade import REGISTER_COUNT, make_scenario
from gateway.modbus import ModbusHandler, Server


def collect_demo():
    monitor, stages = make_scenario()
    results = []
    with Server(("127.0.0.1", 0), ModbusHandler) as server:
        server.snapshot = monitor
        worker = threading.Thread(target=server.serve_forever)
        worker.start()
        try:
            with socket.create_connection(server.server_address, timeout=2) as client:
                with client.makefile("rb") as response:
                    for tid, (title, frames) in enumerate(stages, 1):
                        for frame in frames:
                            monitor.accept(frame)
                        client.sendall(struct.pack(">HHHBBHH", tid, 0, 6, 1, 4, 0, REGISTER_COUNT))
                        expected = struct.pack(">HHHBBB", tid, 0, 3+2*REGISTER_COUNT,
                                               1, 4, 2*REGISTER_COUNT)
                        if response.read(len(expected)) != expected:
                            raise RuntimeError("Resposta FC04 inesperada")
                        registers = struct.unpack(f">{REGISTER_COUNT}H",
                                                  response.read(2*REGISTER_COUNT))
                        results.append({"stage": title, "registers": registers})
        finally:
            server.shutdown()
            worker.join()
    return results


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
