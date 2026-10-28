#!/usr/bin/env python3
"""Keep the HTML's offline/fallback snapshot in sync with the validated official JSON.

This avoids ever falling back to the initial 9-player sample when GitHub Pages
or the browser cannot fetch ./data/stats.json. The public page can still fetch
newer JSON independently.
"""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'index.html'
JSON=ROOT/'data'/'stats.json'
TAG=re.compile(r'(<script id="bootstrap" type="application/json">)([\s\S]*?)(</script>)')

def embed(text,stats):
    if stats.get('schema')!=1 or len(stats.get('advanced',[]))!=26:
        raise ValueError('Refusing to embed an incomplete advanced ranking')
    if len(stats.get('basic',[]))!=26 or len(stats.get('players',[]))<300:
        raise ValueError('Refusing to embed sample or incomplete player/basic statistics')
    if not TAG.search(text):raise ValueError('Bootstrap script not found')
    # Avoid HTML script-tag injection from any unexpected team/player content.
    packed=json.dumps(stats,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')
    replacement=lambda match:match.group(1)+packed+match.group(3)
    next_html,count=TAG.subn(replacement,text,count=1)
    if count!=1:raise ValueError('Expected exactly one bootstrap tag')
    recovered=TAG.search(next_html)
    if json.loads(recovered.group(2))['players']!=stats['players']:
        raise ValueError('Embedded snapshot validation failed')
    return next_html

def main():
    data=json.loads(JSON.read_text(encoding='utf-8'))
    html=HTML.read_text(encoding='utf-8')
    result=embed(html,data)
    if result!=html:
        HTML.write_text(result,encoding='utf-8')
        print(f"Embedded current stats: {len(data['advanced'])} advanced clubs, "
              f"{len(data['basic'])} basic clubs, {len(data['players'])} players.")
    else:
        print("HTML snapshot already current.")

if __name__=='__main__':main()
