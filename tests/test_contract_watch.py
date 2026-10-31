"""Safe contract news discovery; article headlines are not contract terms."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("contract_watch",ROOT/"scripts"/"watch_contract_releases.py")
w=importlib.util.module_from_spec(spec);sys.modules[spec.name]=w;spec.loader.exec_module(w)
SRC={"club":"茨城","kind":"news","url":"https://www.ibarakirobots.win/news/?contents_type=32"}
class WatchTests(unittest.TestCase):
    def test_extracts_contract_news_only(self):
        doc='''<html><body><a href="/news/detail/id=10001">2026-27 選手契約継続のお知らせ（テスト選手）</a>
          <a href="/news/detail/id=20002">チームスタッフ契約合意のお知らせ</a>
          <a href="/news/detail/id=30003">バスケットボール教室のお知らせ</a>
          <a href="https://example.com/news/detail/id=40004">選手契約解除のお知らせ</a></body></html>'''
        records=w.candidate_links(doc,SRC)
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]["url"],"https://www.ibarakirobots.win/news/detail/id=10001")
    def test_fa_digest_only_from_league_rows(self):
        doc='''<table><tr><th>所属元リーグ</th><th>氏名</th><th>公示理由</th><th>日付</th><th>備考</th></tr>
         <tr><td>B.PREMIER</td><td>Test Player</td><td>契約解除</td><td>2026/10/30</td><td></td></tr>
         <tr><td>B.ONE</td><td>Another Player</td><td>契約満了</td><td>2026/10/30</td><td></td></tr></table>'''
        digest,count=w.fa_digest(doc)
        self.assertEqual(count,1)
        self.assertEqual(len(digest),64)
        self.assertEqual((digest,count),w.fa_digest(doc))
    def test_does_not_infer_terms(self):
        records=w.candidate_links('<a href="/news/detail/id=82">選手契約のお知らせ</a>',SRC)
        self.assertEqual(records,[])
        records=w.candidate_links('<a href="/news/detail/id=82">2026-27シーズン 選手契約のお知らせ</a>',SRC)
        self.assertEqual(len(records),1)
        self.assertNotIn("contractYears",records[0])
        self.assertNotIn("PO",records[0])
    def test_https_only(self):
        self.assertEqual(w.normalize_url("http://example.com/news/1"),"")
        self.assertEqual(w.normalize_url("https://example.com/news/1?utm_source=test"),"https://example.com/news/1")
if __name__=="__main__":unittest.main()
