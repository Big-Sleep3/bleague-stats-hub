# University Recruiting Hub / 2026
Public site: recruiting/index.html
Private notes: recruiting/staff.html (requires Supabase project setup)

The public player dataset is Kanto men's Division 1 scoring-table athletes (initially 30), NOT every registered collegiate athlete. Stats source:
https://www.kcbbf.jp/game/stats/type/league/year/2026/league_id/408

Official data update workflow: .github/workflows/update-college-recruiting.yml
Scraper: scripts/update_college_recruiting.py
Runs regularly during JST evenings/night plus a midday check, commits ONLY on changed stats. When official table cannot be parsed or validation fails, the workflow fails and keeps the last verified file. Rankings do not change player IDs for known athletes. The 2026 season is explicitly fixed; don't mix other seasons with this dataset.

Staff-protected notes REQUIRE external setup:
1. Create a dedicated Supabase project, enable email magic-link authentication, and allow redirects to the exact recruiting/staff.html URL. Set production SMTP for real staff use (Supabase's default mail service is restricted).
2. Run recruiting/schema.sql from the trusted SQL editor.
3. In recruiting/supabase-config.js set ONLY the Supabase URL and public anon/publishable key. Never place a secret service_role key or passwords in client code or GitHub.
4. Invite/create each intended user in Supabase Auth > Users first; new users cannot sign themselves up through this site. An administrator must explicitly approve their exact Auth UUID in the recruiting_staff table as shown in the SQL comment.
5. Test an UNAPPROVED user is unable to SELECT/INSERT/UPDATE notes and test approval/revocation.

IMPORTANT: GitHub Pages HTML, scripts and public player stats are public even if the staff page has a login! Only notes in Supabase with RLS enabled are staff-restricted. The public board's localStorage notes are saved on the current device and do not sync to staff.html; use staff.html for shared notes. This version uses last-save-wins updates; hit Reload before editing to avoid accidental overwrites.

The college federation website may change its layout, so monitor failed Actions. Review permissions/terms before sharing film links, and do not publish nonpublic personal information in GitHub commits.

Security hardening (2026-10-28): authorization function is in a non-API-exposed `recruiting_private` schema; sign-in disables self-signup (`shouldCreateUser:false`). Ensure `recruiting_private` is NOT added to Supabase API exposed schemas. Confirm RLS deny/allow with actual test users before sharing private notes.
