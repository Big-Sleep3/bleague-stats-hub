import unittest
from scripts.defensive_stats import (opponent_shooting, opponent_four_factors,
                                     aggregate_verified_opponents)


class OpponentShootingTests(unittest.TestCase):
    def setUp(self):
        self.box = dict(FGM=30, FGA=70, **{"3PM": 10, "3PA": 30},
                        FTM=15, FTA=20, PTS=85, PITP=28)

    def test_shares_are_exclusive_and_pitp_separate(self):
        result = opponent_shooting(self.box)
        self.assertEqual((result["opp_2pm"], result["opp_2pa"]), (20, 40))
        self.assertAlmostEqual(sum(result[k] for k in
            ("opp_pts_2pt_share", "opp_pts_3pt_share", "opp_pts_ft_share")), 1)
        self.assertAlmostEqual(result["opp_pitp_share"], 28 / 85)
        self.assertAlmostEqual(result["opp_efg_pct"], 35 / 70)

    def test_missing_pitp_is_unknown_not_zero(self):
        self.box.pop("PITP")
        self.assertIsNone(opponent_shooting(self.box)["opp_pitp_share"])

    def test_invalid_points_fail_closed(self):
        self.box["PTS"] = 84
        with self.assertRaisesRegex(ValueError, "Inconsistent"):
            opponent_shooting(self.box)

    def test_incomplete_or_invalid_box_fails_closed(self):
        for field in ("FGA", "3PA", "FTM"):
            box = self.box.copy()
            del box[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                opponent_shooting(box)
        self.box["3PM"] = 40
        with self.assertRaises(ValueError):
            opponent_shooting(self.box)

    def test_zero_denominator_is_missing(self):
        box = dict(FGM=0, FGA=0, **{"3PM": 0, "3PA": 0},
                   FTM=0, FTA=0, PTS=0)
        result = opponent_shooting(box)
        self.assertIsNone(result["opp_efg_pct"])
        self.assertIsNone(result["opp_pts_2pt_share"])

    def test_pitp_cannot_exceed_two_point_scoring(self):
        self.box["PITP"] = 42
        with self.assertRaisesRegex(ValueError, "PITP"):
            opponent_shooting(self.box)


class OpponentFourFactorsTests(unittest.TestCase):
    def setUp(self):
        self.box = dict(FGM=30, FGA=70, **{"3PM": 10, "3PA": 30},
                        FTM=15, FTA=20, PTS=85, PITP=28,
                        TOV=12, OREB=11)

    def test_tov_and_oreb_percentage(self):
        result = opponent_four_factors(self.box, own_dreb=25)
        self.assertAlmostEqual(result["opp_tov_pct"], 12 / (70 + 0.44 * 20 + 12))
        self.assertAlmostEqual(result["opp_oreb_pct"], 11 / (11 + 25))
        self.assertAlmostEqual(result["opp_3par"], 30 / 70)
        self.assertEqual(result["opp_tov"], 12)

    def test_missing_optional_stats_are_unknown_not_zero(self):
        del self.box["TOV"]
        del self.box["OREB"]
        result = opponent_four_factors(self.box)
        self.assertIsNone(result["opp_tov_pct"])
        self.assertIsNone(result["opp_oreb_pct"])

    def test_invalid_optional_counts_are_rejected(self):
        self.box["TOV"] = -1
        with self.assertRaises(ValueError):
            opponent_four_factors(self.box)
        self.box["TOV"] = 12
        with self.assertRaises(ValueError):
            opponent_four_factors(self.box, own_dreb=-2)

    def test_season_rates_use_totals_not_average_of_rates(self):
        a = dict(self.box)
        b = dict(FGM=20, FGA=45, **{"3PM": 5, "3PA": 12},
                 FTM=6, FTA=8, PTS=51, PITP=20, TOV=8, OREB=5)
        games = [
            {"game_id": "101", "season": "2026-27",
             "opponent_box": a, "team_dreb": 25},
            {"game_id": "102", "season": "2026-27",
             "opponent_box": b, "team_dreb": 19},
        ]
        result = aggregate_verified_opponents(games)
        self.assertEqual(result["gp"], 2)
        self.assertEqual(result["opp_2pa"], (70 - 30) + (45 - 12))
        self.assertEqual(result["opp_tov"], 20)
        self.assertAlmostEqual(result["opp_tov_pct"],
                               20 / (115 + 0.44 * 28 + 20))
        self.assertAlmostEqual(result["opp_oreb_pct"], 16 / (16 + 44))
        self.assertEqual(result["opp_pts_pg"], 68)
        self.assertEqual(result["game_ids"], ["101", "102"])

    def test_partial_coverage_blocks_season_rates(self):
        a = dict(self.box)
        b = dict(self.box)
        del b["TOV"]
        games = [
            {"game_id": "101", "season": "2026-27",
             "opponent_box": a, "team_dreb": 25},
            {"game_id": "102", "season": "2026-27",
             "opponent_box": b, "team_dreb": None},
        ]
        result = aggregate_verified_opponents(games)
        self.assertIsNone(result["opp_tov_pct"])
        self.assertIsNone(result["opp_oreb_pct"])
        self.assertFalse(result["coverage"]["TOV"])
        self.assertFalse(result["coverage"]["team_dreb"])

    def test_duplicate_game_and_cross_season_are_rejected(self):
        a = {"game_id": "101", "season": "2026-27",
             "opponent_box": self.box, "team_dreb": 25}
        with self.assertRaisesRegex(ValueError, "duplicated game ID"):
            aggregate_verified_opponents([a, a])
        with self.assertRaisesRegex(ValueError, "game season"):
            aggregate_verified_opponents([{**a, "season": "2025-26"}])

    def test_missing_all_games_rejected(self):
        with self.assertRaises(ValueError):
            aggregate_verified_opponents([])


if __name__ == "__main__":
    unittest.main()
