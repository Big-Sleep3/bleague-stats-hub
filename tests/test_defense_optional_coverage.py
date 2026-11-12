"""Regression checks: optional BOX fields must never become fabricated zeroes.

Run: python -m unittest discover -s tests -p 'test_defense_optional_coverage.py'
"""
import unittest

from scripts.defensive_stats import aggregate_verified_opponents


def game(game_id, **optional):
    box = {"FGM": 20, "FGA": 50, "3PM": 5, "3PA": 20,
           "FTM": 10, "FTA": 12, "PTS": 55}
    box.update(optional)
    return {"game_id": game_id, "season": "2026-27",
            "opponent_box": box, "team_dreb": 25}


class OptionalCoverageTests(unittest.TestCase):
    def test_missing_tov_does_not_publish_partial_turnover_rate(self):
        result = aggregate_verified_opponents([
            game("1001", TOV=12, OREB=8),
            game("1002", OREB=7),
        ])
        self.assertEqual(result["gp"], 2)
        self.assertEqual(result["opp_pts"], 110)
        self.assertIsNone(result["opp_tov"])
        self.assertIsNone(result["opp_tov_pct"])
        self.assertFalse(result["coverage"]["TOV"])
        self.assertEqual(result["opp_oreb"], 15)
        self.assertTrue(result["coverage"]["OREB"])

    def test_missing_pitp_is_not_zero(self):
        result = aggregate_verified_opponents([
            game("1003", PITP=20), game("1004")
        ])
        self.assertIsNone(result["opp_pitp"])
        self.assertIsNone(result["opp_pitp_share"])
        self.assertFalse(result["coverage"]["PITP"])

    def test_complete_optional_fields_are_aggregated(self):
        result = aggregate_verified_opponents([
            game("1005", TOV=10, OREB=6, PITP=20),
            game("1006", TOV=14, OREB=8, PITP=22),
        ])
        self.assertEqual(result["opp_tov"], 24)
        self.assertEqual(result["opp_oreb"], 14)
        self.assertEqual(result["opp_pitp"], 42)
        self.assertAlmostEqual(result["opp_oreb_pct"], 14 / 64)
        self.assertTrue(all(result["coverage"].values()))


if __name__ == "__main__":
    unittest.main()
