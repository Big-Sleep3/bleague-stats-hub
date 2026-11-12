"""Regression checks for ranking table frozen columns and defensive-sort order."""
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).resolve().parents[1] / "index.html").as_uri()

class TableLayoutTests(unittest.TestCase):
    def test_club_player_table_scroll_and_defense_sort(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width":1365,"height":900}, locale="ja-JP")
                errors = []
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                page.goto(HTML, wait_until="load")
                self.assertEqual(page.locator("#tbody tr").count(),26)

                def geometry():
                    return page.evaluate("""() => {
                      const sc=document.querySelector('#rankingTable .table-scroll');
                      const cells=[...document.querySelector('#tbody tr').cells].slice(0,3);
                      return {
                        left:sc.getBoundingClientRect().left,
                        scrollWidth:sc.scrollWidth,clientWidth:sc.clientWidth,
                        cells:cells.map(el=>({left:el.getBoundingClientRect().left,
                          right:el.getBoundingClientRect().right,
                          width:el.getBoundingClientRect().width,
                          sticky:getComputedStyle(el).position,
                          color:getComputedStyle(el).backgroundColor,
                          text:el.textContent.trim()}))
                      };
                    }""")

                def check_three_frozen():
                    d=geometry()
                    self.assertGreater(d["scrollWidth"],d["clientWidth"])
                    a,b,c=d["cells"]
                    self.assertAlmostEqual(a["left"],d["left"],delta=3)
                    self.assertAlmostEqual(b["left"],a["right"],delta=3)
                    self.assertAlmostEqual(c["left"],b["right"],delta=3)
                    self.assertGreaterEqual(c["width"],75)
                    for item in (a,b,c):
                        self.assertEqual(item["sticky"],"sticky")
                        self.assertNotEqual(item["color"],"rgba(0, 0, 0, 0)")
                    self.assertRegex(c["text"],r"^\d+$")

                for fraction in (0,0.5,1):
                    page.locator("#rankingTable .table-scroll").evaluate(
                        "(e,f)=>e.scrollLeft=(e.scrollWidth-e.clientWidth)*f",fraction)
                    check_three_frozen()

                # Clicking DEFRTG for the first time must rank the lowest value first.
                page.locator('#thead [data-sort="DEFRTG"]').evaluate("(e)=>e.click()")
                self.assertIn("低い順",page.locator("#sortToggle").inner_text())
                expected=page.evaluate("Math.min(...data.advanced.map(x=>x.v.DEFRTG)).toFixed(1)")
                self.assertEqual(page.locator("#tbody tr:first-child td.sel").inner_text(),expected)

                page.locator('[data-tab="basic"]').click()
                self.assertEqual(page.locator("#tbody tr").count(),26)
                check_three_frozen()

                page.locator('[data-tab="players"]').click()
                self.assertGreaterEqual(page.locator("#tbody tr").count(),300)
                page.locator("#langEn").click()
                self.assertEqual(page.locator("#rankingTable").get_attribute("data-view"),"players")
                self.assertTrue(page.locator("#tbody tr:first-child td.name").get_attribute("title"))
                page.set_viewport_size({"width":390,"height":844})
                page.locator("#rankingTable .table-scroll").evaluate("(e)=>e.scrollLeft=e.scrollWidth")
                d=geometry()
                a,b,c=d["cells"]
                self.assertAlmostEqual(a["left"],d["left"],delta=3)
                self.assertAlmostEqual(b["left"],a["right"],delta=3)
                self.assertAlmostEqual(c["left"],b["right"],delta=3)
                self.assertGreaterEqual(c["width"],90)

                # Comparison rows are deliberately not frozen as ranking rows are.
                page.locator('[data-tab="compare"]').click()
                self.assertEqual(page.locator("#compareBody tr").count(),18)
                self.assertEqual(page.locator("#compareBody tr:first-child td:nth-child(2)").evaluate(
                    "(e)=>getComputedStyle(e).position"),"static")
                self.assertFalse(errors,errors)
            finally:
                browser.close()

if __name__=="__main__":
    unittest.main()
