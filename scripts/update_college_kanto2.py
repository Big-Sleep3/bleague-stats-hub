#!/usr/bin/env python3
"""Import the *verified* Kanto 2026 D2 player stats; no guessed records."""
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from update_college_recruiting import scrape, key

URL="https://www.kcbbf.jp/game/stats/type/league/year/2026/league_id/410"
DEST=Path("recruiting/players-kanto2.json")
KNOWN_TEAMS={
"筑波大学","専修大学","法政大学","江戸川大学","東洋大学","上武大学",
"拓殖大学","駒澤大学","明星大学","立教大学","順天堂大学","関東学院大学"
}
def validated_rows(html, previous=()):
    rows=scrape(html)
    # D2 roster and aggregate columns must match the federation's D2 tournament.
    if len(rows)<20 or len(rows)<int(len(previous)*0.75):
        raise ValueError("D2 source incomplete: only %s player rows" % len(rows))
    matching=sum(1 for row in rows.values() if row["university"] in KNOWN_TEAMS)
    if matching<len(rows)*0.85:
        raise ValueError("D2 team validation failed: %d/%d" % (matching,len(rows)))
    old={(key(x["name"]),key(x["university"])):x for x in previous}
    result=[]
    for k,row in rows.items():
        if row["university"] not in KNOWN_TEAMS:
            continue
        prev=old.get(k,{})
        now=row["stats"]
        if prev and (now["gp"]<prev["stats"]["gp"] or now["pts"]<prev["stats"]["pts"]):
            raise ValueError("Stats regressed: "+row["name"])
        ident=prev.get("id") or "K26D2-"+hashlib.sha256("|".join(k).encode()).hexdigest()[:12].upper()
        result.append({**row,"id":ident,"league":"関東大学2部","grade":prev.get("grade"),
                       "position":prev.get("position"),"height":prev.get("height"),
                       "graduationYear":prev.get("graduationYear")})
    if len(result)<20:
        raise ValueError("D2 verified roster unexpectedly small")
    return result

def main():
    old=json.loads(DEST.read_text(encoding="utf-8"))
    req=Request(URL,headers={"User-Agent":"UniversityRecruitingHub/1.2","Accept":"text/html"})
    with urlopen(req,timeout=25) as r:
        if r.status!=200:raise ValueError("HTTP "+str(r.status))
        html=r.read().decode("utf-8",errors="replace")
    players=validated_rows(html,old["players"])
    oldstats=sorted((p["id"],p["stats"]) for p in old["players"])
    newstats=sorted((p["id"],p["stats"]) for p in players)
    if oldstats==newstats:
        print("No D2 statistical change");return
    old.update({"players":players,"asOf":datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST"),
         "coverage":f"関東大学2部・公式掲載 {len(players)}名（全登録選手ではない）",
         "status":"verified"})
    DEST.write_text(json.dumps(old,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Verified Kanto D2 update",len(players))
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print("D2 update rejected (preserving prior dataset):",exc,file=sys.stderr)
        sys.exit(1)
