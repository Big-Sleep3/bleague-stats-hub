"""Regression tests for B.PREMIER verified opponent-allowed metrics."""
import copy
import unittest

from scripts.update_defense import (
    normalize_game, validated_summary, aggregate_clubs,
)


def source_team(prefix, points=85, oreb=11, dreb=25, second=13):
    # 20 two-point makes + 10 triples + 15 FTs = 85 points.
    fields = {"PTM": 30, "PTA": 70, "PT3M": 10, "PT3A": 30,
              "FTM": 15, "FTA": 20, "TO": 12, "RB_OFF": oreb,
              "RB_DEF": dreb, "PT2IN": 28, "PT2ND": second,
              "PTFB": 9, "PTPFT": 13}
    return {prefix + k: v for k, v in fields.items()}


def fixture():
    return {
        "game_id": "5001", "date": "2026-11-01",
        "home_abbr": "信州", "away_abbr": "千葉J",
        "home_score": 85, "away_score": 85,
    }


def raw_game():
    return {
        "Game": {
            "ScheduleKey": 5001, "Year": 2026, "Event": 2,
            "GameEndedFlg": True, "RecordFixedFlg": True,
            "HomeTeamNameJ": "信州ブレイブウォリアーズ",
            "AwayTeamNameJ": "千葉ジェッツ",
            "HomeTeamScore": 85, "AwayTeamScore": 85,
            "HomeTeamID": 1, "AwayTeamID": 2,
        },
        "Summaries": [{
            "ScheduleKey": 5001, "PeriodCategory": 18,
            "HomeTeamID": 1, "AwayTeamID": 2,
            **source_team("HomeTeam", oreb=11, dreb=25, second=13),
            **source_team("AwayTeam", oreb=8, dreb=23, second=17),
        }],
    }


