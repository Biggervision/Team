#!/usr/bin/env python3
"""Audit what actually needs redirecting as the old strain pages are retired.

The instinct is that every old strain page needs a 301 to its replacement. It
does not, and setting those up would break the site rather than fix it: the
strain post type claims the whole /strain/* path, so an old page and its new
post share one URL. A 301 on /strain/alien-og/ would intercept the URL before
the new post could serve it, and point it at itself.

So this reports three separate things:

* old page URLs that a new strain post already covers - nothing to do
* old page URLs with no replacement - these genuinely need a redirect
* URLs that 404 only because the replacement is still a draft - publishing
  fixes these, a redirect would be the wrong tool

It also lists the redirects already configured, so nothing gets duplicated.

    python3 tools/strain_redirect_audit.py
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

SITE = "https://staging2.evergreenoc.com"


def path_of(url: str) -> str:
    return re.sub(rf"^{re.escape(SITE)}", "", url or "").rstrip("/") or "/"


def fetch_all(route: str, fields: str) -> list:
    out, page = [], 1
    while True:
        r, h = wp.request("GET", f"{route}?per_page=100&page={page}&status=any&_fields={fields}")
        out += r
        if page >= int(h.get("X-WP-TotalPages", "1")):
            break
        page += 1
        time.sleep(2)
    return out


def main() -> int:
    pages = fetch_all("/wp/v2/pages", "id,slug,link,status,title")
    strains = fetch_all("/wp/v2/strain", "id,slug,link,status,title")
    print(f"pages: {len(pages)}   strain posts: {len(strains)}")

    old = [p for p in pages if "/strain/" in (p.get("link") or "")]
    by_slug = {s["slug"]: s for s in strains}
    published = {s["slug"] for s in strains if s.get("status") == "publish"}

    covered, orphan, hub = [], [], []
    for p in old:
        slug = p["slug"]
        if slug == "strain":
            hub.append(p)
        elif slug in by_slug:
            covered.append((p, by_slug[slug]))
        else:
            orphan.append(p)

    print(f"\nold pages sitting under /strain/ : {len(old)}")
    print(f"  covered by a new strain post   : {len(covered)}  -> same URL, no redirect needed")
    print(f"  no replacement (need redirect) : {len(orphan)}")
    for p in orphan:
        print(f"      {path_of(p['link'])}  (page {p['id']})")
    print(f"  the /strain/ hub itself        : {len(hub)}")
    for p in hub:
        print(f"      {path_of(p['link'])}  (page {p['id']}) -> retiring, needs a 301 to /strain-hub/")

    waiting = [s for s, _ in ((s["slug"], s) for s in strains) if s not in published]
    print(f"\nstrain URLs that 404 today because the post is a draft: {len(waiting)}")
    print("  -> fixed by publishing, not by redirecting")

    # strain posts whose slug has no old page: nothing to redirect from
    old_slugs = {p["slug"] for p in old}
    fresh = [s["slug"] for s in strains if s["slug"] not in old_slugs]
    print(f"\nnew strain posts with no old page: {len(fresh)} {fresh}")

    print("\nredirects already configured:")
    try:
        r, _ = wp.request("GET", "/redirection/v1/redirect?per_page=200")
        items = r.get("items", r if isinstance(r, list) else [])
        strain_rules = [i for i in items if "strain" in (i.get("url") or "").lower()
                        or "strain" in ((i.get("action_data") or {}).get("url") or "").lower()]
        print(f"  {len(items)} total, {len(strain_rules)} touching /strain/")
        for i in strain_rules:
            tgt = (i.get("action_data") or {}).get("url")
            print(f"    {i.get('url'):<44} -> {tgt}  [{i.get('action_code')}]")
        # would any rule shadow a live strain URL?
        clash = [i for i in strain_rules
                 if re.match(r"^/strain/[a-z0-9-]+/?$", i.get("url") or "")
                 and (i.get("url") or "").strip("/").split("/")[-1] in by_slug]
        print(f"\n  rules that would shadow a real strain URL: {len(clash)}")
        for i in clash:
            print(f"    !! {i.get('url')} would intercept a live strain page")
    except Exception as exc:
        print("  could not read redirects:", str(exc)[:120])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
