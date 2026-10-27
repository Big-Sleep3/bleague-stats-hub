"""Parse only the official 2026-27 BP (B.PREMIER) season detail rows."""
import re
from urllib.parse import urlparse,parse_qs
from bs4 import BeautifulSoup

BASIC='PPG OPPPTSPG FGMPG FGAPG FG% 2FGMPG 2FGAPG 2FG% 3FGMPG 3FGAPG 3FG% FTMPG FTAPG FT% ORPG DRPG RPG APG TOPG STPG BSPG BSRPG FPG FDPG MINPG EFFPG'.split()
PLAYER='G GS MIN MINPG PPG FGMPG FGAPG FG% 2FGMPG 2FGAPG 2FG% 3FGMPG 3FGAPG 3FG% FTMPG FTAPG FT% ORPG DRPG RPG APG TOPG STPG BSPG BSRPG FPG FDPG EFFPG +/-'.split()

def clean(s):
 return re.sub(r'\s+',' ',str(s or '')).strip()
def val(s):
 s=clean(s).replace(',','').replace('%','')
 if re.fullmatch(r'\d+:\d\d',s):return s
 if re.fullmatch(r'[+-]?\d+(?:\.\d+)?',s):return float(s)
 return None
def rows(html):
 soup=BeautifulSoup(html,'html.parser')
 for table in soup.select('table'):
  h=None
  for tr in table.select('tr'):
   cells=tr.find_all(['th','td'],recursive=False)
   a=[clean(c.get_text(' ',strip=True)) for c in cells]
   if len(a)>=28 and 'SEASON' in a and 'TYPE' in a:
    h=a;continue
   if h and len(a)>=len(h):
    yield dict(zip(h,a[:len(h)]))
def club_detail(html,abbr):
 for row in rows(html):
  if row.get('SEASON')!='2026-27' or row.get('TYPE')!='BP' or not set(BASIC)<=set(row):continue
  v={k:val(row[k]) for k in BASIC}
  w,l=val(row.get('W')),val(row.get('L'))
  if sum(x is not None for x in v.values())<25 or not isinstance(w,float) or not isinstance(l,float):continue
  if not 0<w+l<=70 or not isinstance(v['PPG'],float) or not 10<v['PPG']<160:continue
  return {'abbr':abbr,'gp':int(w+l),'W':int(w),'L':int(l),**v}
 raise ValueError('Missing official 2026-27 BP club averages')
def player_detail(html,club,name,number='',pos='',url=''):
 for row in rows(html):
  if row.get('SEASON')!='2026-27' or row.get('TYPE')!='BP' or not set(PLAYER)<=set(row):continue
  v={k:val(row[k]) for k in PLAYER}
  if not isinstance(v['G'],float) or not 0<v['G']<=65 or not isinstance(v['PPG'],float):continue
  if row.get('CLUB') and row['CLUB']!=club and club not in row['CLUB']:continue
  return {'club':club,'name':name,'number':number,'pos':pos or row.get('PO',''),'url':url,**v}
 raise ValueError('Missing official 2026-27 BP player averages')
def club_urls(html):
 soup=BeautifulSoup(html,'html.parser')
 result=[]
 for a in soup.select('a[href]'):
  m=re.search(r'club_detail/\?TeamID=(\d+)',a['href'])
  if m:
   u='https://www.bleague.jp/club_detail/?TeamID='+m[1]+'&tab=1'
   if u not in result:result.append(u)
 return result
def roster_links(html):
 soup=BeautifulSoup(html,'html.parser')
 out={}
 for a in soup.select('a[href]'):
  href=a['href']
  if 'roster_detail/' not in href or 'PlayerID=' not in href:continue
  pid=parse_qs(urlparse(href).query).get('PlayerID',[''])[0]
  if not pid:continue
  label=clean(a.get_text(' ',strip=True))
  pos=re.search(r'\b(?:PG|SG|SF|PF|C)(?:\s*/\s*(?:PG|SG|SF|PF|C))*',label)
  number=re.search(r'#\s*(\d{1,2})',label)
  name=re.sub(r'ポジション[：:].*$','',label)
  name=re.sub(r'^\s*(?:#\s*)?\d{1,2}\s+','',name)
  name=re.sub(r'\s*#\s*\d{1,2}\s*  if not name or len(name)>100:continue
  entry={'name':name,'pos':pos[0].replace(' ','') if pos else '',
    'number':number[1] if number else '',
    'url':'https://www.bleague.jp/roster_detail/?PlayerID='+pid}
  score=int(bool(pos))+int(bool(number))+int(len(name)<35)
  if pid not in out or out[pid][0]<score:out[pid]=(score,entry)
 return [v[1] for v in out.values()]
,'',name).strip()
  name=re.sub(r'^(?:平均得点|平均リバウンド|平均アシスト)\s+','',name)
  name=re.sub(r'\s*背番号\s*[：:]\s*  if not name or len(name)>100:continue
  entry={'name':name,'pos':pos[0].replace(' ','') if pos else '',
    'number':number[1] if number else '',
    'url':'https://www.bleague.jp/roster_detail/?PlayerID='+pid}
  score=int(bool(pos))+int(bool(number))+int(len(name)<35)
  if pid not in out or out[pid][0]<score:out[pid]=(score,entry)
 return [v[1] for v in out.values()]
,'',name)
  name=clean(name)
  if not name or len(name)>100:continue
  entry={'name':name,'pos':pos[0].replace(' ','') if pos else '',
    'number':number[1] if number else '',
    'url':'https://www.bleague.jp/roster_detail/?PlayerID='+pid}
  score=int(bool(pos))+int(bool(number))+int(len(name)<35)
  if pid not in out or out[pid][0]<score:out[pid]=(score,entry)
 return [v[1] for v in out.values()]
