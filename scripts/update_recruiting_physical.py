#!/usr/bin/env python3
"""Evidence-tracked recruiting physical profiles. Public official sources ONLY.
Never infer weight from height, and never match on name alone without university.
"""
from __future__ import annotations
import json,re,sys,unicodedata
from pathlib import Path
from datetime import datetime,timedelta,timezone
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor,as_completed
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"recruiting"/"physical-profiles.json"
SOURCES=ROOT/"recruiting"/"physical-sources.json"
DATA=[ROOT/"recruiting"/"players.json",ROOT/"recruiting"/"players-kanto2.json"]

def key(s):
    return re.sub(r"[\s\u3000・·.,．/（）()]+","",unicodedata.normalize("NFKC",str(s or ""))).casefold()
def university(s):
    s=str(s or "").replace("白鴎","白鷗")
    return key(s)
def page(url):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; RecruitingHub/1.0; verified public rosters)","Accept":"text/html"})
    with urlopen(req,timeout=20) as f:
        if f.status!=200:raise RuntimeError(f"HTTP {f.status} {url}")
        buf=f.read(2600000)
        return buf.decode("utf-8",errors="replace")
def row_value(table,which):
    """Parse 2025 JUBF roster rows (number/year/position/name/height)."""
    soup=BeautifulSoup(table,"html.parser")
    rows=[]
    for tr in soup.select("tr"):
        cells=[td.get_text(" ",strip=True) for td in tr.find_all(["td","th"],recursive=False)]
        if len(cells)<5:continue
        gradeidx=next((i for i,t in enumerate(cells) if re.fullmatch(r"[1-4]\s*年",t)),None)
        hidx=next((i for i,t in enumerate(cells) if re.fullmatch(r"(?:1[4-9]\d|2[0-2]\d)(?:\.\d+)?\s*cm",t)),None)
        if gradeidx is None or hidx is None or hidx<2:continue
        name=cells[hidx-1].strip()
        if not name or len(name)>100 or not re.search(r"[\u3040-\u30ff\u3400-\u9fff]",name):continue
        position=cells[hidx-2] if re.fullmatch(r"(?:PG|SG|SF|PF|C|CF|G|F|GF|FC|CG|Wing|Big)",cells[hidx-2],re.I) else None
        rows.append({"name":name,"height":float(re.search(r"(\d+(?:\.\d+)?)",cells[hidx]).group(1)),
                     "gradeAtSource":int(re.search(r"\d",cells[gradeidx]).group()),"position":position})
    return rows
def jsports_profile(html):
    soup=BeautifulSoup(html,"html.parser")
    title=(soup.find("h1").get_text(" ",strip=True) if soup.find("h1") else "")
    text=soup.get_text("\n",strip=True)
    part=text.split("プロフィール",1)[-1].split("メンバー",1)[0]
    lines=[x.strip() for x in part.splitlines() if x.strip()]
    def value(label):
        try:return lines[lines.index(label)+1]
        except (ValueError,IndexError):return None
    profile={"name":title,"university":value("チーム"),"position":value("ポジション")}
    for column,label in [("height","身長"),("weight","体重"),("gradeAtSource","学年")]:
        s=value(label)
        if s and re.fullmatch(r"\d{1,3}(?:\.\d+)?",s):
            profile[column]=float(s) if column!="gradeAtSource" else int(s)
    return profile
def jsports_directory(html):
    soup=BeautifulSoup(html,"html.parser")
    entries={}
    for a in soup.find_all("a",href=True):
        href=urljoin("https://www.jsports.co.jp/",a["href"])
        if not re.search(r"/basketball/college/autumnleague_2025/player/\d+/?$",href):continue
        name=re.sub(r"\s*\(C\)\s*$","",a.get_text(" ",strip=True),flags=re.I)
        if name:entries.setdefault(key(name),href)
    return entries
def as_record(row,url,year,provider,club=None):
    return {**row,"university":club or row.get("university"),"source":url,"sourceYear":year,"publisher":provider}
def grade2026(rec):
    if not rec.get("gradeAtSource"):return None
    g=int(rec["gradeAtSource"])
    if rec["sourceYear"]==2026:return g if 1<=g<=4 else None
    if rec["sourceYear"]==2025:return g+1 if 1<=g<=3 else None
    return None
def choose(old,new,field):
    """Prefer newer source year; same-year school/pro league beats media directory."""
    year=int(new["sourceYear"])
    quality=(2 if "J SPORTS" not in new["publisher"] else 1)
    new_rank=(year,quality)
    old_rank=(int(old.get("sourceYear",0)),int(old.get("quality",0))) if old else (-1,-1)
    if old and old_rank>new_rank:return old
    if old and old_rank==new_rank and str(old.get("source",""))<str(new.get("source","")):return old
    return {"value":new[field],"source":new["source"],"sourceYear":year,
            "publisher":new["publisher"],"quality":quality}
