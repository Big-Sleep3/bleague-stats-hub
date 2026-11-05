"""Browser smoke test for ADVANCED LAB against real repo snapshot.

Run with: python -m unittest discover -s tests -p test_advanced_browser.py -v
Requires playwright + installed Chromium (run only in dedicated GitHub Action).
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class AdvancedLabBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise unittest.SkipTest("Playwright not installed")
        cls.sync_playwright = sync_playwright
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.server_thread = threading.Thread(
            target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_all_teams_players_translation_and_csv(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            url = "http://127.0.0.1:%s/advanced-lab.html" % self.server.server_port
            page.goto(url, wait_until="networkidle")
            self.assertEqual(page.locator("#tbody tr").count(), 26)
            self.assertIn("26", page.locator("#count").inner_text())
            page.locator("#playerBtn").click()
            self.assertGreaterEqual(page.locator("#tbody tr").count(), 300)
            page.locator("#langBtn").click()
            self.assertIn("Player Advanced Stats", page.locator("#tableTitle").inner_text())
            page.locator("#query").fill("Tominaga")
            self.assertGreaterEqual(page.locator("#tbody tr").count(), 1)
            with page.expect_download() as downloaded:
                page.locator("#csvBtn").click()
            self.assertTrue(downloaded.value.suggested_filename.endswith(".csv"))
            self.assertEqual(errors, [])
            context.close()
            browser.close()


if __name__ == "__main__":
    unittest.main()
