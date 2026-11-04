# Defensive statistics implementation contract

Status: design + source audit in progress. No fabricated defensive numbers.

## Existing dataset audit (2026-11-04)
- `data/stats.json` advanced team records include `DEFRTG`, but the existing `%PTS2PT`, `%PTS3PT`, `%PTSFT`, `%PTSPITP`, `%FGA2PT`, and `%FGA3PT` are **own offense** figures, not opponent figures.
- Existing 26-club team aggregate records alone cannot reconstruct opponent 2PA, 3PA, ORB, or shot zones.
- Source opponent box scores by season/game ID, not by subtracting existing team aggregate columns.

## New output: data/defense.json
Versioned, independently refreshable; `season`, `updated`, `source`, `clubs`, `quality`.
Each club: stable ID, games counted, opponent totals and per-game stats, derived rates, timestamp provenance, completeness flag, warnings.

## Derivations
- Opp 2PM = Opp FGM - Opp 3PM; Opp 2PA = Opp FGA - Opp 3PA.
- Opp 2P% = Opp 2PM / Opp 2PA; Opp 3P% = Opp 3PM / Opp 3PA.
- Opp eFG% = (Opp FGM + 0.5 * Opp 3PM) / Opp FGA.
- Opp ORB% = Opp ORB / (Opp ORB + own DREB) where both game-level counts exist.
- Opp FTr = Opp FTA / Opp FGA.
- Opp 2PT points = 2 * Opp 2PM; 3PT points = 3 * Opp 3PM; FT points = Opp FTM.
- Scoring share denominator = Opp 2PT points + Opp 3PT points + Opp FT points; these three shares sum to 100%.
- PITP is a subset of 2PT scoring; show separate Opp PITP / Opp PTS, never add to three-way share.
- Opp TOV% and DEF RTG must use a documented possession convention consistently across clubs; do not derive from incomplete data.
- Shot zones require official play-by-play with shot locations or shot-chart data; otherwise N/A.

## Validation
- 26 clubs and each scheduled completed game appears once per side.
- Per-game Opp PTS equals opposing team actual scored points.
- FGA=2PA+3PA; PTS=2*2PM+3*3PM+FTM; percentages in [0,100].
- No partial values presented as full-season. Show source and coverage.
- Refresh timestamps do not increment data-change revision unless substantive numeric or roster values change.
- Preserve existing UI, sorting, ranking, Japanese/English toggles, and notifications.

## Planned UI
DEFENSE tab; all 26 clubs sortable; totals/per-game toggle; ranks (lower-is-better for allowed efficiency, higher-is-better for forced turnovers); opponent FGM/FGA, 2PM/2PA, 3PM/3PA, FT, ORB, ORB%, PITP, eFG%, DEFRTG; 2PT/3PT/FT scoring mix; shot-zone section only when verified.
