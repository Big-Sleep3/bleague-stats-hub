#!/usr/bin/env python3
"""Read publicly published Kanto D1 individual stats. Fail closed on changes."""
import hashlib,json,re,sys
from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timedelta,timezone
from bs4 import BeautifulSoup
URL="https://www.kcbbf.jp/game/stats/type/league/year/2026/league_id/408"
DEST=Path("recruiting/players.json")
def key(s):return re.sub(r"\s+","",s.replace("\u3000"," ")).casefold()
def scrape(html):
    soup=BeautifulSoup(html,"html.parser"); rows={}
    for tr in soup.select("tr"):
        td=tr.find_all("td",recursive=False)
        if len(td)<19:continue
        t=[x.get_text(" ",strip=True) for x in td]
        if not t[0].isdigit():continue
        match=re.match(r"^(.*?)\s*[\(（]([^()（）]*大学[^()（）]*)[\)）]\s*$",t[1].replace("\u3000"," "))
        if not match:continue
        try:
            gp,pts,t3,a3,t2,a2,ftm,fta,f,off,deff,reb,tov,ast,stl,blk=map(lambda x:int(x.replace(",","")),t[2:18])
            if not re.fullmatch(r"\d+:\d{2}",t[18]):continue
            minute,sec=map(int,t[18].split(":"))
            if not (0<=sec<60 and 0<gp<=50 and t3<=a3 and t2<=a2 and ftm<=fta and reb==off+deff and pts==3*t3+2*t2+ftm):continue
            fga=a3+a2
            s={"gp":gp,"pts":pts,"ppg":pts/gp,"rpg":reb/gp,"apg":ast/gp,
            "fg":(t3+t2)/fga if fga else None,"three":t3/a3 if a3 else None,"ft":ftm/fta if fta else None,
            "threeAttempts":a3/gp,"ts":pts/(2*(fga+0.44*fta)) if fga+0.44*fta else None,
            "astTo":ast/tov if tov else None,"mpg":(minute+sec/60)/gp,
            "reb":reb,"ast":ast,"stl":stl,"blk":blk,"tov":tov,
            "threeMade":t3,"threeAtt":a3,"fg2Made":t2,"fg2Att":a2,"ftMade":ftm,"ftAtt":fta}
            name,uni=match[1].strip(),match[2].strip()
            rows[(key(name),key(uni))]={"name":name,"university":uni,"region":"関東","stats":s}
        except (ValueError,TypeError,ZeroDivisionError):continue
    return rows
def main():
    old=json.loads(DEST.read_text())
    request=Request(URL,headers={"User-Agent":"UniversityRecruitingHub/1.1","Accept":"text/html"})
    with urlopen(request,timeout=25) as r:
        if r.status!=200:raise RuntimeError("Official source HTTP "+str(r.status))
        html=r.read().decode("utf-8",errors="replace")
    fresh=scrape(html); previous=old["players"]
    if len(fresh)<20 or len(fresh)<len(previous)*.75:
        raise ValueError("Official site returned incomplete/unexpected player list: "+str(len(fresh)))
    ids={(key(x["name"]),key(x["university"])):x for x in previous}
    new=[]
    for k,row in fresh.items():
        prev=ids.get(k,{})
        if prev and (row["stats"]["gp"]<prev["stats"].get("gp",0) or row["stats"]["pts"]<prev["stats"].get("pts",0)):
            raise ValueError("GP/PTS regression for "+row["name"])
        stable=prev.get("id") or "K26-"+hashlib.sha256(("|".join(k)).encode()).hexdigest()[:12].upper()
        new.append({**row,"id":stable,"position":prev.get("position"),"grade":prev.get("grade"),"height":prev.get("height"),"graduationYear":prev.get("graduationYear")})
    updated={**old,"season":2026,"competition":"関東大学男子1部リーグ戦",
        "coverage":"関東大学男子1部・公式掲載 "+str(len(new))+"名（全登録選手ではない）",
        "officialStatsUrl":URL,"players":new}
    was=[(x["id"],x["stats"]) for x in old["players"]]
    now=[(x["id"],x["stats"]) for x in new]
    if was==now:
        print("No statistical change");return
    updated["asOf"]=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")
    DEST.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n")
    print("Updated",len(new),"players from official source")
if __name__=="__main__":
    try:main()
    except Exception as e:print("Update rejected:",e,file=sys.stderr);sys.exit(1)
