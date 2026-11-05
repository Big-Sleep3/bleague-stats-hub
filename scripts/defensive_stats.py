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
