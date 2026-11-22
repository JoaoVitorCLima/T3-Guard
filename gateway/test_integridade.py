import unittest

from gateway.demo_integridade import collect_demo
from gateway.integridade import (
    ACCEPTED, AUTH_FAILED, INVALID, MAP_ID, REPLAY, UNKNOWN, IntegrityMonitor, signed_sample,
)


class IntegrityTest(unittest.TestCase):
    def test_fc04_reports_each_stage(self):
        valid, modified, repeated, divergent = [item["registers"] for item in collect_demo()]
        self.assertEqual(valid, (MAP_ID, 7, 123, 124, 123, 0, 3, 0, 0, 0, ACCEPTED, 2))
        self.assertEqual(modified, (MAP_ID, 7, 123, 124, 123, 0, 3, 0, 1, 0, AUTH_FAILED, 1))
        self.assertEqual(repeated, (MAP_ID, 7, 123, 124, 123, 0, 3, 0, 1, 1, REPLAY, 1))
        self.assertEqual(divergent, (MAP_ID, 7, 123, 324, 123, 2, 12, 0, 1, 1, ACCEPTED, 2))

    def test_rejection_does_not_refresh_or_advance_sequence(self):
        now = [0]
        keys = tuple(bytes([i]) * 32 for i in range(3))
        monitor = IntegrityMonitor(keys, clock=lambda: now[0])
        b = signed_sample(keys[1], monitor.session, 1, 1, 123)
        self.assertEqual(monitor.accept(b), ACCEPTED)
        now[0] = 2
        self.assertEqual(monitor.accept(b), REPLAY)
        self.assertEqual(monitor.registers()[1:5], (0, UNKNOWN, UNKNOWN, UNKNOWN))
        self.assertEqual(monitor.accept(signed_sample(keys[0], monitor.session, 1, 2, 321)), AUTH_FAILED)
        self.assertEqual(monitor.accept(signed_sample(keys[1], monitor.session, 1, 2, 1001)), INVALID)
        self.assertEqual(monitor.accept(signed_sample(keys[1], monitor.session, 1, 2, 127)), ACCEPTED)
        self.assertEqual(monitor.registers()[1:5], (2, UNKNOWN, 127, UNKNOWN))
        restarted = IntegrityMonitor(keys)
        self.assertEqual(restarted.accept(b), REPLAY)
