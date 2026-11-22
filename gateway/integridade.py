"""Verificação de amostras autenticadas de uma sessão de bancada."""

from collections import deque
import hashlib
import hmac
import secrets
import struct
import threading
import time

from diagnostico.offline import CONFIRM, baseline


FORMAT = struct.Struct(">16sBIH")
TAG_SIZE = hashlib.sha256().digest_size
STALE_SECONDS = 2
ACCEPTED, INVALID, AUTH_FAILED, REPLAY = 1, 2, 3, 4
UNKNOWN = 65535
MAP_ID = 0x0401
REGISTER_COUNT = 12


def signed_sample(key, session, channel, sequence, pressure):
    payload = FORMAT.pack(session, channel, sequence, pressure)
    return payload + hmac.digest(key, payload, "sha256")


class IntegrityMonitor:
    def __init__(self, keys, clock=time.monotonic, *, on_round=None):
        if len(keys) != 3 or any(len(key) != 32 for key in keys) or len(set(keys)) != 3:
            raise ValueError("Forneça três chaves distintas de 32 bytes")
        self.session = secrets.token_bytes(16)
        self._keys = tuple(keys)
        self._clock = clock
        self._on_round = on_round
        self._lock = threading.Lock()
        self._sequences = [0, 0, 0]
        self._round = [0, 0, 0]
        self._pressures = [UNKNOWN, UNKNOWN, UNKNOWN]
        self._received = [None, None, None]
        self._history = deque(maxlen=CONFIRM)
        self._suspect = 0
        self._counts = [0] * 5
        self._last = 0
        self._last_channel = UNKNOWN

    def _record(self, status, channel):
        self._counts[status] = min(65535, self._counts[status] + 1)
        self._last = status
        self._last_channel = channel
        return status

    def _fresh_mask(self, now):
        return sum(1 << i for i, stamp in enumerate(self._received)
                   if stamp is not None and now - stamp < STALE_SECONDS)

    def accept(self, frame):
        with self._lock:
            if len(frame) != FORMAT.size + TAG_SIZE:
                return self._record(INVALID, UNKNOWN)
            payload, tag = frame[:FORMAT.size], frame[FORMAT.size:]
            session, channel, sequence, pressure = FORMAT.unpack(payload)
            if channel >= 3:
                return self._record(INVALID, UNKNOWN)
            if not hmac.compare_digest(tag, hmac.digest(self._keys[channel], payload, "sha256")):
                return self._record(AUTH_FAILED, channel)
            if session != self.session or sequence <= self._sequences[channel]:
                return self._record(REPLAY, channel)
            if pressure > 1000:
                return self._record(INVALID, channel)
            now = self._clock()
            if self._fresh_mask(now) != 7:
                self._history.clear()
                self._suspect = 0
            self._sequences[channel] = sequence
            self._pressures[channel] = pressure
            self._received[channel] = now
            if self._fresh_mask(now) == 7 and all(
                    sequence > previous for sequence, previous in zip(self._sequences, self._round)):
                self._round[:] = self._sequences
                pressures = tuple(self._pressures)
                self._history.append(pressures)
                if self._on_round is not None:
                    self._on_round(pressures)
                self._suspect = 0
                if len(self._history) == CONFIRM:
                    window = tuple(self._history)
                    self._suspect = sum(1 << i for i in range(3) if baseline(window, i))
            return self._record(ACCEPTED, channel)

    def registers(self):
        with self._lock:
            fresh = self._fresh_mask(self._clock())
            pressures = tuple(value if fresh & (1 << i) else UNKNOWN
                              for i, value in enumerate(self._pressures))
            return (MAP_ID, fresh, *pressures, self._suspect if fresh == 7 else 0,
                    *self._counts[1:], self._last, self._last_channel)


def bench_scenario(keys, session):
    """In-memory test fixtures from three simulated producers."""
    yield "Amostras válidas", tuple(
        signed_sample(key, session, channel, 1, pressure)
        for channel, (key, pressure) in enumerate(zip(keys, (123, 124, 123))))
    candidate = signed_sample(keys[1], session, 1, 2, 124)
    changed_value = FORMAT.pack(session, 1, 2, 324)
    yield "Amostra alterada", (changed_value + candidate[-TAG_SIZE:],)
    yield "Amostra repetida", (signed_sample(keys[1], session, 1, 1, 124),)
    yield "Canal autenticado divergente", tuple(
        signed_sample(key, session, channel, seq, pressure)
        for seq in (2, 3, 4)
        for channel, (key, pressure) in enumerate(zip(keys, (123, 324, 123))))


def make_scenario(*, on_round=None):
    keys = tuple(secrets.token_bytes(32) for _ in range(3))
    monitor = IntegrityMonitor(keys, on_round=on_round)
    return monitor, bench_scenario(keys, monitor.session)
