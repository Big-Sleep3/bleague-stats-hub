#!/usr/bin/env python3
"""Fail-closed checks for the published English player-name mapping.

Run: python -m unittest discover -s tests -p 'test_published_name_mapping.py'
No network or third-party packages required.
"""
import json
import re
import unittest
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
BLOCKED = {"ticket", "tickets", "schedule", "statistics", "ranking", "rankings",
           "privacy", "policy", "checkout", "register", "subscribe", "merchandise",
           "highlights", "results", "basketball", "players", "information", "login"}

class PublishedNameMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stats = json.loads((ROOT / "data/stats.json").read_text(encoding="utf-8"))
        cls.mapping = json.loads((ROOT / "data/player-names-en.json").read_text(encoding="utf-8"))

    def test_roster_and_mapping_integrity(self):
        players = self.stats["players"]
        names = self.mapping["names"]
        ids = [parse_qs(urlparse(p.get("url", "")).query).get("PlayerID", [""])[0]
               for p in players]
        self.assertTrue(players, "No players in current stats")
        self.assertTrue(all(re.fullmatch(r"\d+", pid or "") for pid in ids))
        self.assertEqual(len(ids), len(set(ids)), "Duplicate PlayerID in current roster")
        self.assertEqual(set(ids), set(names), "Missing or stale player name IDs")
        self.assertEqual(self.mapping["total_players"], len(ids))
        self.assertEqual(self.mapping["verified"], len(names))
        self.assertEqual(self.mapping["pending_count"], len(ids) - len(names))

    def test_names_are_nonempty_and_not_navigation_labels(self):
        names = self.mapping["names"]
        normalized = []
        for pid, name in names.items():
            self.assertTrue(isinstance(name, str) and name.strip(), pid)
            self.assertTrue(4 <= len(name.strip()) <= 85, pid)
            self.assertRegex(name.strip(), r"^[A-Za-zÀ-ÖØ-öø-ÿ.'’\-\s]+$")
            words = name.split()
            self.assertTrue(2 <= len(words) <= 7, pid)
            self.assertFalse(any(w.lower().strip(".'’-") in BLOCKED for w in words), pid)
            normalized.append(unicodedata.normalize("NFKC", " ".join(words)).casefold())
        duplicates = [name for name, count in Counter(normalized).items() if count > 1]
        self.assertEqual(duplicates, [], "Duplicate normalized English names need review")

if __name__ == "__main__":
    unittest.main()