def compile_records(athletes,evidence,old):
    matches={}
    by_athlete={(key(x["name"]),university(x["university"])):x for x in athletes}
    for rec in evidence:
        matched=by_athlete.get((key(rec.get("name")),university(rec.get("university"))))
        if not matched:continue
        pid=matched["id"]
        record=matches.setdefault(pid,{"id":pid,"name":matched["name"],"university":matched["university"]})
        for field in ("height","weight","position"):
            value=rec.get(field)
            if field in ("height","weight") and not (isinstance(value,(int,float)) and (140<=value<=240 if field=="height" else 45<=value<=200)):continue
            if field=="position" and not (value and len(str(value))<16):continue
            record[field+"Evidence"]=choose(record.get(field+"Evidence"),rec,field)
        g=grade2026(rec)
        if g is not None:
            item={**rec,"grade":g}
            record["gradeEvidence"]=choose(record.get("gradeEvidence"),item,"grade")
    result=[]
    by_old={p["id"]:p for p in old}
    for p in athletes:
        pid=p["id"]
        combined=matches.get(pid,{"id":pid,"name":p["name"],"university":p["university"]})
        old_record=by_old.get(pid,{})
        for field in ("height","weight","position","grade"):
            k=field+"Evidence"
            if k not in combined and k in old_record:
                combined[k]=old_record[k]
            if k in combined:
                combined[field]=combined[k]["value"]
        combined["sources"] = list(dict.fromkeys(
             [e["source"] for k,e in combined.items() if k.endswith("Evidence") and isinstance(e,dict)]))
        if any(k in combined for k in ("height","weight","position","grade")):
            result.append(combined)
    return result
def main():
    source=json.loads(SOURCES.read_text())
    old=json.loads(TARGET.read_text()) if TARGET.exists() else {"players":[]}
    athletes=[]
    for file in DATA:
        athletes.extend(json.loads(file.read_text())["players"])
    evidence=[]
    for x in source["curatedProfiles"]:
        evidence.append({**x,"sourceYear":x["asOfYear"]})
    failures=[]
    # Only verified, explicit roster pages, no wide site crawling.
    for desc in source["rosterSources"]:
        year=desc["year"]
        url=f'https://jubf.jp/game/university-detail/id/{desc["id"]}/type/{desc["season"]}/y/{year}/s/men'
        try:
            html=page(url);parsed=row_value(html,"jubf")
            if len(parsed)<8 or university(desc["university"]) not in university(html):
                raise ValueError(f"Not the expected club or roster ({len(parsed)} rows)")
            evidence.extend(as_record(r,url,year,"JUBF official tournament roster",desc["university"]) for r in parsed)
            print("JUBF",desc["university"],year,len(parsed))
        except Exception as e:
            failures.append(url+": "+str(e));print("SKIP",url,str(e)[:150])
    # J SPORTS publishes a single public roster directory with 2025 profiles.
    for desc in source.get("directorySources",[]):
        try:
            directory=jsports_directory(page(desc["url"]))
            lookup={key(a["name"]) for a in athletes}
            links=sorted(set(u for n,u in directory.items() if n in lookup))
            print("J SPORTS candidate profile links",len(links))
            def fetch_profile(url):
                r=jsports_profile(page(url))
                if r.get("name") and r.get("university"):
                    return as_record(r,url,desc["year"],desc["publisher"])
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures={pool.submit(fetch_profile,url):url for url in links}
                for f in as_completed(futures):
                    try:
                        v=f.result()
                        if v:evidence.append(v)
                    except Exception as e:failures.append(futures[f]+": "+str(e))
        except Exception as e:failures.append(desc["url"]+": "+str(e))
    result=compile_records(athletes,evidence,old.get("players",[]))
    if len(result)<len(old.get("players",[]))*.80:
        raise RuntimeError("Too many formerly verified profiles disappeared")
    updated={**old,"schema":1,"asOf":datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST"),
             "coverage":"Sourced basketball player physical measurements. Older measurements labelled by source year.",
             "players":result,"sourceCount":len(evidence),"warnings":failures[:20]}
    if old.get("players")==result and old.get("warnings")==failures[:20]:
        print("No physical profile change");return
    TARGET.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n")
    print("RECRUITING PHYSICAL PROFILES",len(result),"/",len(athletes),
          "HEIGHT",sum("height" in r for r in result),
          "WEIGHT",sum("weight" in r for r in result),
          "GRADE",sum("grade" in r for r in result))
if __name__=="__main__":
    try:main()
    except Exception as e:print("Profile refresh rejected: ",e,file=sys.stderr);sys.exit(1)
