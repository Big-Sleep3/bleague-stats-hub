"""Fail-closed parser regression tests: no network traffic in unit tests."""
import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("college_recruit",ROOT/"scripts"/"update_college_recruiting.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
dataset=json.loads((ROOT/"recruiting"/"players.json").read_text(encoding="utf-8"))
def sample_html(pts_delta=0):
    rows=[]
    for rank,p in enumerate(dataset["players"],1):
        s=p["stats"]
        off=0
        deff=s["reb"]
        vals=[rank,p["name"]+" ("+p["university"]+")",s["gp"],s["pts"]+(pts_delta if rank==1 else 0),
              s["threeMade"],s["threeAtt"],s["fg2Made"],s["fg2Att"],s["ftMade"],s["ftAtt"],
              0,off,deff,s["reb"],s["tov"],s["ast"],s["stl"],s["blk"],"720:00"]
        rows.append("<tr>"+"".join("<td>"+str(x)+"</td>" for x in vals)+"</tr>")
    return "<html><table><tbody>"+"".join(rows)+"</tbody></table></html>"
class CollegeRecruitingTests(unittest.TestCase):
    def test_30_standings_rows(self):
        d=mod.scrape(sample_html())
        self.assertEqual(len(d),len(dataset["players"]))
        first=dataset["players"][0]
        self.assertIn((mod.key(first["name"]),mod.key(first["university"])),d)
    def test_scoring_mismatch_rejected(self):
        d=mod.scrape(sample_html(pts_delta=1))
        self.assertLess(len(d),len(dataset["players"]))
    def test_missing_page_rejected(self):
        self.assertEqual(mod.scrape("<div>Website error</div>"),{})
    def test_unique_athlete_key_not_rank(self):
        d=mod.scrape(sample_html())
        self.assertEqual(len(d),len(set(d.keys())))
if __name__=="__main__":unittest.main()
