from shutil import which
import unittest

from gateway.demo_integrada import MAP_ID, collect_demo


@unittest.skipUnless(which("iverilog") and which("vvp"), "Icarus Verilog é necessário")
class IntegratedDemoTest(unittest.TestCase):
    def test_only_verified_rounds_reach_rtl_and_fc04_reports_decisions(self):
        stages = collect_demo()
        self.assertEqual([item["rounds"] for item in stages], [1, 1, 1, 4])
        valid, changed, repeated, divergent = [item["registers"] for item in stages]
        self.assertTrue(all(item[0] == MAP_ID for item in (valid, changed, repeated, divergent)))
        for row in (valid, changed, repeated):
            self.assertEqual(row[2:6], (123, 124, 123, 0))
            self.assertEqual(row[12:], (0, 0, 0, 1, 0))
        self.assertEqual(changed[8:11], (1, 0, 3))
        self.assertEqual(repeated[8:11], (1, 1, 4))
        self.assertEqual(divergent[2:6], (123, 324, 123, 2))
        self.assertEqual(divergent[12:], (1, 0, 0, 2, 2))
