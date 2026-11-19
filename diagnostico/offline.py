"""Diagnóstico offline de três canais de pressão do T3-Guard."""
import argparse
import csv
import io
from pathlib import Path
import random
import statistics
import sys

HEADER = ("timestamp_ms", "unidade", "a_kpa", "b_kpa", "c_kpa")
CHANNELS = ("A", "B", "C")
MAX_BYTES = 2_000_000
FIELD_LIMIT = 32
WINDOW = 6
DIVERGENCE = 180
CONFIRM = 3


def read_csv(path):
    with Path(path).open("rb") as source:
        content = source.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError("CSV excede 2 MB")
    reader = csv.reader(io.StringIO(content.decode("utf-8-sig"), newline=""), strict=True)
    if tuple(next(reader, ())) != HEADER:
        raise ValueError("cabeçalho deve ser " + ",".join(HEADER))
    samples = []
    previous = -1
    for number, row in enumerate(reader, 2):
        if len(row) != 5 or any(len(field) > FIELD_LIMIT for field in row):
            raise ValueError(f"linha {number}: tamanho ou colunas inválidas")
        timestamp, unit, *values = row
        if unit != "kPa" or not timestamp.isascii() or not timestamp.isdecimal():
            raise ValueError(f"linha {number}: use timestamp inteiro em ms e unidade kPa")
        time_ms = int(timestamp)
        if time_ms <= previous:
            raise ValueError(f"linha {number}: timestamps devem ser crescentes")
        previous = time_ms
        parsed = []
        for value in values:
            if value == "":
                parsed.append(None)
                continue
            if not value.isascii() or not value.isdecimal() or not 0 <= int(value) <= 1000:
                raise ValueError(f"linha {number}: use leitura inteira de 0 a 1000 kPa ou campo vazio")
            parsed.append(int(value))
        samples.append((time_ms, tuple(parsed)))
    if len(samples) < WINDOW:
        raise ValueError(f"forneça ao menos {WINDOW} amostras")
    cadence = samples[1][0] - samples[0][0]
    if any(t - last != cadence for (last, _), (t, _) in zip(samples, samples[1:])):
        raise ValueError("cadência irregular; use uma linha por instante, mesmo quando faltar uma leitura")
    return samples


def baseline(window, channel):
    peers = [i for i in range(3) if i != channel]
    if window[-1][channel] is None:
        return True
    for values in window[-CONFIRM:]:
        candidate, a, b = values[channel], values[peers[0]], values[peers[1]]
        if None in (candidate, a, b):
            return False
        if not (abs(a-b) <= DIVERGENCE and
                abs(candidate-a) > DIVERGENCE and abs(candidate-b) > DIVERGENCE):
            return False
    return True


def features(window, channel):
    target = [row[channel] for row in window]
    peers = [i for i in range(3) if i != channel]
    differences = []
    agreement = []
    for row in window:
        a, b = (row[i] for i in peers)
        if a is not None and b is not None:
            agreement.append(abs(a-b))
            if row[channel] is not None:
                differences.append(abs(row[channel] - (a+b)/2))
    target_values = [value for value in target if value is not None]
    peer_values = [row[i] for row in window for i in peers if row[i] is not None]
    mobility = (max(peer_values)-min(peer_values) if peer_values else 0) - (
        max(target_values)-min(target_values) if target_values else 0)
    return (int(target[-1] is None), statistics.median(differences) if differences else 0,
            max(agreement, default=0), mobility)


def generate_run(seed, fault, channel):
    rng = random.Random(seed)
    center = rng.randint(240, 680)
    slope = rng.choice((-1, 1)) * rng.randint(3, 10)
    bias = rng.choice((-1, 1)) * rng.randint(55, 245)
    readings = []
    for step in range(18):
        signal = center + step*slope
        if step >= 9 and fault == "process":
            signal += 105
        row = [signal + rng.randint(-6, 6) for _ in CHANNELS]
        if step >= 9:
            if fault == "offset":
                row[channel] += bias
            elif fault == "frozen":
                row[channel] = readings[8][1][channel]
            elif fault == "missing":
                row[channel] = None
        readings.append((step*100, tuple(min(1000, max(0, x)) if x is not None else None for x in row)))
    return readings


