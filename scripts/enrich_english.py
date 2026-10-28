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

def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")

def pid_of(player):
    url = player.get("url") or ""
    return parse_qs(urlparse(url).query).get("PlayerID", [""])[0]

def ascii_name(value):
    if not isinstance(value, str): return False
    value=value.strip()
    if not 4 <= len(value) <= 85 or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ.'’\-\s]+",value):
        return False
    words=value.split()
    if len(words)<2 or len(words)>7: return False
    banned={"Player Information","Club Information","B LEAGUE","Player Profile","Individual Performance",
            "Season Results","Basketball Stats","Sendai 89ERS","Season Stats","B PREMIER"}
    return value not in banned and all(len(w)<35 for w in words)

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
    queue=asyncio.Queue()
    for pid,player in work.items():
        if not known.get(pid):queue.put_nowait((pid,player))
    attempts=queue.qsize()
    failures={}
    discoveries={}
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
                    for url in (EN_ROOT+pid,JA_ROOT+pid):
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
    record={"source":"B.LEAGUE official Japanese and English roster profiles",
        "updated_at":now(),"total_players":len(work),"verified":sum(bool(known.get(k)) for k in work),
        "pending_count":sum(not bool(known.get(k)) for k in work),
        "names":{k:known[k] for k in sorted(known) if k in work and ascii_name(known[k])}}
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
