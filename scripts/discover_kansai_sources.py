#!/usr/bin/env python3
"""Inspect publicly linked KIBF 2026 stats files; no modifications."""
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urljoin
for division in (1,2):
 url=f'https://www.kibf.or.jp/archives/{34936+division}'
 print('\n=== KIBF DIV',division,url,'===')
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:
   body=r.read().decode('utf-8',errors='replace')
   print('Status:',r.status,'Bytes:',len(body),'Final URL:',r.url)
  soup=BeautifulSoup(body,'html.parser')
  seen=set()
  for a in soup.find_all('a',href=True):
   href=urljoin(url,a['href'])
   label=a.get_text(' ',strip=True)[:120]
   if href in seen:continue
   seen.add(href)
   if any(w in (label+' '+href).lower() for w in ('スタッツ','stats','ranking','ランキング','pdf','box','youtube','順位','drive.google')):
    print('LINK',repr(label),href[:500])
 except Exception as e:
  print('ERROR',type(e).__name__,str(e)[:300])
