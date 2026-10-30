import unittest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import scripts.enrich_english as names_module
from scripts.enrich_english import extract_official_english, pid_of, ascii_name, filter_name_map, profile_urls

class EnglishNameTests(unittest.TestCase):
 def test_complete_verified_map_skips_browser_and_preserves_file(self):
  # A complete official name map must not require Playwright or rewrite metadata.
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   stats_path=root/'stats.json'
   map_path=root/'player-names-en.json'
   ids=[str(20000+i) for i in range(332)]
   players=[{'name':'選手'+str(i),
             'url':'https://www.bleague.jp/roster_detail/?PlayerID='+pid}
            for i,pid in enumerate(ids)]
   names={pid:'Alex '+chr(65+i//26)+chr(65+i%26)
          for i,pid in enumerate(ids)}
   stats_path.write_text(json.dumps({'players':players}),encoding='utf-8')
   previous={'source':'official','updated_at':'previous run',
             'total_players':332,'verified':332,'pending_count':0,'names':names}
   map_path.write_text(json.dumps(previous),encoding='utf-8')
   original=map_path.read_bytes()
   with patch.object(names_module,'STATS',stats_path), \
        patch.object(names_module,'OUT',map_path), \
        patch.object(names_module,'async_playwright',
                     side_effect=AssertionError('Browser launched with zero pending players')):
    asyncio.run(names_module.enrich())
   self.assertEqual(map_path.read_bytes(),original)
 def test_official_profile_roman_spelling(self):
  html="""<p>1999年2月20日</p><div>Jarrett Culver</div><h1>ジャレット・カルバー</h1><div>PTS Total Points</div>"""
  self.assertEqual(extract_official_english(html,'ジャレット・カルバー'),'Jarrett Culver')
 def test_split_roman_name_fragments(self):
  html='<span>Sergio</span><span>El Darwich</span><h2>セルジオ・エル ダーウィッチ</h2><div>PTS Total Points</div>'
  self.assertEqual(extract_official_english(html,'セルジオ・エル ダーウィッチ'),'Sergio El Darwich')
 def test_split_suffix_not_lost(self):
  html='<span>Trey</span><span>Kell III</span><h2>トレイ・ケル</h2><div>PTS Total Points</div>'
  self.assertEqual(extract_official_english(html,'トレイ・ケル'),'Trey Kell III')
 def test_bilingual_japanese_profile_fetched_before_english_only_profile(self):
  self.assertEqual(profile_urls('19755'),(
   'https://www.bleague.jp/roster_detail/?PlayerID=19755',
   'https://www.bleague.jp/en/roster_detail/?PlayerID=19755'))
  en='<h1>Keisei Tominaga</h1><div>Keisei Tominaga</div><div>PPG Points</div>'
  ja='<h1>富永 啓生</h1><div>Keisei Tominaga</div><h2>富永 啓生</h2><div>PPG 平均得点数</div>'
  self.assertIsNone(extract_official_english(en,'富永 啓生'))
  self.assertEqual(extract_official_english(ja,'富永 啓生'),'Keisei Tominaga')
 def test_current_japanese_profile_uses_ppg(self):
  html='<header>富永 啓生</header><div>Keisei Tominaga</div><h2>富永 啓生</h2><div>PPG 平均得点数</div>'
  self.assertEqual(extract_official_english(html,'富永 啓生'),'Keisei Tominaga')
 def test_japanese_name_with_spaces(self):
  html="""<div>Keisei Tominaga</div><h2>富永 啓生</h2><div>PTS Total Points</div>"""
  self.assertEqual(extract_official_english(html,'富永啓生'),'Keisei Tominaga')
 def test_navigation_not_a_player_name(self):
  html='<a>Buy tickets</a><h1>ジャレット・カルバー</h1><div>生年月日1999年2月20日</div><div>Jarrett Culver</div><h2>ジャレット・カルバー</h2><p>PTS Total Points</p>'
  self.assertEqual(extract_official_english(html,'ジャレット・カルバー'),'Jarrett Culver')
  self.assertIsNone(extract_official_english('<a>Buy tickets</a><h1>ジャレット・カルバー</h1>','ジャレット・カルバー'))
 def test_reject_unverified(self):
  html="<h1>別の選手</h1><span>LeBron James</span>"
  self.assertIsNone(extract_official_english(html,'架空選手'))
 def test_mass_duplicate_labels_fail_closed(self):
  with self.assertRaises(RuntimeError):
   filter_name_map({str(i):'Same Duplicate' for i in range(6)}, {str(i) for i in range(6)})
 def test_bad_labels_ignored(self):
  clean=filter_name_map({'1':'Buy tickets','2':'Jarrett Culver'},{'1','2'})
  self.assertEqual(clean,{'2':'Jarrett Culver'})
 def test_name_shaped_navigation_is_rejected(self):
  # Menu calls to action have the same shape as a two-word person name.
  labels=('Sign Up','My Account','Shop Now','Checkout Cart','Register Account')
  for label in labels:
   with self.subTest(label=label):
    self.assertFalse(ascii_name(label))
  self.assertTrue(ascii_name('John Lawrence Harper Jr.'))
 def test_navigation_labels_cannot_enter_verified_map(self):
  candidate={'1':'Sign Up','2':'My Account','3':'Shop Now',
             '4':'Checkout Cart','5':'Register Account','6':'Keisei Tominaga'}
  self.assertEqual(filter_name_map(candidate,set(candidate)),{'6':'Keisei Tominaga'})
 def test_read_player_id(self):
  self.assertEqual(pid_of({'url':'https://www.bleague.jp/roster_detail/?PlayerID=19755'}),'19755')
 def test_name_not_an_unrelated_page_element(self):
  self.assertFalse(ascii_name('B.PREMIER'))
  self.assertFalse(ascii_name('HOME'))
  self.assertTrue(ascii_name('Trey Kell III'))
  self.assertFalse(ascii_name('Buy tickets'))

if __name__=='__main__':unittest.main()