def dataset(start, count):
    kinds = ("normal", "process", "offset", "frozen", "missing")
    examples = []
    for seed in range(start, start+count):
        fault = kinds[seed % len(kinds)]
        channel = (seed // len(kinds)) % 3
        rows = generate_run(seed, fault, channel)
        for end in (6, 9, 15, 18):
            window = [values for _, values in rows[end-WINDOW:end]]
            for candidate in range(3):
                expected = end > 9 and fault in ("offset", "frozen", "missing") and candidate == channel
                examples.append((features(window, candidate), baseline(window, candidate), expected))
    return examples


def fit_tree(rows, depth=3):
    positives = sum(label for _, _, label in rows)
    if depth == 0 or positives in (0, len(rows)):
        return positives > len(rows)/2

    def loss(group):
        total = sum(label for _, _, label in group)
        return total*(len(group)-total)/len(group)

    best_loss = loss(rows)
    split = None
    for feature in range(len(rows[0][0])):
        values = sorted({vector[feature] for vector, _, _ in rows})
        for threshold in values[:-1]:
            left, right = [], []
            for row in rows:
                group = left if row[0][feature] <= threshold else right
                group.append(row)
            score = loss(left) + loss(right)
            if score < best_loss:
                best_loss = score
                split = feature, threshold, left, right
    if split is None:
        return positives > len(rows)/2
    feature, threshold, left, right = split
    return feature, threshold, fit_tree(left, depth-1), fit_tree(right, depth-1)


def predict(tree, vector):
    while isinstance(tree, tuple):
        feature, threshold, left, right = tree
        tree = left if vector[feature] <= threshold else right
    return tree


def report():
    tree = fit_tree(dataset(1000, 180))
    test = dataset(4000, 90)
    def errors(classify):
        fp = fn = tp = tn = 0
        for vector, rule, label in test:
            result = classify(vector, rule)
            fp += result and not label
            fn += not result and label
            tp += result and label
            tn += not result and not label
        return fp, fn, tp, tn
    rule = errors(lambda _, flag: flag)
    model = errors(lambda vector, _: predict(tree, vector))
    print("90 ensaios sintéticos separados do treino")
    for title, results in (("Regra", rule), ("Árvore", model)):
        fp, fn, tp, tn = results
        print(f"{title}: alarmes indevidos={fp}, falhas não detectadas={fn}, detectadas={tp}, normais corretos={tn}")
    if model[0] <= rule[0] and model[1] < rule[1]:
        print("Árvore candidata a teste físico; importador padrão usa a regra.")
    else:
        print("Manter a regra neste experimento.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--comparar", action="store_true")
    group.add_argument("--csv", type=Path)
    group.add_argument("--gerar", type=Path)
    args = parser.parse_args()
    try:
        if args.comparar:
            report()
        elif args.gerar:
            with args.gerar.open("x", encoding="utf-8", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(HEADER)
                writer.writerows((t, "kPa", *values) for t, values in generate_run(1002, "missing", 1))
        else:
            samples = read_csv(args.csv)
            for end in range(WINDOW, len(samples)+1):
                window = [values for _, values in samples[end-WINDOW:end]]
                flagged = [name for index, name in enumerate(CHANNELS) if baseline(window, index)]
                if sum(value is None for value in window[-1]) >= 2:
                    label = "inconclusivo (dois ou mais canais ausentes)"
                elif flagged:
                    label = "suspeita nos canais " + ", ".join(flagged)
                else:
                    label = "sem discrepância confirmada"
                print(f"{samples[end-1][0]} ms  {label}")
    except (OSError, csv.Error, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
