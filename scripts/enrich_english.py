#!/usr/bin/env python3
"""Fetch verified English player names from B.LEAGUE official /en/ profile pages.

Writes only data/player-names-en.json, never official numerical statistics or
the revision watermark used by notifications.
"""
import asyncio
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "data" / "stats.json"
OUT = ROOT / "data" / "player-names-en.json"
EN_ROOT = "https://www.bleague.jp/en/roster_detail/?PlayerID="
JA_ROOT = "https://www.bleague.jp/roster_detail/?PlayerID="

def profile_urls(pid):
    """Prefer the JP profile: its bilingual name pair verifies the Roman spelling.

    The /en/ profile can show only the Roman name, so the parser cannot
    establish the required Japanese-name match there.
    """
    return (JA_ROOT + pid, EN_ROOT + pid)

def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")

def pid_of(player):
    url = player.get("url") or ""
    return parse_qs(urlparse(url).query).get("PlayerID", [""])[0]

def ascii_name(value):
    """Conservative name validation: reject navigation and generic page labels."""
    if not isinstance(value,str):return False
    value=value.strip()
    if not 4<=len(value)<=85 or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ.'’\-\s]+",value):
        return False
    words=value.split()
    if not 2<=len(words)<=7 or not all(len(w)<35 for w in words):return False
    blocked={'buy','ticket','tickets','club','player','players','information','news',
      'schedule','stats','statistics','basketball','league','game','games',
      'merchandise','login','log','in','member','members','watch','live',
      'stream','highlights','results','ranking','rankings','about',
      'privacy','policy','visit','home','away','next','previous','see','more',
      'sign','up','account','shop','now','checkout','cart','register','subscribe'}
    return not any(w.lower().strip(".'’-") in blocked for w in words)

def filter_name_map(candidate, current_ids):
    """Reject a dataset-wide ingestion failure before publishing any map."""
    from collections import Counter
    result={pid:name.strip() for pid,name in candidate.items()
            if pid in current_ids and ascii_name(name)}
    # Treat case and whitespace variants as the same label when detecting
    # a broken scrape (e.g. "John Smith", "JOHN SMITH", "John  Smith").
    counts=Counter(re.sub(r"\s+", " ", name).strip().casefold()
                   for name in result.values())
    worst=counts.most_common(1)
    if worst and worst[0][1]>=5:
        raise RuntimeError(f"Invalid name map: a single label was repeated {worst[0][1]} times")
    return result

try:
    from scripts.official_detail import english_name as extract_official_english
except ImportError:
    from official_detail import english_name as extract_official_english

async def enrich():
    data=json.loads(STATS.read_text(encoding="utf-8"))
    players=data.get("players",[])
    if len(players)<200:raise RuntimeError("Statistics player list incomplete; refusing to overwrite name mapping.")
    previous=json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    known=dict(previous.get("names",{}))
    work={}
    for player in players:
        pid=pid_of(player)
        if pid:
            work.setdefault(pid,player)
    if len(work)<200:raise RuntimeError("Not enough official player IDs.")
    known=filter_name_map(known,set(work))
    queue=asyncio.Queue()
    for pid,player in work.items():
        if not known.get(pid):queue.put_nowait((pid,player))
    attempts=queue.qsize()
    failures={}
    discoveries={}
    # All currently verified players need no browser session or network requests.
    if attempts:
        async with async_playwright() as playwright:
            browser=await playwright.chromium.launch(headless=True,args=["--no-sandbox"])
            context=await browser.new_context(locale="en-US",timezone_id="Asia/Tokyo",
                viewport={"width":1280,"height":820})
            async def worker(worker_id):
                page=await context.new_page()
                while True:
                    try:pid,player=queue.get_nowait()
                    except asyncio.QueueEmpty:break
                    try:
                        name=None
                        for url in profile_urls(pid):
                            try:
                                await page.goto(url,wait_until="domcontentloaded",timeout=25000)
                                name=extract_official_english(await page.content(),player["name"])
                                if name:break
                            except Exception:pass
                        if name:discoveries[pid]=name
                        else:failures[pid]=player["name"]
                    finally:
                        queue.task_done()
                        await asyncio.sleep(.4)
                await page.close()
            await asyncio.gather(*(worker(i) for i in range(4)))
            await browser.close()
    known.update(discoveries)
    names=filter_name_map(known,set(work))
    record={"source":"B.LEAGUE official Japanese and English roster profiles",
        "updated_at":now(),"total_players":len(work),"verified":len(names),
        "pending_count":len(work)-len(names),
        "names":{k:names[k] for k in sorted(names)}}
    current_names=previous.get("names",{})
    if current_names!=record["names"] or previous.get("total_players")!=len(work):
        OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"attempted":attempts,"newly_verified":len(discoveries),
        "verified":record["verified"],"total":len(work),
        "failed":len(failures),"examples":list(discoveries.items())[:4]},ensure_ascii=False),flush=True)
    # A partially unavailable official site must never replace verified names with guesses.
    # Return success if any verified names are persisted, even when some URLs were unreachable.
    if record["verified"]==0:raise RuntimeError("No verified English names were retrieved")
if __name__=="__main__":
    asyncio.run(enrich())
