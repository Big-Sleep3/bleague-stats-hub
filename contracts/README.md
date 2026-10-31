# B.LEAGUE CONTRACT HUB — 2026-27

Public site: https://big-sleep3.github.io/bleague-stats-hub/contracts/
Approved-staff portal: https://big-sleep3.github.io/bleague-stats-hub/contracts/staff.html

## Scope and evidentiary standard
- Roster and box-score stats use `../data/stats.json` (2026-27 B.PREMIER; 26 clubs; roster snapshot). Players not in that JSON are not included. This is NOT a full league-wide registration database.
- `contracts.json` contains public contract evidence for a subset of these players. The relevant source URL, announcement date, start/end season and explicitly named options are attached individually.
- **Unverified does not mean one-year.** An unspecified option is not an absence of an option. Do not infer a guaranteed year from PO/TO season. End-year 2030 means last listed season 2029-30.
- Club press releases are marked `sourceType: "club"`. Media articles are marked `sourceType: "media"` and require further primary confirmation.
- Player matching uses normalized club plus player name, not only name. Contract records not present in the published roster remain out of the UI.
- All values reflect the source publication and may be superseded by new releases. Recheck source with player/club before initiating negotiations.
- Data source entry is curated; **there is no automatic 26-club contract terms scraper**. Official stats update independently via the existing STATS HUB.
- Privacy: **never** put internal notes, agent contact data, salary or scouting opinions into `contracts.json` or GitHub.

## Staff setup
- `staff.html` uses the existing Recruiting HUB Supabase project and only its public publishable key in `../recruiting/supabase-config.js`. It does not contain service-role credentials.
- Apply `contracts/schema.sql` in the existing Supabase project (already applied in this deployment).
- `bleague_contract_notes` has RLS, and reads/inserts/updates require approved `recruiting_staff` membership. Existing approved accounts, including invited staff, can log in.
- Add the **exact** `https://big-sleep3.github.io/bleague-stats-hub/contracts/staff.html` URL to Supabase **Authentication → URL Configuration → Redirect URLs**. The old University STAFF login redirect remains a separate authorized URL.
- Passwordless login does not create new users (`shouldCreateUser:false`); administrators must invite users separately and approve their UUID in `recruiting_staff`.
- The internal fields (priority, pipeline stage, target year, agent contact, internal contract questions, evaluation, next action) remain in the RLS-protected Supabase table. Public GitHub Pages displays no private notes.
- Last-write-wins when two staff edit the same player simultaneously. Confirm real multi-user browser syncing before production reliance.

## Updates
1. Check each team release, official league release, or reliable media report for contract term and option type.
2. Verify exact player + team from current `data/stats.json`, ensure announcement date/URL and option-year mapping are correct.
3. Update `contracts/contracts.json` only with evidence; leave missing terms `null` rather than guessing.
4. Browser tests are in `tests/test_contracts_browser.py`.
