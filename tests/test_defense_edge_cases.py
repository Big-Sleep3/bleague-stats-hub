"""Regression checks for defensive box-score fail-closed behavior."""
import unittest
from scripts.defensive_stats import aggregate_verified_opponents, opponent_four_factors


class DefenseEdgeCases(unittest.TestCase):
    def setUp(self):
        self.box = dict(FGM=2, FGA=5, **{"3PM": 1, "3PA": 3}, FTM=1,
                        FTA=2, PTS=6, TOV=0, OREB=0, PITP=2)

    def test_zero_rebound_chances_are_unknown(self):
        result = opponent_four_factors(self.box, own_dreb=0)
        self.assertIsNone(result["opp_oreb_pct"])
        self.assertEqual(result["opp_tov_pct"], 0)

    def test_partial_pitp_does_not_publish_season_share(self):
        second = dict(self.box)
        second.pop("PITP")
        games = [
            {"game_id": "1001", "season": "2026-27", "opponent_box": self.box, "team_dreb": 3},
            {"game_id": "1002", "season": "2026-27", "opponent_box": second, "team_dreb": 3},
        ]
        result = aggregate_verified_opponents(games)
        self.assertFalse(result["coverage"]["PITP"])
        self.assertIsNone(result["opp_pitp"])
        self.assertIsNone(result["opp_pitp_share"])

    def test_boolean_optional_counts_rejected(self):
        for field in ("TOV", "OREB", "PITP"):
            with self.subTest(field=field):
                box = dict(self.box)
                box[field] = True
                with self.assertRaises(ValueError):
                    opponent_four_factors(box, own_dreb=3)


if __name__ == "__main__":
    unittest.main()
