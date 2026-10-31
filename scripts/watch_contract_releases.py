#!/usr/bin/env python3
"""Monitor publicly published B.LEAGUE contract announcements (lead discovery only).

Never infer contract years/options from headlines. This script writes only
public URLs/titles into watch-state.json. Verified terms are curated separately.
"""
from __future__ import annotations
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "contracts" / "watch-state.json"
CONFIG = ROOT / "contracts" / "watch-sources.json"
PATTERN = re.compile(
    r"(?:選手契約|契約(?:継続|更新|締結|合意|満了|解除|終了|延長)|複数年契約|"
    r"退団|新規契約|新加入|加入のお知らせ|移籍(?:先|決定|の)?お知らせ|自由交渉|"
    r"プレーヤーオプション|チームオプション|[PT]O(?:を|が|あり)|"
    r"player option|team option|contract extension|signing)",
    re.IGNORECASE,
)
EXCLUDE = re.compile(r"(チームスタッフ|スタッフ契約|コーチ契約|スポンサー契約|ファンクラブ|特典|グッズ|チケット|入団記者会見)")
MAX_PER_SOURCE = 100
MAX_SEEN = 1200
MAX_PENDING = 180

def normalize_url(url: str) -> str:
    p = urlparse(url)
    if p.scheme != "https" or not p.hostname:
        return ""
    if p.port not in (None, 443):
        return ""
    path = re.sub(r"/+", "/", p.path)
    return urlunparse(("https", p.netloc.lower(), path, "", "", ""))

def fetch(url: str) -> str:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; RecruitingContractWatch/1.0; public release discovery)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(req, timeout=23) as response:
        if response.status != 200:
            raise ValueError("HTTP %s" % response.status)
        raw = response.read(3_000_000)
    return raw.decode("utf-8", errors="replace")

def candidate_links(html: str, source: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(source["url"]).hostname.lower().removeprefix("www.")
    out = []
    urls = set()
    for tag in soup.find_all("a", href=True):
        title = " ".join(tag.get_text(" ", strip=True).split())
        if not (12 <= len(title) <= 160) or not PATTERN.search(title) or EXCLUDE.search(title):
            continue
        url = normalize_url(urljoin(source["url"], tag["href"]))
        if not url or url in urls:
            continue
        parsed = urlparse(url)
        if parsed.hostname.lower().removeprefix("www.") != host:
            continue
        # Ignore general landing pages and dynamic results, not exact release URLs.
        if not re.search(r"(?:/news/(?:detail|[0-9]|id=)|/news/.*(?:id|detail))", parsed.path):
            continue
        urls.add(url)
        out.append({"club": source["club"], "title": title[:160], "url": url, "source": "club_official"})
        if len(out) >= MAX_PER_SOURCE:
            break
    return out

def fa_digest(html: str) -> tuple[str, int]:
    soup = BeautifulSoup(html, "html.parser")
    # Hash canonical table rows, not volatile page chrome.
    rows = []
    for tr in soup.find_all("tr"):
        cells = [" ".join(td.get_text(" ", strip=True).split()) for td in tr.find_all(["td", "th"], recursive=False)]
        if len(cells) >= 5 and any("B.PREMIER" in c for c in cells):
            rows.append("|".join(cells))
    if not rows:
        raise ValueError("No B.PREMIER FA rows; page may have changed")
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest(), len(rows)

def main() -> None:
    sources = json.loads(CONFIG.read_text(encoding="utf-8"))
    old = json.loads(DEST.read_text(encoding="utf-8"))
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d")
    results = []
    failures = []
    def visit(source):
        if source["kind"] == "fa":
            digest, count = fa_digest(fetch(source["url"]))
            return ("fa", source, (digest, count))
        return ("news", source, candidate_links(fetch(source["url"]), source))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        tasks = {pool.submit(visit, s): s for s in sources["sources"]}
        for task in concurrent.futures.as_completed(tasks):
            s = tasks[task]
            try:
                results.append(task.result())
            except Exception as exc:
                failures.append(s["club"] + ": " + str(exc)[:130])
    if len(results) < 2:
        raise ValueError("Too few official sources reachable; preserving previous snapshot: " + "; ".join(failures))
    current = {v["url"]: v for typ, src, items in results if typ == "news" for v in items}
    prior_seen = set(old.get("seenUrls", []))
    initial = not old.get("initialized")
    new = [] if initial else [v for url, v in sorted(current.items()) if url not in prior_seen]
    seen = sorted((prior_seen | set(current)))[-MAX_SEEN:]
    fa_changes = []
    for typ, source, payload in results:
        if typ != "fa":
            continue
        digest, count = payload
        key = source["club"]
        previous = old.get("faDigests", {}).get(key)
        if previous and digest != previous:
            fa_changes.append({"club": key, "title": "B.LEAGUE自由交渉選手リスト：公式掲載内容に変化", "url": source["url"], "source": "league_official", "firstSeen": today, "digest": digest})
        old.setdefault("faDigests", {})[key] = digest
        print("Official FA rows", count)
    for v in new:
        v["firstSeen"] = today
    changes = new + fa_changes
    old.update({
        "schema": 1,
        "initialized": True,
        "seenUrls": seen,
        "pending": (old.get("pending", []) + changes)[-MAX_PENDING:],
        "sourceCoverage": [src["club"] for typ, src, x in results],
    })
    # Avoid producing a new Git commit just because a scheduled check ran.
    if changes or initial or set(seen) != prior_seen:
        DEST.write_text(json.dumps(old, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"sourcesChecked": len(results), "sourceErrors": failures,
        "candidatesSeen": len(current), "newCandidates": len(new),
        "faListChanges": len(fa_changes), "initialBaseline": initial}, ensure_ascii=False))
    if failures:
        print("WARNING: Partial scan; failed sources are not considered up-to-date", file=sys.stderr)
if __name__ == "__main__":
    main()
