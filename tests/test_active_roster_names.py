"""Roster/name-map integrity regression tests (no fixed player count)."""
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(players, mapping):
    ids = []
    for player in players:
        match = re.search(r"[?&]PlayerID=(\d+)(?:&|$)", player.get("url", ""))
        if not match:
            raise ValueError("Missing official PlayerID")
        ids.append(match.group(1))
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate player ID")
    names = mapping["names"]
    missing = sorted(set(ids) - set(names))
    if missing:
        raise ValueError("Missing current player English names: " + ", ".join(missing))
    active = [names[pid] for pid in ids]
    normalized = [re.sub(r"\s+", " ", unicodedata.normalize("NFKC", n)).strip().casefold() for n in active]
    if any(not n for n in normalized) or len(normalized) != len(set(normalized)):
        raise ValueError("Empty or duplicate active English name")
    blocked = {"players", "tickets", "schedule", "statistics", "login", "merchandise"}
    if any(set(n.split()) & blocked for n in normalized):
        raise ValueError("Navigation label ingested as player name")
    return sorted(set(names) - set(ids))


class RosterNameMapTests(unittest.TestCase):
    def test_current_dataset(self):
        stats = json.loads((ROOT / "data/stats.json").read_text(encoding="utf-8"))
        mapping = json.loads((ROOT / "data/player-names-en.json").read_text(encoding="utf-8"))
        stale = audit(stats["players"], mapping)
        if stale:
            print("Historical IDs outside current player stats (not counted as active):", ", ".join(stale))

    def test_reject_missing_and_duplicate(self):
        players = [{"url": "https://www.bleague.jp/roster_detail/?PlayerID=1"},
                   {"url": "https://www.bleague.jp/roster_detail/?PlayerID=2"}]
        mapping = {"names": {"1": "First Player", "2": "Second Player"}}
        self.assertEqual(audit(players, mapping), [])
        with self.assertRaisesRegex(ValueError, "Missing current"):
            audit(players, {"names": {"1": "First Player"}})
        with self.assertRaisesRegex(ValueError, "Duplicate player ID"):
            audit(players[:1] * 2, mapping)
        with self.assertRaisesRegex(ValueError, "duplicate active"):
            audit(players, {"names": {"1": "First Player", "2": "FIRST  PLAYER"}})
        with self.assertRaisesRegex(ValueError, "Navigation"):
            audit(players, {"names": {"1": "First Player", "2": "Tickets Schedule"}})


if __name__ == "__main__":
    unittest.main()
