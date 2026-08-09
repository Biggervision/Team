#!/usr/bin/env python3
"""Audit every link on every strain page: is it there, and does it resolve?

Two separate questions, and only asking both is useful:

* Is the link present and pointing where the internal linking sheet says?
  Checked against the sheet, anchor text included.
* Would that URL actually load for a visitor?
  A strain URL only resolves once its post is published, so a link to a draft
  is correctly written and still a 404 to anyone who clicks it.

Resolution is worked out from post status over the API rather than by fetching
97 URLs, because the site rate limits hard and status is the thing that decides
it. A handful of live fetches confirm the rule holds.

    python3 tools/strain_link_audit.py
    python3 tools/strain_link_audit.py --full
    python3 tools/strain_link_audit.py --http 6   # live-check N URLs too
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

SITE = "https://staging2.evergreenoc.com"
HUB_URL = f"{SITE}/strain-hub/"
SHOP_URL = f"{SITE}/shop/"
SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")

PROSE = ("about_html", "effects_html", "flavor_html",
         "jar_html", "cultivation_html", "use_html")

import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from wp import USER_AGENT as UA  # one definition, so it cannot drift


def slug_of(path: str) -> str:
    return path.strip().rstrip("/").split("/")[-1]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def http_status(url: str) -> str:
    for _ in range(12):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as resp:
                body = resp.read(4096)
                if b"sgcaptcha" in body:
                    time.sleep(3)
                    continue
                return str(resp.status)
        except urllib.error.HTTPError as exc:
            return str(exc.code)
        except Exception:
            time.sleep(3)
    return "rate-limited"


def load_strains() -> dict:
    out, page = {}, 1
    while True:
        r, h = wp.request(
            "GET", f"/wp/v2/strain?per_page=100&page={page}&status=any"
                   "&_fields=id,slug,status,link,meta")
        for x in r:
            out[x["slug"]] = x
        if page >= int(h.get("X-WP-TotalPages", "1")):
            break
        page += 1
        time.sleep(2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--http", type=int, default=0, help="live-check N sample URLs")
    args = ap.parse_args()

    strains = load_strains()
    print(f"strain posts: {len(strains)}")

    rows = {slug_of(r["Strain page"]): r
            for r in csv.DictReader(open(SCRATCH / "links.csv"))
            if (r.get("Strain page") or "").startswith("/strain/")}
    print(f"rows in linking sheet: {len(rows)}")

    published = {s for s, x in strains.items() if x.get("status") == "publish"}
    print(f"published: {len(published)}  |  draft: {len(strains) - len(published)}\n")

    total_links = 0
    broken_target = []      # points at something that does not exist at all
    unresolvable = []       # exists but is a draft, so 404 today
    missing_expected = []   # sheet says link, page does not have it
    anchor_wrong = []
    no_hub = []
    detail = []

    for slug, post in sorted(strains.items()):
        meta = post.get("meta") or {}
        found = {}
        for field in PROSE:
            for m in re.finditer(r'(?is)<a\s+href="([^"]+)"\s*>(.*?)</a>',
                                 meta.get(field, "") or ""):
                found.setdefault(m.group(1), []).append(
                    re.sub(r"<[^>]+>", "", m.group(2)).strip())
        total_links += sum(len(v) for v in found.values())

        if HUB_URL not in found:
            no_hub.append(slug)

        for url in found:
            if url in (HUB_URL, SHOP_URL):
                continue
            m = re.match(rf"^{re.escape(SITE)}/strain/([a-z0-9-]+)/$", url)
            if not m:
                broken_target.append((slug, url, "unexpected URL shape"))
                continue
            target = m.group(1)
            if target not in strains:
                broken_target.append((slug, url, "no such strain"))
            elif target not in published:
                unresolvable.append((slug, target))

        row = rows.get(slug)
        if row:
            expected = [(HUB_URL, row["Anchor 1"].strip())]
            for lc, ac in (("Link 2 - related strain", "Anchor 2"),
                           ("Link 3 - related strain", "Anchor 3")):
                t = (row.get(lc) or "").strip()
                if t:
                    expected.append((f"{SITE}/strain/{slug_of(t)}/", (row.get(ac) or "").strip()))
            for url, anc in expected:
                if url not in found:
                    missing_expected.append((slug, url))
                elif anc and not any(norm(anc) in norm(g) for g in found[url]):
                    anchor_wrong.append((slug, anc, found[url][:1]))

        detail.append((slug, post.get("status"), len(found), sum(len(v) for v in found.values())))

    print(f"links found on strain pages : {total_links}")
    print(f"  distinct-target coverage  : {len(detail)} pages checked")
    print(f"pages missing the hub link  : {len(no_hub)} {no_hub or ''}")
    print(f"links to a non-existent page: {len(broken_target)}")
    for s, u, why in broken_target[:10]:
        print(f"    {s} -> {u} ({why})")
    print(f"sheet links missing on page : {len(missing_expected)}")
    for s, u in missing_expected[:10]:
        print(f"    {s} -> {u}")
    print(f"anchor text mismatches      : {len(anchor_wrong)}")
    for s, a, g in anchor_wrong[:10]:
        print(f"    {s}: expected {a!r} got {g}")

    dead = sorted({t for _, t in unresolvable})
    print(f"\nlinks pointing at an unpublished strain: {len(unresolvable)}")
    print(f"  distinct dead targets: {len(dead)}")
    print("  -> these are written correctly but 404 until those posts are published")

    if args.full:
        print("\nper-page:")
        for slug, status, targets, links in detail:
            print(f"  {slug:<24} {status:<8} {targets} targets / {links} links")

    if args.http:
        print(f"\nlive-checking {args.http} URLs:")
        samples = [HUB_URL, SHOP_URL]
        samples += [f"{SITE}/strain/{s}/" for s in sorted(published)][:2]
        samples += [f"{SITE}/strain/{s}/" for s in dead[:max(0, args.http - 4)]]
        for u in samples[:args.http]:
            print(f"  {http_status(u):>13}  {u}")
            time.sleep(2)

    ok = not (broken_target or missing_expected or anchor_wrong or no_hub)
    print(f"\nstructural result: {'PASS' if ok else 'ISSUES FOUND'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
