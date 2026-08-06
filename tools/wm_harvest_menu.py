#!/usr/bin/env python3
"""Harvest the live Weedmaps menu for Evergreen OC.

Used to answer, per strain, whether we actually stock it — and if so at what
price and with which product photo.

Two quirks worth recording. The storefront and the API both sit behind a WAF
that returns 406 to requests carrying a normal browser User-Agent, while
requests with no User-Agent header at all are served normally; that is the
opposite of the usual arrangement and the reason this script sets no UA.
Chromium cannot be used as a fallback here because it fails to negotiate the
environment's proxy, so this goes straight at the JSON API.

    python3 tools/wm_harvest_menu.py [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

LISTING = "evergreen-santa-ana"
API = (f"https://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{LISTING}"
       "/menu_items?page_size={size}&page={page}")

PAGE_SIZE = 100
ATTEMPTS = 8


def get(url: str):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            # deliberately no User-Agent: the WAF rejects browser UAs with 406
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            print(f"    attempt {attempt}/{ATTEMPTS}: {type(exc).__name__}", flush=True)
            time.sleep(4 * attempt)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/claude-0/-home-user-Team/"
                                     "f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad/wm-menu.json")
    args = ap.parse_args()

    items, page, total = [], 1, None
    while True:
        data = get(API.format(size=PAGE_SIZE, page=page))
        if not data:
            print(f"giving up at page {page}")
            break
        if total is None:
            total = data.get("meta", {}).get("total_menu_items")
            print(f"menu reports {total} items")
        batch = (data.get("data") or {}).get("menu_items") or []
        items.extend(batch)
        print(f"  page {page}: +{len(batch)} ({len(items)} so far)", flush=True)
        if not batch or (total and len(items) >= total):
            break
        page += 1
        time.sleep(1.5)

    Path(args.out).write_text(json.dumps(items, indent=1), encoding="utf-8")
    print(f"\nharvested {len(items)} menu items -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
