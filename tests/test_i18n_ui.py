"""Browser smoke tests for Japanese/English switching on the deployed static page."""
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML=(Path(__file__).resolve().parents[1]/'index.html').as_uri()
class LanguageSwitcherTests(unittest.TestCase):
 def test_language_toggle_and_rankings(self):
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True)
   page=browser.new_page(locale='ja-JP',viewport={'width':1365,'height':900})
   errors=[]
   page.on('pageerror',lambda exc:errors.append(str(exc)))
   page.goto(HTML,wait_until='load')
   self.assertEqual(page.locator('html').get_attribute('lang'),'ja')
   self.assertIn('クラブ詳細',page.locator('[data-tab=advanced]').inner_text())
   self.assertEqual(page.locator('#tbody tr').count(),26)
   page.locator('#langEn').click()
   self.assertEqual(page.locator('html').get_attribute('lang'),'en')
   self.assertEqual(page.locator('#langEn').get_attribute('aria-pressed'),'true')
   self.assertIn('Club Advanced',page.locator('[data-tab=advanced]').inner_text())
   self.assertIn('Points in the Paint',page.locator('#metric option[value=PITP]').inner_text())
   self.assertIn('Shinshu Brave Warriors',page.locator('#tbody').inner_text())
   self.assertIn('Per Game',page.locator('#modeAvg').inner_text())
   page.locator('#metric').select_option('FBPS')
   self.assertIn('Fast-Break Points',page.locator('#metric option[value=FBPS]').inner_text())
   page.locator('[data-tab=compare]').click()
   self.assertIn('Club Comparison',page.locator('#compareView .headline h2').inner_text())
   self.assertIn('Utsunomiya Brex',page.locator('#compareNameB').inner_text())
   page.locator('#langJa').click()
   self.assertEqual(page.locator('html').get_attribute('lang'),'ja')
   self.assertIn('クラブ比較',page.locator('#compareView .headline h2').inner_text())
   self.assertIn('宇都宮ブレックス',page.locator('#compareNameB').inner_text())
   page.locator('[data-tab=players]').click()
   self.assertGreaterEqual(page.locator('#tbody tr').count(),300)
   self.assertNotIn('only the top three',page.locator('#warning').inner_text().lower())
   self.assertIn('個人成績',page.locator('#panelTitle').inner_text())
   page.locator('#langEn').click()
   self.assertIn('Player Rankings',page.locator('#panelTitle').inner_text())
   self.assertIn('Official data snapshot',page.locator('#sourceInfo').inner_text())
   self.assertIn('Jarrett Culver',page.locator('#tbody').inner_text())
   # Simulate a verified official name for another player and search it.
   page.evaluate("EN_OFFICIAL_NAMES['19755']='Keisei Tominaga'")
   page.evaluate("EN_PLAYER_STARTERS['富永 啓生']='WRONG FIXTURE'")
   page.evaluate("render()")
   self.assertIn('Keisei Tominaga',page.locator('#tbody').inner_text())
   page.locator('#search').fill('Keisei')
   self.assertGreaterEqual(page.locator('#tbody tr').count(),1)
   self.assertIn('Keisei Tominaga',page.locator('#tbody').inner_text())
   page.locator('#search').fill('')

   self.assertEqual(page.locator('#search').get_attribute('placeholder'),'Club / Player Name')
   self.assertGreaterEqual(page.locator('#tbody tr').count(),9)
   self.assertFalse(errors,errors)
   browser.close()

if __name__=='__main__':unittest.main()
