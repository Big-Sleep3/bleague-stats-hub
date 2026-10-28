"""Kanto D2 source safety gates (offline fixtures)."""
import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("kanto2",ROOT/"scripts"/"update_college_kanto2.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def html_rows(n=25,uni="筑波大学"):
    rows=[]
    for i in range(n):
        s=[i+1,f"架空選手{i} ({uni})",2,10,0,1,4,7,2,2,1,0,4,4,1,1,0,0,"10:00"]
        # 0 three, 4 twos, 2 FT = 10 points; total REB=0+4
        rows.append("<tr>"+"".join("<td>"+str(x)+"</td>" for x in s)+"</tr>")
    return "<table>"+"".join(rows)+"</table>"
class D2Tests(unittest.TestCase):
    def test_valid_verified_teams(self):
        p=m.validated_rows(html_rows())
        self.assertEqual(len(p),25)
        self.assertEqual(p[0]["league"],"関東大学2部")
        self.assertAlmostEqual(p[0]["stats"]["two"],4/7)
    def test_reject_d1_table_or_wrong_league(self):
        with self.assertRaisesRegex(ValueError,"team validation"):
            m.validated_rows(html_rows(25,"早稲田大学"))
    def test_reject_too_few(self):
        with self.assertRaises(ValueError):m.validated_rows(html_rows(10))
    def test_preserve_ids(self):
        first=m.validated_rows(html_rows())
        second=m.validated_rows(html_rows(),first)
        self.assertEqual([p["id"] for p in first],[p["id"] for p in second])
    def test_reject_previous_list_shrinking(self):
        first=m.validated_rows(html_rows(35))
        with self.assertRaises(ValueError):m.validated_rows(html_rows(21),first)
if __name__=="__main__":unittest.main()
