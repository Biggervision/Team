#!/usr/bin/env python3
"""Finish applying menu prices and images, patiently.

Sideloading product photos means large binary POSTs, and SiteGround's rate
limiter treats those far more harshly than the text writes the rest of the
migration used — a run that pushes straight through gets locked out partway.

This does the same work as strain_apply_menu.py but paced for that: it checks
what is already done before each item so it can be re-run safely, waits between
items, and backs off for minutes rather than seconds when it is refused.

    python3 tools/strain_apply_menu_finish.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp                      # noqa: E402
import strain_apply_menu as am  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")

GAP = 25          # between successful items
COOLDOWN = 180    # after a refusal
ROUNDS = 12


def patient(fn, *a, **kw):
    for attempt in range(1, 6):
        try:
            return fn(*a, **kw)
        except Exception as exc:
            if "captcha" not in str(exc).lower():
                raise
            wait = COOLDOWN * attempt
            print(f"      rate limited, waiting {wait}s (attempt {attempt}/5)", flush=True)
            time.sleep(wait)
    raise RuntimeError("still rate limited after 5 attempts")


def main() -> int:
    mapping = json.load(open(SCRATCH / "wm-map.json"))
    strains = json.load(open(SCRATCH / "strain-names.json"))
    targets = {k: v for k, v in mapping.items() if v.get("available")}

    for rnd in range(1, ROUNDS + 1):
        pending = []
        for slug, entry in sorted(targets.items()):
            pid = strains[slug]["id"]
            post = patient(wp.request, "GET",
                           f"/wp/v2/strain/{pid}?context=edit")[0]
            meta = post.get("meta") or {}
            if meta.get("price") and post.get("featured_media"):
                continue
            pending.append((slug, entry, pid, post))
            time.sleep(3)

        if not pending:
            print(f"\nall {len(targets)} in-stock strains have price and image")
            return 0

        print(f"\n=== round {rnd}: {len(pending)} still to do ===", flush=True)
        for slug, entry, pid, post in pending:
            name = strains[slug]["name"]
            payload = {"meta": {"price": am.money(entry["price"]),
                                "price_note": am.price_note(entry)}}
            try:
                if entry.get("image") and not post.get("featured_media"):
                    mid = patient(am.upload_image, entry["image"], f"{name} — Evergreen OC")
                    if mid:
                        payload["featured_media"] = mid
                patient(wp.request, "POST", f"/wp/v2/strain/{pid}", data=payload)
                print(f"  {slug:<22} {payload['meta']['price']:<7} "
                      f"featured={payload.get('featured_media', post.get('featured_media'))}",
                      flush=True)
            except Exception as exc:
                print(f"  {slug:<22} deferred: {str(exc)[:70]}", flush=True)
            time.sleep(GAP)

    print("\ngave up with items still pending")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
