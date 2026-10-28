import json
import unittest
from pathlib import Path
from scripts.embed_snapshot import embed, TAG

ROOT=Path(__file__).resolve().parents[1]

class EmbeddedDataTests(unittest.TestCase):
 def test_deployed_html_contains_full_data(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  stats=json.loads((ROOT/'data/stats.json').read_text(encoding='utf-8'))
  embedded=json.loads(TAG.search(html).group(2))
  self.assertEqual(len(embedded['advanced']),26)
  self.assertEqual(len(embedded['basic']),26)
  self.assertGreaterEqual(len(embedded['players']),300)
  self.assertEqual(len(embedded['players']),len(stats['players']))
  self.assertEqual(embedded['players'],stats['players'])
 def test_update_keeps_complete_snapshot(self):
  html='<html><script id="bootstrap" type="application/json">{}</script></html>'
  stats={'schema':1,'advanced':[{'abbr':str(i)} for i in range(26)],
         'basic':[{'abbr':str(i)} for i in range(26)],
         'players':[{'name':'Test Player'} for _ in range(332)]}
  updated=embed(html,stats)
  self.assertEqual(len(json.loads(TAG.search(updated).group(2))['players']),332)
  self.assertEqual(embed(updated,stats),updated)
 def test_refuse_nine_player_fallback(self):
  html='<html><script id="bootstrap" type="application/json">{}</script></html>'
  stats={'schema':1,'advanced':[{} for _ in range(26)],
         'basic':[{} for _ in range(26)],'players':[{} for _ in range(9)]}
  with self.assertRaises(ValueError):
   embed(html,stats)
 def test_script_escape(self):
  html='<script id="bootstrap" type="application/json">{}</script>'
  stats={'schema':1,'advanced':[{}]*26,'basic':[{}]*26,'players':[{'name':'</script>'}]*300}
  result=embed(html,stats)
  self.assertEqual(result.count('</script>'),1)

if __name__=='__main__':unittest.main()
