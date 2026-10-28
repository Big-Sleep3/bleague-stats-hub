import unittest
from scripts.enrich_english import extract_official_english, pid_of, ascii_name

class EnglishNameTests(unittest.TestCase):
 def test_official_profile_roman_spelling(self):
  html="""<p>1999年2月20日</p><div>Jarrett Culver</div><h1>ジャレット・カルバー</h1><div>PTS Total Points</div>"""
  self.assertEqual(extract_official_english(html,'ジャレット・カルバー'),'Jarrett Culver')
 def test_split_roman_name_fragments(self):
  html='<span>Sergio</span><span>El Darwich</span><h2>セルジオ・エル ダーウィッチ</h2><div>PTS Total Points</div>'
  self.assertEqual(extract_official_english(html,'セルジオ・エル ダーウィッチ'),'Sergio El Darwich')
 def test_split_suffix_not_lost(self):
  html='<span>Trey</span><span>Kell III</span><h2>トレイ・ケル</h2><div>PTS Total Points</div>'
  self.assertEqual(extract_official_english(html,'トレイ・ケル'),'Trey Kell III')
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
 def test_read_player_id(self):
  self.assertEqual(pid_of({'url':'https://www.bleague.jp/roster_detail/?PlayerID=19755'}),'19755')
 def test_name_not_an_unrelated_page_element(self):
  self.assertFalse(ascii_name('B.PREMIER'))
  self.assertFalse(ascii_name('HOME'))
  self.assertTrue(ascii_name('Trey Kell III'))
  self.assertFalse(ascii_name('Buy tickets'))

if __name__=='__main__':unittest.main()
