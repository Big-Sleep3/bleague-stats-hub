"""Physical source matching must never mix universities or infer weight."""
import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("body",ROOT/"scripts"/"update_recruiting_physical.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def athlete():
 return [{"id":"K1","name":"松本 秦","university":"早稲田大学"},
         {"id":"K2","name":"松本 秦","university":"別の大学"},
         {"id":"K3","name":"北條 彪之介","university":"青山学院大学"}]
class VerifiedBodyTests(unittest.TestCase):
 def test_tournament_roster(self):
  html="<table>"+ "".join(f"<tr><td>{i}</td><td>3年</td><td>PG</td><td>選手{i}</td><td>180cm</td><td>高校</td></tr>" for i in range(10))+"</table>"
  rows=m.row_value(html,"JUBF");self.assertEqual(len(rows),10)
  self.assertEqual(rows[0]["height"],180)
  self.assertEqual(rows[0]["gradeAtSource"],3)
 def test_only_same_university(self):
  r={"name":"松本秦","university":"早稲田大学","height":191,"weight":85,"sourceYear":2025,
     "source":"https://jubf.jp/verified","publisher":"JUBF official"}
  x=m.compile_records(athlete(),[r],[])
  self.assertEqual(len(x),1);self.assertEqual(x[0]["id"],"K1")
 def test_no_fabricated_weight(self):
  r={"name":"北條 彪之介","university":"青山学院大学","height":191,"sourceYear":2025,
     "source":"https://jubf.jp/verified","publisher":"JUBF"}
  x=m.compile_records(athlete(),[r],[])
  self.assertNotIn("weight",x[0]);self.assertEqual(x[0]["grade"],None) if "grade" in x[0] else None
 def test_grade_explicit_previous_year(self):
  r={"name":"北條 彪之介","university":"青山学院大学","gradeAtSource":2,
     "height":192,"sourceYear":2025,"publisher":"J SPORTS","source":"https://www.jsports.co.jp"}
  x=m.compile_records(athlete(),[r],[])
  self.assertEqual(x[0]["grade"],3)
  self.assertEqual(x[0]["gradeEvidence"]["sourceYear"],2025)
 def test_newer_mass_wins(self):
  old={"name":"松本 秦","university":"早稲田大学","height":191,"weight":85,"sourceYear":2025,
       "source":"https://jubf.jp/","publisher":"JUBF"}
  new={**old,"weight":88,"sourceYear":2026,"source":"https://www.bleague.jp/","publisher":"B.LEAGUE"}
  x=m.compile_records(athlete(),[old,new],[])
  self.assertEqual(x[0]["weight"],88)
  self.assertEqual(x[0]["weightEvidence"]["sourceYear"],2026)
 def test_jsports_profile(self):
  html="<h1>北條 彪之介</h1><div>プロフィール</div><dl><dt>チーム</dt><dd>青山学院大学</dd><dt>身長</dt><dd>192</dd><dt>体重</dt><dd>85</dd><dt>学年</dt><dd>2</dd></dl><h2>メンバー</h2>"
  x=m.jsports_profile(html);self.assertEqual(x["height"],192);self.assertEqual(x["weight"],85)
if __name__=="__main__":unittest.main()
