"""Fallback extraction from official club list and player detail pages."""
import time
from official_detail import club_urls,club_detail,player_detail,roster_links
LIST_URL='https://www.bleague.jp/club/'
def pages(page,alias,known,delay=.5):
 page.goto(LIST_URL,wait_until='domcontentloaded',timeout=90000)
 page.wait_for_timeout(1200)
 urls=club_urls(page.content())
 if len(urls)<26:raise ValueError('Club index returned fewer than 26 detail links')
 output={}
 for u in urls:
  page.goto(u,wait_until='domcontentloaded',timeout=45000)
  page.wait_for_timeout(220)
  short=alias(page.title())
  if short in known and short not in output:output[short]=(u,page.content())
  time.sleep(delay)
  if len(output)==26:break
 if set(output)!=set(known):raise ValueError(f'Only {len(output)} of 26 clubs in fallback')
 return output
def basic_from_pages(found,reference):
 out=[]
 for r in reference:
  u,html=found[r['abbr']]
  x=club_detail(html,r['abbr'])
  x['name']=r['name']
  out.append(x)
 return out
def players_from_pages(page,found,validate,reference,delay=.55):
 items={}
 for club,(u,html) in found.items():
  for p in roster_links(html):
   pid=p['url'].split('PlayerID=')[-1]
   if pid not in items:items[pid]=(club,p)
 if len(items)<200:raise ValueError(f'Only {len(items)} player links in fallback')
 output=[];errors=0
 for i,(pid,(club,p)) in enumerate(items.items()):
  try:
   page.goto(p['url'],wait_until='domcontentloaded',timeout=45000)
   page.wait_for_timeout(150)
   output.append(player_detail(page.content(),club,p['name'],p['number'],p['pos'],p['url']))
  except Exception:errors+=1
  if i%25==0:print('Player details',i+1,'/',len(items),'valid',len(output),flush=True)
  time.sleep(delay)
 validate(output,'players',reference)
 if len(output)<.7*len(items):raise ValueError(f'Only {len(output)} of {len(items)} player pages parsed')
 return output,{'roster_count':len(items),'failed_or_unplayed':errors}
