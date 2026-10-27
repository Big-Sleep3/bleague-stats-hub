#!/usr/bin/env python3
"""B.PREMIER Stats Hub updater: preserve existing data on any incomplete scrape."""
from __future__ import annotations
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
STATS=ROOT/'data/stats.json'
STATUS=ROOT/'data/sync-status.json'
BASE='https://www.bleague.jp/stats/'
ADV='2NDPTS FBPS PITP PTSOFFTO %PTSFT %PTSPITP EFG% TS% %PTS2PT %FGA2PT %PTS3PT %FGA3PT AST/TO PACE POSS OFFRTG DEFRTG NETRTG'.split()
BASIC='PPG OPPPTSPG FGMPG FGAPG FG% 2FGMPG 2FGAPG 2FG% 3FGMPG 3FGAPG 3FG% FTMPG FTAPG FT% ORPG DRPG RPG APG TOPG STPG BSPG BSRPG FPG FDPG MINPG EFFPG'.split()
PLAYER='G GS MIN MINPG PPG FGMPG FGAPG FG% 2FGMPG 2FGAPG 2FG% 3FGMPG 3FGAPG 3FG% FTMPG FTAPG FT% ORPG DRPG RPG APG TOPG STPG BSPG BSRPG FPG FDPG EFFPG +/-'.split()
ALIAS={
'北海道':'北海道','仙台':'仙台','A東京':'A東京','東京SR':'東京SR','サンロッカーズ渋谷':'東京SR',
'群馬':'群馬','富山':'富山','宇都宮':'宇都宮','茨城':'茨城','千葉J':'千葉J','千葉ジェッツ':'千葉J',
'A千葉':'A千葉','アルティーリ千葉':'A千葉','横浜BC':'横浜BC','横浜ビー・コルセアーズ':'横浜BC',
'川崎':'川崎','秋田':'秋田','三河':'三河','名古屋D':'名古屋D','三遠':'三遠','信州':'信州',
'滋賀':'滋賀','京都':'京都','大阪':'大阪','琉球':'琉球','広島':'広島','島根':'島根',
'長崎':'長崎','神戸':'神戸','佐賀':'佐賀','アルバルク東京':'A東京','レバンガ北海道':'北海道',
'仙台89ERS':'仙台','群馬クレインサンダーズ':'群馬','富山グラウジーズ':'富山','宇都宮ブレックス':'宇都宮',
'茨城ロボッツ':'茨城','川崎ブレイブサンダース':'川崎','秋田ノーザンハピネッツ':'秋田',
'シーホース三河':'三河','名古屋ダイヤモンドドルフィンズ':'名古屋D','三遠ネオフェニックス':'三遠',
'信州ブレイブウォリアーズ':'信州','滋賀レイクス':'滋賀','京都ハンナリーズ':'京都',
'大阪エヴェッサ':'大阪','琉球ゴールデンキングス':'琉球','広島ドラゴンフライズ':'広島',
'島根スサノオマジック':'島根','長崎ヴェルカ':'長崎','神戸ストークス':'神戸',
'佐賀バルーナーズ':'佐賀','東京サンロッカーズ':'東京SR'
}
ALIASES=sorted(ALIAS.items(),key=lambda x:-len(x[0]))
def club(t):
 s=str(t or '').strip()
 return next((v for k,v in ALIASES if k in s),None)
def number(t):
 s=re.sub(r'\s+','',str(t or '')).replace(',','').replace('%','')
 if not s or s in ('—','-','–'):return None
 if re.fullmatch(r'\d+:\d\d',s):return s
 try:return float(s)
 except ValueError:return None
def now():
 return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_name(path.name+'.tmp')
 temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 temp.replace(path)
def url(kind):
 args={'year':2026,'tab':1,'e':2,'o':'desc'}
 if kind=='advanced':args.update(target='club-b1',value='sPointsInThePaint',dt='dtl')
 elif kind=='basic':args.update(target='club-b1',value='STAV')
 else:args.update(target='player-b1',value='ASAV')
 return BASE+'?'+urlencode(args)
def extract_tables(page):
 return page.evaluate("""() => [...document.querySelectorAll('table')].map(t=>({
   head:[...t.querySelectorAll('thead th,thead td')].map(x=>x.innerText.trim()).join(' '),
   rows:[...t.querySelectorAll('tbody tr')].map(r=>({
     c:[...r.children].filter(x=>x.matches('td,th')).map(x=>x.innerText.trim()),
     links:[...r.querySelectorAll('a[href]')].map(x=>x.href)
   }))
 }))""")
def get_table(page,kind):
 expected={'advanced':('PITP','POSS',18),'basic':('PPG','OPPPTSPG',26),'players':('PPG','RPG',29)}[kind]
 ts=[t for t in extract_tables(page) if all(x in t['head'] for x in expected[:2]) and any(len(r['c'])>=expected[2]+2 for r in t['rows'])]
 return max(ts,key=lambda t:len(t['rows'])) if ts else None
