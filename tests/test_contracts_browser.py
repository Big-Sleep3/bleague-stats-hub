"""B.LEAGUE Contract HUB — browser smoke tests; no production Auth traffic."""
import json,functools,http.server,threading,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
class ContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.http=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
  cls.base='http://127.0.0.1:'+str(cls.http.server_address[1])+'/contracts/'
  cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(headless=True)
 @classmethod
 def tearDownClass(cls):
  cls.browser.close();cls.pw.stop();cls.http.shutdown();cls.http.server_close()
 def test_public_332_and_verified_options(self):
  page=self.browser.new_page(accept_downloads=True)
  errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
  page.goto(self.base,wait_until='domcontentloaded')
  expect(page.locator('#kpis .kpi')).to_have_count(5)
  expect(page.locator('#results tr')).to_have_count(332)
  page.locator('#term').select_option('po')
  po=page.locator('#results tr')
  self.assertGreaterEqual(po.count(),4)
  page.locator('#query').fill('吉井')
  expect(page.locator('#results tr')).to_have_count(1)
  expect(page.locator('#results')).to_contain_text('2027-28')
  page.locator('#results [data-id]').click()
  expect(page.locator('#detail')).to_contain_text('2027-28')
  page.locator('#close').click()
  page.locator('#en').click()
  expect(page.locator('#heading')).to_have_text('Player Contract Database')
  page.locator('#ja').click()
  expect(page.locator('#heading')).to_have_text('選手契約データベース')
  with page.expect_download() as downloaded:page.locator('#export').click()
  csv=Path(downloaded.value.path()).read_text(encoding='utf-8-sig')
  self.assertIn('吉井',csv)
  self.assertIn('options',csv)
  self.assertFalse(errors,errors)
  page.close()
 def test_public_all_unknown_not_assumed_one_year(self):
  page=self.browser.new_page()
  page.goto(self.base,wait_until='domcontentloaded')
  page.locator('#term').select_option('unknown')
  expect(page.locator('#results tr')).to_have_count(321)
  self.assertNotIn('1 年',page.locator('#results').inner_text())
  page.close()
 def test_staff_has_login_without_auth(self):
  page=self.browser.new_page()
  page.route('https://cdn.jsdelivr.net/**/supabase.min.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body="window.supabase={createClient:()=>({auth:{getSession:async()=>({data:{session:null}}),onAuthStateChange:()=>({})}})};"))
  page.goto(self.base+'staff.html',wait_until='domcontentloaded')
  expect(page.locator('#login')).to_be_visible()
  page.locator('#en').click()
  expect(page.locator('#loginTitle')).to_have_text('Staff sign in')
  expect(page.locator('#app')).to_be_hidden()
  page.close()
if __name__=='__main__': unittest.main()
