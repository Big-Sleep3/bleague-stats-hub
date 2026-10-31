import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("validate",ROOT/"scripts"/"validate_bleague_contracts.py")
v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
ROSTER=[{"club":"茨城","name":"吉井 裕鷹"}]
def contract():
 return {"club":"茨城","name":"吉井 裕鷹","startYear":2026,"endYear":2028,"totalYears":2,
 "options":[{"year":2027,"kind":"PO"}],"optionDisclosure":"specified",
 "sourceType":"club","verification":"source_backed","source":"https://example.com/release","announced":"2026-06-12"}
class ContractValidationTests(unittest.TestCase):
 def test_good(self):
  err,w=v.verify({"season":"2026-27","contracts":[contract()]},ROSTER)
  self.assertEqual(err,[])
 def test_wrong_option_year(self):
  c=contract();c["options"][0]["year"]=2029
  err,_=v.verify({"season":"2026-27","contracts":[c]},ROSTER)
  self.assertTrue(any("outside" in x for x in err))
 def test_unknown_source_not_fabricated(self):
  c=contract();c["source"]=""
  err,_=v.verify({"season":"2026-27","contracts":[c]},ROSTER)
  self.assertTrue(err)
 def test_no_duplicate(self):
  c=contract();err,_=v.verify({"season":"2026-27","contracts":[c,c]},ROSTER)
  self.assertTrue(any("duplicate" in x for x in err))
 def test_unpublished_option_unknown_is_allowed(self):
  c=contract();c["options"]=[];c["optionDisclosure"]="not_reported"
  err,_=v.verify({"season":"2026-27","contracts":[c]},ROSTER)
  self.assertEqual(err,[])
if __name__=="__main__":unittest.main()
