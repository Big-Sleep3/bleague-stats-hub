"""Smoke-test the actual DEFENSE dashboard, language, filter, sorting, and CSV."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class DefenseBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import playwright.sync_api
        except ImportError:
            raise unittest.SkipTest("Playwright is not installed")
        cls.http = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()

    def test_sort_direction_dropdown_and_column_click_keep_csv_and_ranks_consistent(self):
        from playwright.sync_api import sync_playwright
        import csv
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto("http://127.0.0.1:%s/defense.html" % self.http.server_port,
                      wait_until="networkidle")
            self.assertEqual(page.locator("#rows tr").count(), 26)
            # Lowest opponent offensive-rebounding percentage comes first by default.
            page.locator("#sort").select_option("opp_oreb_pct")
            self.assertEqual(page.locator("#direction").input_value(), "asc")
            ascending = page.evaluate(
                "() => visible().filter(valid).map(r => value(r, 'opp_oreb_pct'))")
            self.assertEqual(ascending, sorted(ascending))
            first_asc = page.locator("#rows tr").first.locator("td").nth(1).inner_text()
            self.assertEqual(page.locator('#head th[aria-sort="ascending"]').count(), 1)
            # Explicit select control switches descending, with all clubs retained.
            page.locator("#direction").select_option("desc")
            descending = page.evaluate(
                "() => visible().filter(valid).map(r => value(r, 'opp_oreb_pct'))")
            self.assertEqual(descending, sorted(descending, reverse=True))
            self.assertEqual(len(descending), len(ascending))
            self.assertEqual(page.locator('#head th[aria-sort="descending"]').count(), 1)
            if ascending[0] != ascending[-1]:
                self.assertNotEqual(first_asc,
                                    page.locator("#rows tr").first.locator("td").nth(1).inner_text())
            # Header click toggles the SAME metric instead of ignoring the direction.
            page.locator("#head th button").filter(has_text="被ORB%" ).first.click()
            self.assertEqual(page.locator("#direction").input_value(), "asc")
            self.assertEqual(page.evaluate(
                "() => visible().filter(valid).map(r => value(r, 'opp_oreb_pct'))"),
                ascending)
            # Changing sort metric chooses its sensible default (forced TOV% = high first).
            page.locator("#sort").select_option("opp_tov_pct")
            self.assertEqual(page.locator("#direction").input_value(), "desc")
            page.locator("#direction").select_option("asc")
            self.assertEqual(page.evaluate(
                "() => visible().filter(valid).map(r => value(r, 'opp_tov_pct'))"),
                sorted(page.evaluate(
                    "() => visible().filter(valid).map(r => value(r, 'opp_tov_pct'))")))
            # CSV must use precisely the displayed order.
            first_club = page.locator("#rows tr").first.locator("td").nth(1).inner_text()
            with page.expect_download() as download:
                page.locator("#export").click()
            with open(download.value.path(), encoding="utf-8-sig", newline="") as fh:
                rows = list(csv.reader(fh))
            self.assertEqual(rows[1][1], first_club)
            self.assertEqual(len(rows), 27)
            page.locator("#search").fill("信州")
            self.assertEqual(page.locator("#rows tr").count(), 1)
            self.assertEqual(page.locator("#direction").input_value(), "asc")
            self.assertEqual(errors, [])
            browser.close()

    def test_26_clubs_filters_translation_and_csv(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto("http://127.0.0.1:%s/defense.html" % self.http.server_port,
                      wait_until="networkidle")
            self.assertEqual(page.locator("#rows tr").count(), 26)
            page.locator("#search").fill("信州")
            self.assertEqual(page.locator("#rows tr").count(), 1)
            page.locator("#en").click()
            self.assertIn("Opponent defense", page.locator("#heading").inner_text())
            page.locator("#search").fill("")
            self.assertEqual(page.locator("#rows tr").count(), 26)
            page.locator("#sort").select_option("opp_tov_pct")
            self.assertEqual(page.locator("#rows tr").count(), 26)
            page.locator("#group").select_option("rebound")
            self.assertEqual(page.locator("#head th").count(), 8)
            self.assertIn("Opp ORB%", page.locator("#head").inner_text())
            page.locator("#sort").select_option("opp_pts_off_tov")
            self.assertEqual(page.locator("#group").input_value(), "turnover")
            self.assertEqual(page.locator("#rows tr").count(), 26)
            page.locator("#group").select_option("all")
            self.assertGreaterEqual(page.locator("#head th").count(), 25)
            page.locator("#period").select_option("last5")
            self.assertIn("Last 5", page.locator("#summary").inner_text())
            self.assertEqual(page.locator("#rows tr").count(), 26)
            page.locator("#period").select_option("season")
            page.locator("#total").click()
            with page.expect_download() as download:
                page.locator("#export").click()
            self.assertEqual(download.value.suggested_filename,
                             "bleague-defense-2026-27.csv")
            self.assertEqual(errors, [])
            browser.close()


if __name__ == "__main__":
    unittest.main()
