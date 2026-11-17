"""Opponent scoring-mix validation; PITP is separate from the three-way split."""
import unittest


def scoring_mix(fgm, fga, threes_made, threes_attempted, ftm, pts, pitp=None):
    vals = (fgm, fga, threes_made, threes_attempted, ftm, pts)
    if any(type(v) is not int or v < 0 for v in vals):
        raise ValueError("nonnegative integer box-score counts required")
    if not (threes_made <= threes_attempted <= fga and threes_made <= fgm <= fga):
        raise ValueError("inconsistent field goals")
    twos_made = fgm - threes_made
    if twos_made > fga - threes_attempted:
        raise ValueError("2PM exceeds 2PA")
    points = (2 * twos_made, 3 * threes_made, ftm)
    if sum(points) != pts:
        raise ValueError("points do not reconcile with box score")
    if pitp is not None and (type(pitp) is not int or pitp < 0 or pitp > points[0]):
        raise ValueError("paint points must be subset of two-point points")
    if pts == 0:
        return {"two_pct": None, "three_pct": None, "ft_pct": None, "pitp_pct": None}
    return {"two_pct": 100 * points[0] / pts,
            "three_pct": 100 * points[1] / pts,
            "ft_pct": 100 * points[2] / pts,
            "pitp_pct": None if pitp is None else 100 * pitp / pts}


class TestOpponentScoringMix(unittest.TestCase):
    def test_three_shares_sum_to_100_paint_is_separate(self):
        result = scoring_mix(35, 70, 10, 25, 15, 95, pitp=36)
        self.assertAlmostEqual(sum(result[k] for k in ("two_pct", "three_pct", "ft_pct")), 100)
        self.assertAlmostEqual(result["pitp_pct"], 36 / 95 * 100)

    def test_missing_paint_stays_missing(self):
        self.assertIsNone(scoring_mix(1, 2, 0, 0, 0, 2)["pitp_pct"])

    def test_zero_points_stays_missing(self):
        self.assertTrue(all(v is None for v in scoring_mix(0, 0, 0, 0, 0, 0).values()))

    def test_inconsistent_points_rejected(self):
        with self.assertRaises(ValueError):
            scoring_mix(1, 2, 0, 0, 0, 3)

    def test_impossible_two_point_attempts_rejected(self):
        with self.assertRaises(ValueError):
            scoring_mix(5, 5, 2, 4, 0, 12)

    def test_paint_cannot_exceed_two_point_points(self):
        with self.assertRaises(ValueError):
            scoring_mix(1, 2, 0, 0, 0, 2, pitp=4)


if __name__ == "__main__":
    unittest.main()
