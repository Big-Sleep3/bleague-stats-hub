import unittest
from scripts.defensive_stats import opponent_shooting


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


if __name__ == "__main__":
    unittest.main()