def parse_rows(t,kind,reference):
 out={}
 cols={'advanced':ADV,'basic':BASIC,'players':PLAYER}[kind]
 known={r['abbr']:r for r in reference}
 for r in t['rows']:
  c=r['c']
  if len(c)<len(cols)+2:continue
  nums=[number(v) for v in c[-len(cols):]]
  if kind=='advanced':
   code=club(c[1])
   if code not in known or any(not isinstance(v,float) for v in nums):continue
   v=dict(zip(cols,nums))
   if v['PACE']<=0:continue
   gp=round(v['POSS']/v['PACE'])
   if not 1<=gp<=60 or abs(gp-v['POSS']/v['PACE'])>.10:continue
   out[code]={'name':known[code]['name'],'abbr':code,'gp':gp,'v':v}
  elif kind=='basic':
   code=club(c[1])
   if code not in known or not isinstance(nums[0],float) or sum(v is not None for v in nums)<23:continue
   row={'name':known[code]['name'],'abbr':code,'gp':known[code]['gp']}
   row.update({k:v for k,v in zip(cols,nums) if v is not None})
   out[code]=row
  else:
   code=club(c[2])
   if code not in known or not isinstance(nums[0],float) or not isinstance(nums[4],float):continue
   label=c[1].strip()
   name=re.split(r'#\s*\d+',label)[0].strip()
   if not name or len(name)>90:continue
   m=re.search(r'#\s*(\d+)',label)
   pos=re.search(r'\b(?:PG|SG|SF|PF|C)(?:\s*/\s*(?:PG|SG|SF|PF|C))*\s*$',label)
   row={'name':name,'club':code,'number':m.group(1) if m else '', 'pos':pos.group() if pos else ''}
   row.update({k:v for k,v in zip(cols,nums) if v is not None})
   for link in r['links']:
    if '/roster_detail/' in link:row['url']=link;break
   out[(name,code,row['number'])]=row
 return list(out.values())
def validate(rows,kind,reference):
 if kind in ('advanced','basic'):
  assert len(rows)==26, f'Expected 26 clubs, got {len(rows)}'
  assert {r['abbr'] for r in rows}=={r['abbr'] for r in reference},'Club mismatch'
  if kind=='advanced':assert all(r['v']['PITP']>=0 and r['v']['PACE']>50 for r in rows)
  else:assert all(r.get('PPG',0)>10 and 0<=r.get('FG%',-1)<=100 for r in rows)
 else:
  assert len(rows)>=200, f'Expected >=200 players, got {len(rows)}'
  assert len({r['club'] for r in rows})>=23,'Player clubs below 23'
  assert all(0<r['G']<=60 and 0<=r['PPG']<100 for r in rows)
def official_time(page):
 text=page.locator('body').inner_text(timeout=12000)
 m=re.search(r'(20\d\d)年(\d\d?)月(\d\d?)日\s*(\d\d?):(\d\d)更新',text)
 if not m:return None
 return f'{int(m[1]):04}-{int(m[2]):02}-{int(m[3]):02} {int(m[4]):02}:{m[5]} JST'
def fetch(page,kind,reference):
 u=url(kind)
 page.goto(u,wait_until='domcontentloaded',timeout=90000)
 page.wait_for_timeout(2400)
 previous=-1
 for i in range(110 if kind=='players' else 14):
  t=get_table(page,kind)
  n=len(t['rows']) if t else 0
  if kind!='players' and n>=26:break
  buttons=page.get_by_role('button',name='もっと見る',exact=True)
  clicked=False
  for j in range(buttons.count()):
   b=buttons.nth(j)
   if b.is_visible():
    try:b.click(timeout=5000);page.wait_for_timeout(450);clicked=True;break
    except Exception:pass
  if not clicked or n==previous:break
  previous=n
 t=get_table(page,kind)
 if not t:raise ValueError(f'No matching {kind} table')
 rows=parse_rows(t,kind,reference)
 validate(rows,kind,reference)
 return rows,u,official_time(page)
def run():
 from playwright.sync_api import sync_playwright
 data=json.loads(STATS.read_text(encoding='utf-8'))
 status={'last_attempt':now(),'results':{},'notes':'Incomplete sources are never accepted; previous validated values remain.'}
 good=0
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
   page=browser.new_page(locale='ja-JP',timezone_id='Asia/Tokyo',viewport={'width':1500,'height':1000})
   page.set_default_timeout(18000)
   for kind in ('advanced','basic','players'):
    try:
     rows,u,official=fetch(page,kind,data['advanced'])
     data[kind]=rows
     data.setdefault('quality',{})[kind]='full'
     data.setdefault('source',{})[kind]=u
     data.setdefault('updated',{})[kind]=official or (now()+' (official timestamp unavailable)')
     data.setdefault('retrieved',{})[kind]=now()
     data.setdefault('method',{})[kind]='leaderboard'
     status['results'][kind]={'success':True,'rows':len(rows),'updated':official}
     good+=1
     print(kind,'success',len(rows),flush=True)
    except Exception as e:
     status['results'][kind]={'success':False,'error':str(e)[:500]}
     print(kind,'ERROR',str(e),file=sys.stderr,flush=True)
   browser.close()
 except Exception as e:status['fatal_error']=str(e)[:500]
 if good:
  data['errors']=[k+': '+v.get('error','') for k,v in status['results'].items() if not v['success']]
  save(STATS,data)
 save(STATUS,status)
 print('Result',good,'/3 successful',flush=True)
 return 0 if good else 2
if __name__=='__main__':sys.exit(run())
