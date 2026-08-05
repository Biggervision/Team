#!/usr/bin/env python3
"""Harvest every live strain page from production in as few requests as possible.

Production's SiteGround protection rate limits hard, and a burst of page loads
earns a sustained block — fetching 96 URLs individually is the wrong shape.
The strain pages are ordinary WordPress pages, so the REST API returns 100 of
them per call with content included. Two successful calls beat 96.

Each call is retried patiently with long backoff rather than hammered, because
hammering is what triggers the block in the first place.

Run:  python3 tools/strain_harvest_prod.py [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

SITE = "https://evergreenoc.com"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

ATTEMPTS = 60
BACKOFF = 20        # seconds between attempts; patience beats retries here


def get_json(url: str, label: str):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read()
                headers = dict(resp.headers)
            if raw[:1] in (b"[", b"{"):
                return json.loads(raw.decode("utf-8", "replace")), headers
            print(f"  {label}: rate limited (attempt {attempt}/{ATTEMPTS})", flush=True)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"  {label}: {type(exc).__name__} (attempt {attempt}/{ATTEMPTS})", flush=True)
        time.sleep(BACKOFF)
    return None, {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/claude-0/-home-user-Team/"
                                     "f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad/prod-pages.json")
    args = ap.parse_args()

    fields = "id,slug,link,title,content,excerpt"
    collected: dict[str, dict] = {}
    page = 1
    total_pages = None

    while True:
        url = f"{SITE}/wp-json/wp/v2/pages?per_page=100&page={page}&_fields={fields}"
        data, headers = get_json(url, f"pages p{page}")
        if data is None:
            print(f"giving up on page {page}")
            break
        if total_pages is None:
            total_pages = int(headers.get("X-WP-TotalPages", "1"))
            print(f"production reports {headers.get('X-WP-Total')} pages "
                  f"across {total_pages} api pages", flush=True)
        for item in data:
            if "/strain/" in (item.get("link") or ""):
                collected[item["slug"]] = item
        print(f"  page {page}: +{len(data)} items, {len(collected)} strains so far", flush=True)
        if page >= total_pages:
            break
        page += 1
        time.sleep(5)

    out = Path(args.out)
    out.write_text(json.dumps(collected, indent=1), encoding="utf-8")
    print(f"\nharvested {len(collected)} strain pages -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
