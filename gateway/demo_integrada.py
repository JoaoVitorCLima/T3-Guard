"""Bancada local com autenticação, simulação do RTL e leitura Modbus FC04."""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import tempfile

from gateway.demo_integridade import collect_fc04
from gateway.integridade import make_scenario

MAP_ID = 0x0501
REGISTER_COUNT = 17
ROOT = Path(__file__).resolve().parents[1]


@dataclass
class StageSnapshot:
    values: tuple = ()

    def registers(self):
        return self.values


def simulate(rounds):
    vectors = "".join(f"{a} {b} {c}\n" for a, b, c in rounds)
    with tempfile.TemporaryDirectory(prefix="t3-guard-") as directory:
        executable = Path(directory) / "gateway_tb"
        subprocess.run(
            ["iverilog", "-g2012", "-s", "tb_gateway", "-o", str(executable),
             str(ROOT / "rtl/vigia.sv"), str(ROOT / "sim/tb_gateway.sv")],
            check=True, capture_output=True, text=True, timeout=30,
        )
        result = subprocess.run(["vvp", str(executable)], input=vectors, text=True,
                                check=True, capture_output=True, timeout=30)
    rows = [tuple(map(int, line.split()[1:]))
            for line in result.stdout.splitlines() if line.startswith("RTL ")]
    if any(len(row) != 6 for row in rows) or [row[0] for row in rows] != list(range(1, len(rounds) + 1)):
        raise RuntimeError("A captura RTL está incompleta")
    return rows


def collect_demo():
    rounds = []
    monitor, stages = make_scenario(on_round=rounds.append)
    verified = []
    for title, frames in stages:
        for frame in frames:
            monitor.accept(frame)
        verified.append((title, len(rounds), monitor.registers()))
    simulated = simulate(rounds)
    snapshot = StageSnapshot()

    def present():
        for title, round_num, measurements in verified:
            _, discrepancy, excluded, mode, trip, event = simulated[round_num-1]
            snapshot.values = (MAP_ID, *measurements[1:5], discrepancy,
                               *measurements[6:], mode, trip, event >> 16, event & 65535, excluded)
            yield title

    results = collect_fc04(snapshot, present(), REGISTER_COUNT)
    for result, (_, round_num, _) in zip(results, verified):
        result["rounds"] = round_num
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--javascript", action="store_true", help="exportar captura para o painel")
    args = parser.parse_args()
    try:
        records = collect_demo()
    except FileNotFoundError as error:
        parser.exit(1, f"Icarus Verilog é necessário: {error}\n")
    except subprocess.CalledProcessError as error:
        parser.exit(1, (error.stderr or error.stdout or str(error)) + "\n")
    except (subprocess.TimeoutExpired, RuntimeError) as error:
        parser.exit(1, f"Falha no ensaio integrado: {error}\n")
    if args.javascript:
        print("window.integrityTrace = " + json.dumps(records) + ";")
        return
    for record in records:
        row = record["registers"]
        print(f'{record["stage"]} | rodadas RTL={record["rounds"]} | B={row[3]} kPa | '
              f'integridade={row[8]} repetição={row[9]} | '
              f'discrep={row[5]:03b} modo={row[12]} trip={row[13]}')


if __name__ == "__main__":
    main()
