"""Tests for translation.py: unit tests, and failure injection on a copy
of the committed inputs (each check must be able to fail).

Run from analysis/:  python3 -m unittest discover -s tests
"""
import ipaddress
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.dirname(HERE)
REPO = os.path.dirname(ANALYSIS)
sys.path.insert(0, ANALYSIS)
import translation as t  # noqa: E402

INPUTS = ["ansible-openvpn/openvpn.yaml", "journal/phase-1.md", "journal/phase-2.md",
          "ansible-openziti/group_vars/all/vars.yaml", "ansible-netbird/group_vars/all/vars.yaml",
          "ansible-netbird/policies-export.json", "test-matrix"]


class Units(unittest.TestCase):
    def test_rule_without_port_matches_any_port(self):
        rule = {"to": ipaddress.ip_network("10.0.0.0/24"), "port": None, "proto": "any"}
        self.assertTrue(t.p1_rule_matches(rule, {"host": "10.0.0.73", "port": 8023, "protos": ("tcp",)}))
        self.assertFalse(t.p1_rule_matches(rule, {"host": "10.100.10.10", "port": 8080, "protos": ("tcp",)}))

    def test_rule_with_port_and_proto(self):
        rule = {"to": ipaddress.ip_network("10.0.0.153/32"), "port": 53, "proto": "udp"}
        self.assertTrue(t.p1_rule_matches(rule, {"host": "10.0.0.153", "port": 53, "protos": ("udp", "tcp")}))
        self.assertFalse(t.p1_rule_matches(rule, {"host": "10.0.0.153", "port": 53, "protos": ("tcp",)}))
        self.assertFalse(t.p1_rule_matches(rule, {"host": "10.0.0.153", "port": 54, "protos": ("udp",)}))

    def test_classify(self):
        self.assertEqual(t.classify("allow", "allow", "x", False, True), "kept (allow)")
        self.assertEqual(t.classify("allow", "deny", "x", False, True), "narrowed (allow -> deny)")
        self.assertEqual(t.classify("allow", "deny", "x", True, True), "enforcement moved (workload -> network)")
        self.assertEqual(t.classify("allow", "deny", "x", False, False), "dropped (no counterpart)")
        self.assertEqual(t.classify("deny", "allow", "x", False, True), "widened (deny -> allow)")

    def test_deny_layer(self):
        self.assertEqual(t.deny_layer('FATAL:  permission denied for database "labdb"'), "database")
        self.assertEqual(t.deny_layer("An error occurred (AccessDenied) when calling"), "iam")
        self.assertEqual(t.deny_layer("connection failed: timed out"), "network")
        self.assertEqual(t.deny_layer("port 5432 failed: Connection refused"), "network")
        self.assertEqual(t.deny_layer("exit 1: something else"), "other")


class FailureInjection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for rel in INPUTS:
            src, dst = os.path.join(REPO, rel), os.path.join(self.tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(src):     # matrix files and results only (no virtualenv)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".venv", "__pycache__"))
            else:
                shutil.copy(src, dst)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_tool(self):
        out = os.path.join(self.tmp, "out")
        r = subprocess.run([sys.executable, os.path.join(ANALYSIS, "translation.py"),
                            "--repo", self.tmp, "--out", out], capture_output=True, text=True)
        return r.returncode, r.stdout

    def edit(self, rel, old, new):
        path = os.path.join(self.tmp, rel)
        with open(path) as fh:
            text = fh.read()
        self.assertIn(old, text)
        with open(path, "w") as fh:
            fh.write(text.replace(old, new, 1))

    def test_unchanged_inputs_pass(self):
        rc, out = self.run_tool()
        self.assertEqual(rc, 0, out)
        self.assertNotIn("FAIL", out)

    def test_live_ruleset_drift(self):
        self.edit("journal/phase-1.md", "10.0.0.73 5432/tcp", "10.0.0.73 5433/tcp")
        rc, out = self.run_tool()
        self.assertEqual(rc, 1)
        self.assertIn("FAIL  Phase 1: declared ruleset = live ruleset", out)

    def test_ziti_and_netbird_tables_differ(self):
        self.edit("ansible-openziti/group_vars/all/vars.yaml",
                  "dial_roles: [remote-admin]          # segment-and-proxy",
                  "dial_roles: [remote-admin, remote-developer]  # segment-and-proxy")
        rc, out = self.run_tool()
        self.assertEqual(rc, 1)
        self.assertIn("FAIL  OpenZiti dial table = NetBird service table", out)
        self.assertIn("FAIL  phase-2-openziti: network entitlements agree", out)

    def test_deployed_netbird_policy_differs(self):
        path = os.path.join(self.tmp, "ansible-netbird/policies-export.json")
        with open(path) as fh:
            export = json.load(fh)
        legacy = next(p for p in export if p["name"] == "legacy-service")
        legacy["rules"][0]["sources"].append({"id": "x", "name": "remote-contractor"})
        with open(path, "w") as fh:
            json.dump(export, fh)
        rc, out = self.run_tool()
        self.assertEqual(rc, 1)
        self.assertIn("FAIL  NetBird service table = deployed policies", out)
        self.assertIn("FAIL  phase-2-netbird: network entitlements agree", out)

    def test_journal_missing_ziti_object(self):
        self.edit("journal/phase-2.md", '"created service-policy legacy-service-dial",', "")
        rc, out = self.run_tool()
        self.assertEqual(rc, 1)
        self.assertIn("FAIL  OpenZiti: objects from the service table", out)


if __name__ == "__main__":
    unittest.main()
