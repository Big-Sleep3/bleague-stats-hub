#!/usr/bin/env python3
"""Collect verified 2026-27 B.PREMIER opponent defense from B.LEAGUE game summaries.

Separate from the existing 26-team/player updater: it never writes stats.json or
last-data-change.json, so UI-only checks cannot trigger normal stats notifications.

Game contexts are the official game's publicly exposed S3 JSON snapshots; only
finished/fixed games with matching game IDs, season, teams and reconciled scores
enter the 26-club totals. Missing optional stats stay null, never zero.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from scripts.defensive_stats import aggregate_verified_opponents
from scripts.update_stats import club

ROOT = Path(__file__).resolve().parents[1]
SEASON = "2026-27"
START = dt.date(2026, 10, 1)
JST = ZoneInfo("Asia/Tokyo")
CACHE = ROOT / "data/defense-games.json"
OUTPUT = ROOT / "data/defense.json"
STATS = ROOT / "data/stats.json"
S3 = "https://b-league.s3.amazonaws.com/web_json"
SCHEDULE = "https://www.bleague.jp/schedule/"
CORE = {
    "FGM": "PTM", "FGA": "PTA", "3PM": "PT3M", "3PA": "PT3A",
    "FTM": "FTM", "FTA": "FTA",
}
OPTIONAL = {
    "TOV": "TO", "OREB": "RB_OFF", "PITP": "PT2IN",
    "SECOND_CHANCE_PTS": "PT2ND",
}


def now_jst():
    return dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")


def integer(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"\s*\d+\s*", value):
        return int(value.strip())
    return None


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_if_changed(path, obj):
    # Data timestamps are updated only when verified numeric/game values change.
    raw = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == raw:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(raw, encoding="utf-8")
    tmp.replace(path)
    return True


def month_day_pairs(today):
    month = START.replace(day=1)
    last = today.replace(day=1)
    while month <= last:
        yield month.year, month.month
        month = (month.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def schedule_url(year, month, day):
    return SCHEDULE + "?" + urlencode({
        "tab": 1, "year": 2026, "event": 2, "mon": f"{month:02d}",
        "day": f"{day:02d}",
    })


def discover_month(page, year, month):
    # The official schedule carries a list of days with matches in the month.
    page.goto(schedule_url(year, month, 1), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(400)
    soup = BeautifulSoup(page.content(), "html.parser")
    years = soup.select('select[name="year"] option[selected]')
    if years and years[0].get("value") != "2026":
        raise ValueError("Schedule year mismatch")
    days = sorted({
        integer(a.get("data-day"))
        for a in soup.select("a.js_click_data[data-day]")
        if integer(a.get("data-day")) is not None
    })
    return [day for day in days if 1 <= day <= 31]


def discover_day(page, year, month, day):
    page.goto(schedule_url(year, month, day), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(350)
    soup = BeautifulSoup(page.content(), "html.parser")
    ul = soup.select_one("#schedule-b1")
    if not ul:
        raise ValueError("Official B.PREMIER schedule list missing")
    out = []
    for item in ul.select("li.list-item"):
        a = item.select_one("a.data-game[href*='ScheduleKey=']")
        if not a:
            continue
        key = integer(parse_qs(urlparse(a["href"]).query).get("ScheduleKey", [None])[0])
        home = item.select_one("span.team.home span.team-name")
        away = item.select_one("span.team.away span.team-name")
        hs = item.select_one("span.home-score")
        aas = item.select_one("span.away-score")
        if not (key and home and away and hs and aas):
            continue
        home_code = club(home.get_text(" ", strip=True))
        away_code = club(away.get_text(" ", strip=True))
        hscore, ascore = integer(hs.get_text(strip=True)), integer(aas.get_text(strip=True))
        if home_code and away_code and home_code != away_code and hscore is not None and ascore is not None:
            out.append({
                "game_id": str(key),
                "date": f"{year:04}-{month:02}-{day:02}",
                "home_abbr": home_code,
                "away_abbr": away_code,
                "home_score": hscore,
                "away_score": ascore,
            })
    return out


def validated_summary(side, row, header_score):
    prefix = side.title() + "Team"
    info = {}
    for key, wire in CORE.items():
        value = integer(row.get(prefix + wire))
        if value is None:
            raise ValueError(f"Missing official {side} {wire}")
        info[key] = value
    info["PTS"] = header_score
    for key, wire in OPTIONAL.items():
        info[key] = integer(row.get(prefix + wire))
    if any(v is not None and v < 0 for v in info.values()):
        raise ValueError("Negative official summary value")
    two_m = info["FGM"] - info["3PM"]
    if (two_m < 0 or info["FGM"] > info["FGA"]
            or info["3PM"] > info["3PA"] or info["3PA"] > info["FGA"]
            or two_m > info["FGA"] - info["3PA"]
            or info["FTM"] > info["FTA"]
            or header_score != 2 * two_m + 3 * info["3PM"] + info["FTM"]):
        raise ValueError("Official game score does not reconcile with shooting")
    if info["PITP"] is not None and (info["PITP"] > 2 * two_m or info["PITP"] % 2):
        raise ValueError("Impossible paint points in official summary")
    if info["SECOND_CHANCE_PTS"] is not None and info["SECOND_CHANCE_PTS"] > header_score:
        raise ValueError("Impossible second-chance points in official summary")
    return info


def normalize_game(raw, fixture, retrieved_at):
    """Fail closed: verify game identity, regular season, final and both team summaries."""
    game = raw.get("Game") if isinstance(raw, dict) else None
    if not isinstance(game, dict):
        raise ValueError("Missing official Game")
    key = integer(game.get("ScheduleKey"))
    if str(key) != fixture["game_id"] or integer(game.get("Year")) != 2026:
        raise ValueError("Official game identity/season mismatch")
    event = integer(game.get("Event"))
    if event is not None and event != 2:
        raise ValueError("Not the regular-season league event")
    if game.get("GameEndedFlg") is not True or game.get("RecordFixedFlg") is not True:
        raise ValueError("Not a finished and fixed game")
    home = club(game.get("HomeTeamNameJ")) or club(game.get("HomeTeamShortNameJ"))
    away = club(game.get("AwayTeamNameJ")) or club(game.get("AwayTeamShortNameJ"))
    if home != fixture["home_abbr"] or away != fixture["away_abbr"]:
        raise ValueError(f"Wrong teams: {home!r} / {away!r}")
    hscore = integer(game.get("HomeTeamScore"))
    ascore = integer(game.get("AwayTeamScore"))
    if hscore != fixture["home_score"] or ascore != fixture["away_score"]:
        raise ValueError("Game header differs from schedule final score")
    rows = [r for r in raw.get("Summaries", []) if isinstance(r, dict)
            and integer(r.get("PeriodCategory")) == 18]
    if len(rows) != 1:
        raise ValueError("Expected exactly one full-game team summary")
    row = rows[0]
    if integer(row.get("ScheduleKey")) not in (None, key):
        raise ValueError("Summary game ID mismatch")
    hid, aid = str(game.get("HomeTeamID", "")), str(game.get("AwayTeamID", ""))
    if not hid or not aid or hid == aid:
        raise ValueError("Invalid two-team IDs")
    if row.get("HomeTeamID") is not None and str(row["HomeTeamID"]) != hid:
        raise ValueError("Summary home ID mismatch")
    if row.get("AwayTeamID") is not None and str(row["AwayTeamID"]) != aid:
        raise ValueError("Summary away ID mismatch")
    h = validated_summary("home", row, hscore)
    a = validated_summary("away", row, ascore)
    hdreb = integer(row.get("HomeTeamRB_DEF"))
    adreb = integer(row.get("AwayTeamRB_DEF"))
    if hdreb is None or adreb is None:
        raise ValueError("Both teams' defensive rebounds required")
    return {
        **fixture,
        "home_id": hid, "away_id": aid,
        "home": {"box": h, "dreb": hdreb},
        "away": {"box": a, "dreb": adreb},
        "retrieved_at": retrieved_at,
        "official_published_at": None,
        "source_url": f"https://www.bleague.jp/game_detail/?ScheduleKey={key}&tab=4",
    }


def fetch_game(request, fixture):
    # Try B.LEAGUE's public v2 game context and only fall back when not found.
    key = fixture["game_id"]
    for feed in ("v2_genius_contexts", "v1_contexts"):
        base = f"{S3}/{feed}/{key}"
        resp = request.get(base + "/latestid", timeout=35000)
        if resp.status in (403, 404):
            continue
        if resp.status != 200:
            raise ValueError(f"Official pointer HTTP {resp.status}")
        latest = resp.text().strip()
        if not re.fullmatch(r"\d{1,9}", latest):
            raise ValueError("Invalid official snapshot pointer")
        r = request.get(f"{base}/{latest}.json", timeout=35000)
        if r.status != 200:
            raise ValueError(f"Official game HTTP {r.status}")
        return normalize_game(r.json(), fixture, now_jst())
    raise ValueError("Official game context not found")


def aggregate_clubs(stats, game_cache, schedule_games, errors):
    references = stats["advanced"]
    expected = {r["abbr"]: int(r["gp"]) for r in references}
    names = {r["abbr"]: r["name"] for r in references}
    if len(expected) != 26:
        raise ValueError("Stats reference does not contain 26 unique clubs")
    records = {}
    for g in game_cache.values():
        key = g.get("game_id")
        for team_side in ("home", "away"):
            own, other = team_side, "away" if team_side == "home" else "home"
            code = g.get(team_side + "_abbr")
            if code not in expected:
                continue
            item = g[other]["box"]
            records.setdefault(code, []).append({
                "game_id": key,
                "season": SEASON,
                "opponent_box": {k: item.get(k) for k in
                    ("FGM", "FGA", "3PM", "3PA", "FTM", "FTA", "PTS", "TOV", "OREB", "PITP")},
                "team_dreb": g[own]["dreb"],
                "opponent_2nd": item.get("SECOND_CHANCE_PTS"),
            })
    scheduled = {code: set() for code in expected}
    for g in schedule_games.values():
        for side in ("home", "away"):
            code = g.get(side + "_abbr")
            if code in scheduled:
                scheduled[code].add(g["game_id"])
    output = []
    for code in sorted(expected):
        games = sorted(records.get(code, []), key=lambda g: str(g["game_id"]))
        verified = len(games)
        gp = expected[code]
        complete = (verified == gp and len(scheduled[code]) == gp
                    and not any(g["game_id"] in errors for g in games))
        metrics = None
        warning = None
        if games:
            try:
                aggregate = aggregate_verified_opponents(games)
                second = [g["opponent_2nd"] for g in games]
                second_ok = all(v is not None for v in second)
                second_total = sum(second) if second_ok else None
                metrics = {
                    **{k: v for k, v in aggregate.items()
                       if k.startswith("opp_") and k not in ("opp_pts_2pt_share", "opp_pts_3pt_share", "opp_pts_ft_share")},
                    "opp_second_chance_pts": second_total,
                    "opp_second_chance_pts_pg": second_total / verified if second_ok else None,
                    "opp_oreb_pg": aggregate.get("opp_oreb") / verified if aggregate.get("opp_oreb") is not None else None,
                    "opp_2pa_pg": aggregate.get("opp_2pa") / verified if aggregate.get("opp_2pa") is not None else None,
                    "opp_3pa_pg": aggregate.get("opp_3pa") / verified if aggregate.get("opp_3pa") is not None else None,
                }
            except ValueError as e:
                warning = str(e)
                complete = False
        missing = sorted(scheduled[code] - {g["game_id"] for g in games})
        output.append({
            "abbr": code, "name": names[code], "gp": verified,
            "expected_gp": gp, "scheduled_gp": len(scheduled[code]),
            "complete": complete, "metrics": metrics,
            "missing_game_ids": missing[:30],
            "warning": warning or ("Partial official game coverage; ranks exclude this club" if not complete else None),
        })
    return output


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full-refresh", action="store_true", help="re-check all verified game snapshots")
    ap.add_argument("--max-new", type=int, default=500, help="guardrail on official game requests")
    args = ap.parse_args()
    today = dt.datetime.now(JST).date()
    reference = read_json(STATS, {})
    old_cache = read_json(CACHE, {"schema": 1, "season": SEASON, "games": {}, "schedule_games": {}})
    if old_cache.get("season") != SEASON:
        raise ValueError("Defense cache is not for this season")
    games = dict(old_cache.get("games", {}))
    discovered = dict(old_cache.get("schedule_games", {}))
    errors = {}
    requests_made = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(locale="ja-JP", timezone_id="Asia/Tokyo")
        for year, month in month_day_pairs(today):
            try:
                days = discover_month(page, year, month)
            except Exception as exc:
                print(f"Could not discover {year}-{month:02d}: {exc}", flush=True)
                continue
            for day in days:
                date = dt.date(year, month, day)
                if date >= today:
                    continue
                try:
                    day_games = discover_day(page, year, month, day)
                    for g in day_games:
                        if g["home_abbr"] in {x["abbr"] for x in reference["advanced"]} and g["away_abbr"] in {x["abbr"] for x in reference["advanced"]}:
                            discovered[g["game_id"]] = g
                except Exception as exc:
                    print(f"Could not parse schedule {date}: {exc}", flush=True)
        # Avoid hitting B.LEAGUE repeatedly for already verified past games.
        for key, fixture in sorted(discovered.items(), key=lambda kv: (kv[1]["date"], kv[0])):
            if requests_made >= args.max_new:
                break
            old = games.get(key)
            if old and not args.full_refresh:
                continue
            requests_made += 1
            try:
                new = fetch_game(page.request, fixture)
                old_comparable = {k: v for k, v in old.items() if k != "retrieved_at"} if old else {}
                new_comparable = {k: v for k, v in new.items() if k != "retrieved_at"}
                if old_comparable != new_comparable:
                    games[key] = new
                print(f"Verified official game {key}", flush=True)
            except Exception as exc:
                errors[key] = str(exc)
                print(f"Unavailable/incomplete game {key}: {exc}", flush=True)
        browser.close()
    clubs = aggregate_clubs(reference, games, discovered, errors)
    # Metadata timestamps only move when substantive game values or club rows change.
    new_cache = {"schema": 1, "season": SEASON, "schedule_games": discovered, "games": games}
    changed_cache = write_if_changed(CACHE, new_cache)
    previous = read_json(OUTPUT, {})
    comparison = {"schema": 1, "season": SEASON, "clubs": clubs}
    was = {k: previous.get(k) for k in comparison}
    if comparison != was:
        document = {
            **comparison, "updated_at": now_jst(),
            "official_published_at": None,
            "source": "B.LEAGUE official season game schedule and official game Summaries (PeriodCategory=18)",
            "source_urls": [SCHEDULE, "https://www.bleague.jp/game_detail/"],
            "notes": "Verified completed regular-season games only. Partial rows are not ranked. Official posting timestamp is not provided by the game summary; date here is retrieval only.",
        }
        write_if_changed(OUTPUT, document)
    print(json.dumps({
        "verified_games": len(games), "scheduled_games": len(discovered),
        "complete_clubs": sum(bool(c["complete"]) for c in clubs),
        "errors_this_run": len(errors), "cache_changed": changed_cache,
        "report_changed": comparison != was,
    }, ensure_ascii=False))
    if not games:
        # Retain an explicitly empty, honest 26-club report; no fabricated stats.
        print("No game verified: inspect official source availability", flush=True)


if __name__ == "__main__":
    main()
