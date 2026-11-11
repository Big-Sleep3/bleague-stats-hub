"""Pure, fail-closed calculations for verified opponent BOX SCORE totals.

No network access or assumed shot zones. Feed only season-matched official
game totals after the collector has verified unique game IDs and both sides.
"""
from collections import Counter

FIELDS = ("FGM", "FGA", "3PM", "3PA", "FTM", "FTA", "PTS")


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def opponent_shooting(box):
    """Return opponent shooting and non-overlapping scoring shares.

    Raises ValueError on inconsistent/missing official totals rather than
    publishing invented or incomplete defense statistics.
    """
    if not isinstance(box, dict) or any(k not in box for k in FIELDS):
        raise ValueError("Incomplete official opponent box score")
    if any(type(box[k]) is not int or box[k] < 0 for k in FIELDS):
        raise ValueError("Invalid official opponent box score count")
    fgm, fga, three_m, three_a = (box[k] for k in ("FGM", "FGA", "3PM", "3PA"))
    ftm, fta, pts = (box[k] for k in ("FTM", "FTA", "PTS"))
    two_m, two_a = fgm - three_m, fga - three_a
    if (two_m < 0 or two_a < 0 or
        two_m > two_a or three_m > three_a or
        fgm > fga or ftm > fta or
        pts != 2 * two_m + 3 * three_m + ftm):
        raise ValueError("Inconsistent official opponent box score")
    result = {
        "opp_2pm": two_m, "opp_2pa": two_a,
        "opp_2p_pct": ratio(two_m, two_a),
        "opp_3pm": three_m, "opp_3pa": three_a,
        "opp_3p_pct": ratio(three_m, three_a),
        "opp_ftm": ftm, "opp_fta": fta,
        "opp_ft_pct": ratio(ftm, fta),
        "opp_pts": pts,
        "opp_efg_pct": ratio(fgm + 0.5 * three_m, fga),
        "opp_ftr": ratio(fta, fga),
        "opp_pts_2pt_share": ratio(2 * two_m, pts),
        "opp_pts_3pt_share": ratio(3 * three_m, pts),
        "opp_pts_ft_share": ratio(ftm, pts),
    }
    if "PITP" in box and box["PITP"] is not None:
        pitp = box["PITP"]
        if type(pitp) is not int or pitp < 0 or pitp > 2 * two_m or pitp % 2:
            raise ValueError("Inconsistent official opponent PITP")
        result["opp_pitp"] = pitp
        result["opp_pitp_share"] = ratio(pitp, pts)
    else:
        result["opp_pitp"] = None
        result["opp_pitp_share"] = None
    return result


def opponent_four_factors(box, own_dreb=None):
    """Return verified opponent possession/second-chance measures.

    Turnover rate uses the conventional box-score Four Factors denominator
    TOV / (FGA + 0.44*FTA + TOV), NOT the published official possession count.
    OREB% uses opponent OREB / (opponent OREB + own team DREB).
    Missing optional fields stay None, never silently become zero.
    All percentages are fractions (0-1) for consumers to format.
    """
    result = opponent_shooting(box)
    for key in ("TOV", "OREB"):
        value = box.get(key)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("Invalid official opponent " + key)
    if own_dreb is not None and (type(own_dreb) is not int or own_dreb < 0):
        raise ValueError("Invalid official own DREB")
    tov = box.get("TOV")
    oreb = box.get("OREB")
    result.update({
        "opp_tov": tov,
        "opp_tov_pct": (ratio(tov, box["FGA"] + 0.44 * box["FTA"] + tov)
                        if tov is not None else None),
        "opp_oreb": oreb,
        "opp_oreb_pct": (ratio(oreb, oreb + own_dreb)
                         if oreb is not None and own_dreb is not None else None),
        "opp_3par": ratio(box["3PA"], box["FGA"]),
        "opp_fg_pct": ratio(box["FGM"], box["FGA"]),
    })
    return result


def aggregate_verified_opponents(games, season="2026-27"):
    """Aggregate verified official opponent BOX scores for one team's games.

    games: iterable of {game_id, season, opponent_box, team_dreb}.
    Duplicates, cross-season data and invalid core scores fail closed. Optional
    TOV/OREB/PITP and DREB must be complete across all games before publishing
    their season-level aggregates. Never average rounded game percentages.
    """
    games = list(games)
    if not games:
        raise ValueError("No official opponent games")
    seen = set()
    totals = {key: 0 for key in FIELDS}
    optional = ("TOV", "OREB", "PITP")
    opt_totals = {key: 0 for key in optional}
    complete = {key: True for key in optional}
    total_dreb = 0
    complete_dreb = True
    for game in games:
        if not isinstance(game, dict) or game.get("season") != season:
            raise ValueError("Unknown or inconsistent game season")
        raw_game_id = game.get("game_id")
        if type(raw_game_id) not in (str, int):
            raise ValueError("Invalid game ID type")
        # Official game IDs are positive decimal identifiers. Reject malformed
        # strings rather than silently normalizing them into valid IDs.
        game_id = str(raw_game_id)
        if (not game_id.isascii() or not game_id.isdecimal() or
                int(game_id) <= 0):
            raise ValueError("Missing, invalid or duplicated game ID")
        # Canonicalize decimal IDs before deduplication: 001 and 1 are
        # the same official game, even when upstream sources differ in type.
        game_id = str(int(game_id))
        if game_id in seen:
            raise ValueError("Missing, invalid or duplicated game ID")
        seen.add(game_id)
        box = game.get("opponent_box")
        opponent_shooting(box)  # validate every game's real scoring identity
        for key in FIELDS:
            totals[key] += box[key]
        for key in optional:
            value = box.get(key)
            if value is None:
                complete[key] = False
            elif type(value) is not int or value < 0:
                raise ValueError("Invalid official opponent " + key)
            else:
                opt_totals[key] += value
        own_dreb = game.get("team_dreb")
        if own_dreb is None:
            complete_dreb = False
        elif type(own_dreb) is not int or own_dreb < 0:
            raise ValueError("Invalid official own DREB")
        else:
            total_dreb += own_dreb
    for key in optional:
        if complete[key]:
            totals[key] = opt_totals[key]
    result = opponent_four_factors(
        totals, own_dreb=total_dreb if complete_dreb else None)
    result.update({
        "gp": len(games),
        "opp_pts_pg": totals["PTS"] / len(games),
        "game_ids": sorted(seen),
        "coverage": {key: complete[key] for key in optional},
    })
    result["coverage"]["team_dreb"] = complete_dreb
    return result
