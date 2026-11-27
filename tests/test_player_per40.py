"""Player Per 40min browser regression: values, labels, sorting, CSV, filters."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class PlayerPer40BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import playwright.sync_api
        except ImportError:
            raise unittest.SkipTest("Playwright not installed")
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_player_per40_value_sort_csv_and_return_to_official_per_game(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto("http://127.0.0.1:%s/index.html" % self.server.server_port,
                      wait_until="networkidle")
            page.locator('[data-tab="players"]').click()
            self.assertTrue(page.locator("#modeWrap").evaluate(
                "(node) => node.classList.contains('hidden')"))
            self.assertTrue(page.locator("#playerRateWrap").is_visible())
            self.assertGreaterEqual(page.locator("#tbody tr").count(), 300)
            page.locator("#metric").select_option("PPG")
            self.assertEqual(page.evaluate('metricVal(data.players[0], "PPG")'), 23.9)
            page.locator("#playerPer40").click()
            self.assertEqual(page.locator("#playerPer40").get_attribute("aria-pressed"), "true")
            self.assertIn("PTS/40", page.locator("#thead").inner_text())
            expected = 23.9 * 18 * 40 / (513 + 3 / 60)
            observed = page.evaluate('metricVal(data.players[0], "PPG")')
            self.assertAlmostEqual(observed, expected, places=5)
            self.assertEqual(page.evaluate('metricVal(data.players[0], "FG%")'), 47.8)
            self.assertEqual(page.evaluate('metricVal(data.players[0], "G")'), 18.0)
            self.assertEqual(page.evaluate('metricVal(data.players[0], "MINPG")'), 28.5)
            self.assertEqual(page.evaluate('displayMetricLabel("RPG")'), "REB/40")
            self.assertEqual(page.evaluate('displayMetricLabel("APG")'), "AST/40")
            page.locator("#metric").select_option("RPG")
            self.assertIn("REB/40", page.locator("#tableTitle").inner_text())
            with page.expect_download() as download:
                page.locator("#csvBtn").click()
            self.assertEqual(download.value.suggested_filename,
                             "BPREMIER_2026-27_players_p40.csv")
            page.locator("#playerPerGame").click()
            self.assertEqual(page.evaluate('metricVal(data.players[0], "PPG")'), 23.9)
            self.assertEqual(page.locator("#playerPer40").get_attribute("aria-pressed"), "false")
            self.assertNotIn("REB/40", page.locator("#tableTitle").inner_text())
            page.locator('[data-tab="basic"]').click()
            self.assertFalse(page.locator("#playerRateWrap").is_visible())
            self.assertEqual(errors, [])
            browser.close()


if __name__ == "__main__":
    unittest.main()
