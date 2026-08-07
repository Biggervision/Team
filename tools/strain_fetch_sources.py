#!/usr/bin/env python3
"""Download every live strain page from production, for migration to staging.

Production is rate limited by SiteGround: a burst gets a captcha interstitial
(HTTP 202, a few hundred bytes) instead of the page. It clears on retry, so each
URL is retried with a short backoff and validated on size before being kept.

Pages are cached to disk, so re-running only fetches what is missing.

Run:  python3 tools/strain_fetch_sources.py [--out DIR] [--force]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = "EvergreenOC-ContentSync/1.0 (WordPress REST client; +https://evergreenoc.com)"

MIN_BYTES = 50_000     # a real strain page; anything smaller is the captcha
ATTEMPTS = 12


def fetch(url: str) -> str | None:
    for attempt in range(ATTEMPTS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as resp:
                html = resp.read().decode("utf-8", "replace")
            if len(html) >= MIN_BYTES and "sgcaptcha" not in html:
                return html
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(min(0.5 * (attempt + 1), 5))
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/claude-0/-home-user-Team/"
                                     "f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad/sources")
    ap.add_argument("--match", default="/tmp/claude-0/-home-user-Team/"
                                       "f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad/match.json")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    match = json.load(open(args.match))

    ok = skipped = failed = 0
    for i, (slug, info) in enumerate(sorted(match.items()), 1):
        dest = out / f"{slug}.html"
        if dest.exists() and not args.force and dest.stat().st_size >= MIN_BYTES:
            skipped += 1
            continue
        html = fetch(info["url"])
        if html:
            dest.write_text(html, encoding="utf-8")
            ok += 1
            print(f"[{i}/{len(match)}] {slug} -> {len(html):,} bytes", flush=True)
        else:
            failed += 1
            print(f"[{i}/{len(match)}] {slug} -> FAILED", flush=True)

    print(f"\nfetched={ok} cached={skipped} failed={failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
