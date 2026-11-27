"""Smoke-test the shared STATS HUB page switcher on desktop and mobile."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        return


class HubNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise unittest.SkipTest("playwright not installed")
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def base(self):
        return "http://127.0.0.1:%d/" % self.server.server_port

    def test_desktop_all_hub_pages_and_nested_routes(self):
        from playwright.sync_api import sync_playwright
        cases = [
            ("index.html#advanced", "advanced"),
            ("index.html#basic", "basic"),
            ("index.html#players", "players"),
            ("index.html#compare", "compare"),
            ("defense.html", "defense"),
            ("advanced-lab.html", "lab"),
            ("contracts/index.html", "contracts"),
            ("recruiting/index.html", "recruiting"),
            ("recruiting/sources.html", "recruiting"),
            ("recruiting/staff.html", "recruiting"),
        ]
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1450, "height": 900})
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            for route, active in cases:
                with self.subTest(route=route):
                    page.goto(self.base() + route, wait_until="domcontentloaded")
                    nav = page.locator("#hubGlobalNav")
                    nav.wait_for(state="visible")
                    self.assertEqual(page.locator("#hubGlobalNav .hub-nav-links a").count(), 8)
                    self.assertTrue(page.locator(
                        "#hubGlobalNav .hub-nav-links a[data-hub-page='%s']" % active
                    ).get_attribute("aria-current") == "page")
                    self.assertEqual(page.locator("#hubNavSelect").input_value(), active)
                    self.assertTrue(page.locator(
                        "#hubGlobalNav .hub-nav-brand").get_attribute("href").endswith(
                            "/index.html#advanced"))
            self.assertFalse(errors, errors)
            browser.close()

    def test_main_page_deep_links_and_browser_history(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.base() + "index.html#players", wait_until="domcontentloaded")
            page.locator("#hubGlobalNav").wait_for()
            self.assertEqual(page.locator('[data-tab="players"]').get_attribute("aria-selected"), "true")
            self.assertEqual(page.locator("#hubNavSelect").input_value(), "players")
            page.locator('[data-tab="basic"]').click()
            self.assertTrue(page.url.endswith("#basic"))
            self.assertEqual(page.locator("#hubNavSelect").input_value(), "basic")
            page.go_back(wait_until="domcontentloaded")
            self.assertEqual(page.locator('[data-tab="players"]').get_attribute("aria-selected"), "true")
            self.assertEqual(page.locator("#hubNavSelect").input_value(), "players")
            # Direct links work without reloading the main app.
            page.locator("#hubGlobalNav .hub-nav-links a[data-hub-page='compare']").click()
            self.assertTrue(page.url.endswith("#compare"))
            self.assertEqual(page.locator('[data-tab="compare"]').get_attribute("aria-selected"), "true")
            browser.close()

    def test_mobile_page_selector_is_usable_and_language_aware(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(self.base() + "index.html#advanced", wait_until="domcontentloaded")
            page.locator("#hubNavSelect").wait_for(state="visible")
            self.assertFalse(page.locator("#hubGlobalNav .hub-nav-links").is_visible())
            self.assertTrue(page.locator("#hubGlobalNav .hub-nav-quick").is_visible())
            page.locator("#langEn").click()
            self.assertIn("Player Stats", page.locator("#hubNavSelect").inner_text())
            page.locator("#hubNavSelect").select_option("players")
            page.wait_for_url("**/index.html#players")
            self.assertEqual(page.locator('[data-tab="players"]').get_attribute("aria-selected"), "true")
            page.locator("#hubNavSelect").select_option("defense")
            page.wait_for_url("**/defense.html")
            self.assertEqual(page.locator("#hubNavSelect").input_value(), "defense")
            page.locator("#hubNavSelect").select_option("contracts")
            page.wait_for_url("**/contracts/index.html")
            self.assertEqual(page.locator("#hubNavSelect").input_value(), "contracts")
            self.assertLessEqual(page.locator("#hubGlobalNav").evaluate(
                "(el) => el.scrollWidth - el.clientWidth"), 2)
            browser.close()


if __name__ == "__main__":
    unittest.main()
