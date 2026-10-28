import unittest
from scripts import official_detail as s
def table(h,v):
 def row(tag,values):return '<tr>'+''.join(f'<{tag}>{x}</{tag}>' for x in values)+'</tr>'
 return '<table>'+row('th',h)+row('td',v)+'</table>'
class TestOfficialDetail(unittest.TestCase):
 def test_club_2026_BP(self):
  v='84.8 88.8 29.5 68.3 43.2% 19.8 37.0 53.4% 9.8 31.3 31.1% 16.1 20.7 77.8% 14.3 28.8 43.1 18.3 15.0 5.2 2.4 1.8 22.1 20.3 200:00 88.3'.split()
  self.assertEqual(len(v),26)
  r=s.club_detail(table(['SEASON','TYPE','W','L']+s.BASIC,['2026-27','BP','3','9']+v),'信州')
  self.assertEqual((r['gp'],r['PPG'],r['RPG'],r['MINPG']),(12,84.8,43.1,'200:00'))
 def test_other_season_rejected(self):
  h=['SEASON','TYPE','W','L']+s.BASIC
  v=['2025-26','B2','3','9']+['10']*len(s.BASIC)
  with self.assertRaises(ValueError):s.club_detail(table(h,v),'信州')
  v[0]='2026-27';v[1]='BO'
  with self.assertRaises(ValueError):s.club_detail(table(h,v),'信州')
 def test_player_2026_BP(self):
  v='11 10 230:24 20:56 7.8 3.4 9.0 37.4% 3.0 6.6 45.2% 0.4 2.4 15.4% 0.7 1.4 53.3% 0.5 1.3 1.7 2.1 1.2 0.6 0.1 0.3 2.2 1.6 3.9 1.6'.split()
  self.assertEqual(len(v),29)
  x=s.player_detail(table(['SEASON','TYPE','CLUB','PO']+s.PLAYER,['2026-27','BP','群馬','PG']+v),'群馬','中村拓人')
  self.assertEqual((x['G'],x['MIN'],x['PPG'],x['APG'],x['pos']),(11,'230:24',7.8,2.1,'PG'))
 def test_leader_link_name_is_cleaned(self):
  h='<a href="/roster_detail/?PlayerID=51000658">平均得点 キーボン・ハリス 背番号： #00</a>'
  found=s.roster_links(h)
  self.assertEqual(len(found),1)
  self.assertEqual(found[0]['name'],'キーボン・ハリス')
  self.assertEqual(found[0]['number'],'00')
 def test_wrong_club_rejected(self):
  h=['SEASON','TYPE','CLUB','PO']+s.PLAYER
  v=['11','10','230:24','20:56']+['1.0']*(len(s.PLAYER)-4)
  with self.assertRaises(ValueError):s.player_detail(table(h,['2026-27','BP','群馬','PG']+v),'信州','架空')
 def test_verified_english_name(self):
  html='<section><p>#8</p><h2>Jarrett Culver</h2><h3>ジャレット・カルバー</h3></section>'
  self.assertEqual(s.english_name(html,'ジャレット・カルバー'),'Jarrett Culver')
  self.assertIsNone(s.english_name(html,'架空 選手'))
 def test_english_spelling_in_player_record(self):
  v='11 10 230:24 20:56 7.8 3.4 9.0 37.4% 3.0 6.6 45.2% 0.4 2.4 15.4% 0.7 1.4 53.3% 0.5 1.3 1.7 2.1 1.2 0.6 0.1 0.3 2.2 1.6 3.9 1.6'.split()
  html='<h2>Jarrett Culver</h2><h3>ジャレット・カルバー</h3>'+table(['SEASON','TYPE','CLUB','PO']+s.PLAYER,['2026-27','BP','仙台','SG']+v)
  r=s.player_detail(html,'仙台','ジャレット・カルバー')
  self.assertEqual(r['name_en'],'Jarrett Culver')
 def test_player_and_club_links(self):
  h='<a href="/club_detail/?TeamID=716&amp;tab=1">信州</a><a href="/roster_detail/?PlayerID=123">00 キーボン・ハリス ポジション：SG #00</a>'
  self.assertEqual(len(s.club_urls(h)),1)
  p=s.roster_links(h)
  self.assertEqual(len(p),1)
  self.assertEqual((p[0]['name'],p[0]['number'],p[0]['pos']),('キーボン・ハリス','00','SG'))
if __name__=='__main__':unittest.main()