class VerifiedOpponentDefenseTest(unittest.TestCase):
    def test_full_game_own_and_opponent_remain_separate(self):
        item = normalize_game(raw_game(), fixture(), "2026-11-02 12:00 JST")
        self.assertEqual(item["away"]["box"]["SECOND_CHANCE_PTS"], 17)
        self.assertEqual(item["home"]["box"]["SECOND_CHANCE_PTS"], 13)
        self.assertEqual(item["away"]["box"]["OREB"], 8)
        self.assertEqual(item["away"]["box"]["FAST_BREAK_PTS"], 9)
        self.assertEqual(item["away"]["box"]["PTS_OFF_TOV"], 13)
        self.assertEqual(item["home"]["dreb"], 25)
        self.assertIsNone(item["official_published_at"])

    def test_reject_wrong_season_and_unfinished(self):
        raw = raw_game()
        raw["Game"]["Year"] = 2025
        with self.assertRaisesRegex(ValueError, "season"):
            normalize_game(raw, fixture(), "t")
        raw = raw_game()
        raw["Game"]["RecordFixedFlg"] = False
        with self.assertRaisesRegex(ValueError, "finished"):
            normalize_game(raw, fixture(), "t")

    def test_reject_bad_score_or_team(self):
        raw = raw_game()
        raw["Summaries"][0]["AwayTeamPTM"] = 39
        with self.assertRaisesRegex(ValueError, "score"):
            normalize_game(raw, fixture(), "t")
        raw = raw_game()
        raw["Game"]["AwayTeamNameJ"] = "群馬クレインサンダーズ"
        with self.assertRaisesRegex(ValueError, "Wrong teams"):
            normalize_game(raw, fixture(), "t")

    def test_missing_second_chance_is_null_not_zero(self):
        raw = raw_game()
        del raw["Summaries"][0]["AwayTeamPT2ND"]
        normalized = normalize_game(raw, fixture(), "t")
        self.assertIsNone(normalized["away"]["box"]["SECOND_CHANCE_PTS"])

    def test_calculations_from_26_club_reference(self):
        one = normalize_game(raw_game(), fixture(), "t")
        abbrs = ["信州", "千葉J"] + [f"C{i:02d}" for i in range(24)]
        ref = {"advanced": [
            {"abbr": a, "name": a, "gp": 1 if a in ("信州", "千葉J") else 0}
            for a in abbrs]}
        out = aggregate_clubs(ref, {"5001": one}, {"5001": fixture()}, {})
        shinshu = next(row for row in out if row["abbr"] == "信州")
        chiba = next(row for row in out if row["abbr"] == "千葉J")
        self.assertTrue(shinshu["complete"])
        self.assertEqual(shinshu["metrics"]["opp_second_chance_pts"], 17)
        self.assertEqual(shinshu["metrics"]["opp_fast_break_pts"], 9)
        self.assertEqual(shinshu["metrics"]["opp_pts_off_tov"], 13)
        self.assertAlmostEqual(shinshu["metrics"]["opp_fast_break_pts_share"], 9 / 85)
        self.assertAlmostEqual(shinshu["metrics"]["opp_pts_off_tov_share"], 13 / 85)
        self.assertAlmostEqual(shinshu["metrics"]["opp_second_chance_pts_per_oreb"], 17 / 8)
        self.assertAlmostEqual(shinshu["metrics"]["opp_pitp_share"], 28 / 85)
        self.assertAlmostEqual(shinshu["metrics"]["opp_2pt_scoring_share"], 40 / 85)
        self.assertAlmostEqual(shinshu["metrics"]["opp_3pt_scoring_share"], 30 / 85)
        self.assertAlmostEqual(shinshu["metrics"]["opp_ft_scoring_share"], 15 / 85)
        self.assertEqual(chiba["metrics"]["opp_second_chance_pts"], 13)
        self.assertAlmostEqual(shinshu["metrics"]["opp_oreb_pct"], 8 / (8 + 25))
        self.assertAlmostEqual(shinshu["metrics"]["opp_tov_pct"], 12 / (70 + .44 * 20 + 12))
        self.assertAlmostEqual(shinshu["metrics"]["opp_2p_pct"], 20 / 40)
        self.assertAlmostEqual(shinshu["metrics"]["opp_3p_pct"], 10 / 30)
        self.assertAlmostEqual(shinshu["metrics"]["opp_efg_pct"], 35 / 70)
        self.assertEqual(len(out), 26)

    def test_missing_game_blocks_ranking(self):
        one = normalize_game(raw_game(), fixture(), "t")
        names = ["信州", "千葉J"] + [f"C{i:02d}" for i in range(24)]
        ref = {"advanced": [
            {"abbr": a, "name": a, "gp": 2 if a == "信州" else (1 if a == "千葉J" else 0)}
            for a in names]}
        out = aggregate_clubs(ref, {"5001": one}, {"5001": fixture()}, {})
        shinshu = next(row for row in out if row["abbr"] == "信州")
        self.assertFalse(shinshu["complete"])
        self.assertEqual(shinshu["gp"], 1)
        self.assertIsNotNone(shinshu["metrics"])

    def test_partial_optional_points_do_not_publish_fake_season_totals(self):
        base = normalize_game(raw_game(), fixture(), "t")
        next_game = copy.deepcopy(base)
        next_game["game_id"] = "5002"
        next_game["away"]["box"]["FAST_BREAK_PTS"] = None
        next_game["away"]["box"]["PTS_OFF_TOV"] = None
        ref = {"advanced": [{"abbr": code, "name": code, "gp": (2 if code in ("信州", "千葉J") else 0)}
                for code in (["信州", "千葉J"] + [f"C{i:02d}" for i in range(24)])]}
        f2 = {**fixture(), "game_id": "5002"}
        clubs = aggregate_clubs(ref, {"5001": base, "5002": next_game},
                                 {"5001": fixture(), "5002": f2}, {})
        shinshu = next(row for row in clubs if row["abbr"] == "信州")
        self.assertTrue(shinshu["complete"])
        self.assertIsNone(shinshu["metrics"]["opp_fast_break_pts"])
        self.assertIsNone(shinshu["metrics"]["opp_pts_off_tov"])
        self.assertEqual(shinshu["metrics"]["opp_second_chance_pts"], 34)

    def test_summary_rejects_impossible_fast_break_and_pts_off_turnover(self):
        for key in ("AwayTeamPTFB", "AwayTeamPTPFT"):
            raw = raw_game()
            raw["Summaries"][0][key] = 100
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "Impossible"):
                normalize_game(raw, fixture(), "t")


    def test_recent_windows_are_last_completed_games_not_season_averages(self):
        records = {}
        fixtures = {}
        for i in range(6):
            match = fixture()
            match["game_id"] = str(5001 + i)
            match["date"] = "2026-11-%02d" % (i + 1)
            raw = raw_game()
            raw["Game"]["ScheduleKey"] = 5001 + i
            raw["Summaries"][0]["ScheduleKey"] = 5001 + i
            raw["Summaries"][0]["AwayTeamPTFB"] = 1 if i == 0 else 9
            fixtures[match["game_id"]] = match
            records[match["game_id"]] = normalize_game(raw, match, "t")
        names = ["信州", "千葉J"] + [f"C{i:02d}" for i in range(24)]
        ref = {"advanced": [{"abbr": name, "name": name,
                             "gp": 6 if name in ("信州", "千葉J") else 0} for name in names]}
        clubs = aggregate_clubs(ref, records, fixtures, {})
        shinshu = next(x for x in clubs if x["abbr"] == "信州")
        self.assertTrue(shinshu["complete"])
        self.assertEqual(shinshu["metrics"]["opp_fast_break_pts"], 46)
        self.assertEqual(shinshu["recent"]["last5"]["gp"], 5)
        self.assertEqual(shinshu["recent"]["last5"]["metrics"]["opp_fast_break_pts"], 45)
        self.assertEqual(shinshu["recent"]["last3"]["gp"], 3)
        self.assertEqual(shinshu["recent"]["last3"]["metrics"]["opp_fast_break_pts"], 27)
        self.assertEqual(shinshu["recent"]["last3"]["game_ids"], ["5004", "5005", "5006"])


if __name__ == "__main__":
    unittest.main()
