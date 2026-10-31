#!/usr/bin/env python3
"""Fail-closed STRUCTURAL validation for public B.LEAGUE contract entries.

The existence of an HTTPS source link does not itself verify article claims.
Human/assistant source review is still required for contract duration and options.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
def normalize(value):
    import unicodedata
    return re.sub(r"[\s　・･\.]+","",unicodedata.normalize("NFKC",str(value or ""))).casefold()

def verify(data, roster):
    errors, warnings=[],[]
    if data.get("season")!="2026-27":
        errors.append("Unexpected contract season")
    if not isinstance(data.get("contracts"), list):
        return ["contracts must be a list"], []
    roster_keys={(normalize(p.get("club")),normalize(p.get("name"))) for p in roster}
    seen=set()
    for i,c in enumerate(data["contracts"]):
        prefix=f"contracts[{i}]"
        club,name=c.get("club"),c.get("name")
        if not isinstance(club,str) or not club.strip() or not isinstance(name,str) or not name.strip():
            errors.append(prefix+": missing club or name");continue
        pair=(normalize(club),normalize(name))
        if pair in seen:errors.append(prefix+": duplicate club/player pair")
        seen.add(pair)
        if pair not in roster_keys:warnings.append(prefix+": current stats roster has no player match")
        url=c.get("source")
        if not isinstance(url,str) or urlparse(url).scheme!="https" or not urlparse(url).hostname:
            errors.append(prefix+": missing trustworthy HTTPS source URL")
        if c.get("sourceType") not in ("club","media"):
            errors.append(prefix+": unknown source type")
        if c.get("verification")!="source_backed":
            errors.append(prefix+": not marked source-backed")
        try:dt.date.fromisoformat(c.get("announced",""))
        except (ValueError,TypeError):errors.append(prefix+": invalid announcement date")
        start,end,years=c.get("startYear"),c.get("endYear"),c.get("totalYears")
        for field,v in (("startYear",start),("endYear",end),("totalYears",years)):
            if v is not None and (type(v) is not int or (1<=v<=4 if field=="totalYears" else 2020<=v<=2035) is False):
                errors.append(prefix+": invalid "+field)
        if start is not None and end is not None:
            if end<=start:errors.append(prefix+": end must be after start")
            if years is not None and years!=end-start:errors.append(prefix+": years inconsistent with seasons")
        options=c.get("options",[])
        if not isinstance(options,list):
            errors.append(prefix+": options must be a list");continue
        kinds=set()
        for option in options:
            if not isinstance(option,dict):
                errors.append(prefix+": option not an object");continue
            year,kind=option.get("year"),option.get("kind")
            if type(year) is not int or not 2020<=year<=2035 or kind not in ("PO","TO"):
                errors.append(prefix+": invalid option year/kind");continue
            if (year,kind) in kinds:errors.append(prefix+": duplicate option")
            kinds.add((year,kind))
            if start is not None and year<start:errors.append(prefix+": option earlier than start")
            if end is not None and year>=end:errors.append(prefix+": option outside contract")
        if options and c.get("optionDisclosure")!="specified":
            errors.append(prefix+": options listed but not marked disclosed")
        if not options and c.get("optionDisclosure")=="specified":
            errors.append(prefix+": claims options specified without any details")
    return errors,warnings

def main():
    data=json.loads((ROOT/"contracts"/"contracts.json").read_text(encoding="utf-8"))
    stats=json.loads((ROOT/"data"/"stats.json").read_text(encoding="utf-8"))
    errors,warnings=verify(data,stats["players"])
    for warning in warnings:print("WARN",warning,file=sys.stderr)
    for error in errors:print("ERROR",error,file=sys.stderr)
    if errors:raise SystemExit(1)
    print("Contracts structurally valid:",len(data["contracts"]),"warnings:",len(warnings))
if __name__=="__main__":main()
