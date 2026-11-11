"""Fail-closed roster/name-map integrity checks; run with python -m unittest discover -s tests."""
import json
import re
import unittest
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]


def audit(players, names):
    ids = [parse_qs(urlparse(p.get("url", "")).query).get("PlayerID", [""])[0]
           for p in players]
    if not ids or any(not re.fullmatch(r"[0-9]+", pid) for pid in ids):
        raise ValueError("Missing or invalid roster PlayerID")
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate roster PlayerID")
    if set(ids) != set(names):
        raise ValueError("English name IDs differ from current roster IDs")
    canonical = [re.sub(r"\\s+", " ", unicodedata.normalize("NFKC", n)).strip().casefold()
                 for n in names.values()]
    if len(canonical) != len(set(canonical)):
        raise ValueError("Duplicate normalized English player name")
    blocked = {"ticket", "tickets", "schedule", "stats", "statistics", "login",
               "ranking", "rankings", "players", "merchandise", "highlights"}
    for name in names.values():
        if not isinstance(name, str) or len(name.split()) < 2:
            raise ValueError("Invalid English name")
        if any(w.strip(".'-").casefold() in blocked for w in name.split()):
            raise ValueError("Navigation/menu label in English names")


class RosterNameIntegrityTests(unittest.TestCase):
    def test_current_dataset(self):
        stats = json.loads((ROOT / "data/stats.json").read_text(encoding="utf-8"))
        mapping = json.loads((ROOT / "data/player-names-en.json").read_text(encoding="utf-8"))
        audit(stats["players"], mapping["names"])
        self.assertEqual(mapping["verified"], len(mapping["names"]))
        self.assertEqual(mapping["total_players"], len(stats["players"]))
        self.assertEqual(mapping["pending_count"], 0)

    def test_missing_and_stale_ids_rejected(self):
        roster = [{"url": "https://www.bleague.jp/roster_detail/?PlayerID=1"}]
        for names in ({}, {"2": "John Smith"}, {"1": "John Smith", "2": "Jane Doe"}):
            with self.subTest(names=names), self.assertRaises(ValueError):
                audit(roster, names)

    def test_duplicate_and_menu_names_rejected(self):
        roster = [{"url": "https://www.bleague.jp/roster_detail/?PlayerID=1"},
                  {"url": "https://www.bleague.jp/roster_detail/?PlayerID=2"}]
        for names in ({"1": "John Smith", "2": "JOHN  SMITH"},
                      {"1": "John Smith", "2": "Tickets Schedule"}):
            with self.subTest(names=names), self.assertRaises(ValueError):
                audit(roster, names)


if __name__ == "__main__":
    unittest.main()
