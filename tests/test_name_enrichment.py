import unittest
from scripts.enrich_english import extract_official_english, pid_of, ascii_name

class EnglishNameTests(unittest.TestCase):
 def test_official_profile_roman_spelling(self):
  html="""<p>1999年2月20日</p><div>Jarrett Culver</div><h1>ジャレット・カルバー</h1>"""
  self.assertEqual(extract_official_english(html,'ジャレット・カルバー'),'Jarrett Culver')
 def test_japanese_name_with_spaces(self):
  html="""<div>Keisei Tominaga</div><h2>富永 啓生</h2>"""
  self.assertEqual(extract_official_english(html,'富永啓生'),'Keisei Tominaga')
 def test_reject_unverified(self):
  html="<h1>別の選手</h1><span>LeBron James</span>"
  self.assertIsNone(extract_official_english(html,'架空選手'))
 def test_read_player_id(self):
  self.assertEqual(pid_of({'url':'https://www.bleague.jp/roster_detail/?PlayerID=19755'}),'19755')
 def test_name_not_an_unrelated_page_element(self):
  self.assertFalse(ascii_name('B.PREMIER'))
  self.assertFalse(ascii_name('HOME'))
  self.assertTrue(ascii_name('Trey Kell III'))

if __name__=='__main__':unittest.main()
