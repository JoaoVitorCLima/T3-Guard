"""Prepare um recorte de pressão PRONTO para reprodução com canais derivados."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from itertools import islice
from pathlib import Path

from diagnostico.offline import HEADER, WINDOW

FACTORS = {"bar": 100, "kPa": 1, "MPa": 1000}


def convert(path, column, unit, skip, count, inject):
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source, strict=True)
        if column not in (reader.fieldnames or ()):
            raise ValueError(f"coluna ausente: {column}")
        records = []
        for index, row in enumerate(islice(reader, skip, skip + count)):
            pressure = Decimal(row[column]) * FACTORS[unit]
            if not pressure.is_finite() or not 0 <= pressure <= 1000:
                raise ValueError(f"pressão fora de 0–1000 kPa na linha {skip+index+2}")
            a = round(pressure)
            b = a + 200 if inject and index >= count//2 else a
            if b > 1000:
                raise ValueError("a injeção ultrapassa 1000 kPa; selecione outro recorte")
            records.append((index*1000, "kPa", a, b, a))
        if len(records) != count:
            raise ValueError("o arquivo não contém todas as amostras solicitadas")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origem", type=Path)
    parser.add_argument("saida", type=Path)
    parser.add_argument("--coluna", default="Mixture.zone.P")
    parser.add_argument("--unidade", choices=FACTORS, required=True)
    parser.add_argument("--pular", type=int, default=0)
    parser.add_argument("--amostras", type=int, default=60)
    parser.add_argument("--desvio-b", action="store_true")
    args = parser.parse_args()
    if args.pular < 0 or not WINDOW <= args.amostras <= 5000:
        parser.error("use 6–5000 amostras e um deslocamento não negativo")
    try:
        rows = convert(args.origem, args.coluna, args.unidade, args.pular,
                       args.amostras, args.desvio_b)
        with args.saida.open("x", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(HEADER)
            writer.writerows(rows)
    except (OSError, ValueError, TypeError, InvalidOperation, csv.Error) as error:
        parser.error(str(error))
    pressures = [row[2] for row in rows]
    print(f"{len(rows)} amostras de {args.coluna}; faixa {min(pressures)}–{max(pressures)} kPa")
    print("Três canais derivados; tempo relativo de reprodução.")
    if args.desvio_b:
        print("Desvio de +200 kPa injetado em B na segunda metade.")


if __name__ == "__main__":
    main()
