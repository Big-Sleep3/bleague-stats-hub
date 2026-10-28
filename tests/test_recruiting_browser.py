"""Live-browser smoke tests against a local copy of the published recruiting pages.

No real Supabase requests: staff authorization & data are mocked in the browser.
"""
import contextlib
import json
import functools
import http.server
import threading
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class RecruitingBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler=functools.partial(QuietHandler,directory=str(ROOT))
        cls.server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f"http://127.0.0.1:{cls.server.server_address[1]}/recruiting/"
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
    def test_public_stats_language_and_player_details(self):
        page=self.browser.new_page()
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        page.goto(self.url+"index.html",wait_until="domcontentloaded")
        expect(page.locator("#urh-language-control button")).to_have_count(2)
        page.locator('[data-view="stats"]').click()
        expect(page.locator("th",has_text="3PA/G")).to_have_count(1)
        expect(page.locator("th",has_text="3P%")).to_have_count(1)
        page.locator("#stats-league").select_option("関東大学1部")
        page.locator("#full-search").fill("松本")
        expect(page.locator("tbody tr")).to_have_count(1)
        row=page.locator("tbody tr").first
        self.assertIn("33.6%",row.inner_text())
        row.locator("button[data-open]").click()
        page.locator("#stats-min-gp").select_option("10")
        page.locator("#stats-min-3pa").select_option("5")
        expect(page.locator("tbody tr")).to_have_count(1)
        with page.expect_download() as event:
            page.locator("#export-stats-csv").click()
        csv=Path(event.value.path()).read_text(encoding="utf-8-sig")
        self.assertIn("3P%",csv)
        self.assertIn("松本",csv)
        expect(page.locator("#drawer-inner")).to_contain_text("3PM")
        expect(page.locator("#drawer-inner")).to_contain_text("3PA")
        page.locator("#close-drawer").click()
        page.locator('#urh-language-control [data-lang="en"]').click()
        expect(page.locator("#full-search")).to_have_attribute("placeholder","Search player or university")
        page.locator('#urh-language-control [data-lang="ja"]').click()
        expect(page.locator("#full-search")).to_have_attribute("placeholder","選手・大学名で検索")
        self.assertFalse(errors,f"Browser runtime errors: {errors}")
        page.close()
    def test_source_status_is_not_falsely_verified(self):
        page=self.browser.new_page()
        page.goto(self.url+"sources.html",wait_until="domcontentloaded")
        dataset=json.loads((ROOT/"recruiting"/"players-kanto2.json").read_text(encoding="utf-8"))
        marker="取り込み済み" if dataset.get("status")=="verified" else "検証待ち"
        expect(page.locator("#d2-source-status")).to_contain_text(marker)
        page.close()
    def test_staff_profile_language_and_film_tags(self):
        page=self.browser.new_page()
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        fake_auth=r"""window.supabase={createClient:function(){
          const ok={data:[],error:null};
          return {auth:{
            getSession:async()=>({data:{session:{user:{id:'fixture-staff',email:'scout@example.invalid'}}}}),
            onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})
          },from:function(name){
            return {
              select:function(){
                return {
                  eq:function(){return this},
                  maybeSingle:async()=>({data:{approved:true,role:'admin'},error:null}),
                  order:async()=>ok,
                  then:function(resolve,reject){return Promise.resolve(ok).then(resolve,reject)}
                }
              }
            }
          }}
        }};"""
        page.route("https://cdn.jsdelivr.net/**/supabase.min.js",
                   lambda route:route.fulfill(status=200,content_type="application/javascript",body=fake_auth))
        page.goto(self.url+"staff.html",wait_until="domcontentloaded")
        expect(page.locator("#app")).to_be_visible(timeout=12000)
        first=json.loads((ROOT/"recruiting"/"players.json").read_text(encoding="utf-8"))
        other=json.loads((ROOT/"recruiting"/"players-kanto2.json").read_text(encoding="utf-8"))
        expected=len(first["players"])+(len(other["players"]) if other.get("status")=="verified" else 0)
        expect(page.locator("#list [data-id]")).to_have_count(expected)
        page.locator("#list [data-id]").first.click()
        expect(page.locator("#official-full-stats")).to_contain_text("3P%")
        expect(page.locator("#video-tag")).to_be_visible()
        page.locator('#urh-language-control [data-lang="en"]').click()
        expect(page.locator('#form label:has(input[name="height"])')).to_contain_text("Height")
        expect(page.locator("#new-prospect-form")).to_have_count(1)
        self.assertFalse(errors,f"Staff browser errors: {errors}")
        page.close()

if __name__=="__main__":unittest.main()
