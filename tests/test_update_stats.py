import json
import unittest
from pathlib import Path
from scripts.update_stats import ADV,BASIC,PLAYER,number,club,parse_rows,validate,signature

class ParserTests(unittest.TestCase):
 def test_metrics(self):
  self.assertEqual(len(ADV),18)
  self.assertEqual(len(BASIC),26)
  self.assertEqual(len(PLAYER),29)
 def test_numeric_and_time(self):
  self.assertEqual(number(' 34.5% '),34.5)
  self.assertEqual(number('200:00'),'200:00')
  self.assertIsNone(number('—'))
 def test_team_alias(self):
  self.assertEqual(club('名古屋ダイヤモンドドルフィンズ 名古屋D'),'名古屋D')
  self.assertEqual(club('信州ブレイブウォリアーズ'),'信州')
 def test_snapshot(self):
  data=json.loads((Path(__file__).parents[1]/'data'/'stats.json').read_text())
  self.assertEqual(len(data['advanced']),26)
  self.assertEqual(len({x['abbr'] for x in data['advanced']}),26)
  self.assertTrue(all(x['gp']>=1 for x in data['advanced']))
  validate(data['advanced'],'advanced',data['advanced'])
 def test_signature_ignores_row_order(self):
  data=json.loads((Path(__file__).parents[1]/'data'/'stats.json').read_text())
  rows=data['advanced']
  self.assertEqual(signature(rows,'advanced'),signature(list(reversed(rows)),'advanced'))
  changed=json.loads(json.dumps(rows))
  changed[0]['v']['PITP']+=2
  self.assertNotEqual(signature(rows,'advanced'),signature(changed,'advanced'))
 def test_bad_data_refused(self):
  data=json.loads((Path(__file__).parents[1]/'data'/'stats.json').read_text())
  with self.assertRaises(AssertionError):validate(data['advanced'][:4],'advanced',data['advanced'])
 def test_advanced_table(self):
  data=json.loads((Path(__file__).parents[1]/'data'/'stats.json').read_text())
  shinshu=next(r for r in data['advanced'] if r['abbr']=='信州')
  nums=[str(shinshu['v'][k]) for k in ADV]
  t={'rows':[{'c':['1','信州ブレイブウォリアーズ',*nums],'links':[]}]}
  parsed=parse_rows(t,'advanced',data['advanced'])
  self.assertEqual(parsed[0]['gp'],shinshu['gp'])
  self.assertEqual(parsed[0]['v']['PITP'],shinshu['v']['PITP'])
if __name__=='__main__':unittest.main()
