"""Fail-closed checks for current roster and verified English-name map."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]


class RosterIntegrityTests(unittest.TestCase):
    def test_current_roster_has_one_verified_name_per_player_id(self):
        stats = json.loads((ROOT / "data/stats.json").read_text(encoding="utf-8"))
        mapping = json.loads((ROOT / "data/player-names-en.json").read_text(encoding="utf-8"))
        players = stats["players"]
        names = mapping["names"]
        self.assertEqual(len(stats["basic"]), 26)
        self.assertEqual(len(stats["advanced"]), 26)
        self.assertGreater(len(players), 200)
        ids = [parse_qs(urlparse(p.get("url", "")).query).get("PlayerID", [""])[0]
               for p in players]
        self.assertTrue(all(re.fullmatch(r"\d+", pid or "") for pid in ids))
        self.assertEqual(len(ids), len(set(ids)), "Duplicate PlayerID in roster")
        self.assertEqual(set(ids), set(names), "Missing or stale English-name mapping")
        self.assertEqual(mapping["verified"], len(names))
        self.assertEqual(mapping["total_players"], len(players))
        self.assertEqual(mapping["pending_count"], 0)
        blocked = {"ticket", "tickets", "schedule", "stats", "statistics",
                   "players", "player", "news", "shop", "login", "ranking",
                   "home", "away", "privacy", "policy", "merchandise"}
        for pid, name in names.items():
            with self.subTest(pid=pid):
                self.assertIsInstance(name, str)
                self.assertTrue(4 <= len(name.strip()) <= 85)
                self.assertTrue(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ.'’\-\s]+", name))
                self.assertTrue(2 <= len(name.split()) <= 7)
                self.assertFalse({w.lower().strip(".'’-") for w in name.split()} & blocked)
        for player, pid in zip(players, ids):
            if player.get("name_en"):
                self.assertEqual(player["name_en"], names[pid], pid)


if __name__ == "__main__":
    unittest.main()
