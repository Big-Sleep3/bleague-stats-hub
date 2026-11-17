"""Regression guard: current roster IDs and English names must stay synchronized.

Run: python -m unittest discover -s tests -p 'test_roster_mapping_consistency.py'
"""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]


class RosterMappingConsistency(unittest.TestCase):
    def test_current_roster_mapping(self):
        stats = json.loads((ROOT / "data/stats.json").read_text(encoding="utf-8"))
        mapping = json.loads((ROOT / "data/player-names-en.json").read_text(encoding="utf-8"))
        players = stats["players"]
        names = mapping["names"]
        self.assertEqual(len(stats["basic"]), 26)
        self.assertEqual(len(stats["advanced"]), 26)
        self.assertEqual(mapping["total_players"], len(names))
        self.assertEqual(mapping["verified"] + mapping["pending_count"], len(names))
        self.assertEqual(len(players), len(names), "Current roster mapping must be complete")
        seen = set()
        forbidden = {"menu", "home", "schedule", "roster", "stats", "login", "news", "more"}
        for player in players:
            pid = parse_qs(urlparse(player["url"]).query).get("PlayerID", [None])[0]
            self.assertIsNotNone(pid, player["url"])
            self.assertRegex(pid, r"^[0-9]+$")
            self.assertNotIn(pid, seen, f"Duplicate player ID {pid}")
            seen.add(pid)
            self.assertIn(pid, names, f"Missing English name for {pid}")
            english = names[pid]
            self.assertIsInstance(english, str)
            self.assertTrue(english.strip())
            self.assertNotIn(english.strip().lower(), forbidden)
            self.assertTrue(re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", english), english)
            self.assertEqual(player.get("name_en"), english, f"English name mismatch: {pid}")
        self.assertEqual(seen, set(names), "Stale IDs or unlisted roster players")


if __name__ == "__main__":
    unittest.main()
