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
