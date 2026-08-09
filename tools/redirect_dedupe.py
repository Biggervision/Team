#!/usr/bin/env python3
"""Remove the four duplicated redirect rules, slowly.

Each of these four source URLs was entered into the Redirection plugin twice.
Both copies of every pair are byte-identical in destination, status code and
match settings, so the pair is genuinely redundant rather than two rules that
happen to share a source.

Which copy goes is decided by hit count, not by id: the surviving rule is the
one visitors have actually been served, so nothing that is currently working
changes behaviour. The deleted ids all have zero hits.

The host rate limits hard and answers a burst with a captcha, so this waits a
long time between calls and stops at the first sign the writes are not landing.
Deleting four rules is not worth re-earning a block.

    python3 tools/redirect_dedupe.py --dry-run
    python3 tools/redirect_dedupe.py --apply
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

# (delete_id, keep_id, source url) -- delete_id is the zero-hit copy
DUPLICATES = [
    (38, 34, "/big-petes-treats/"),
    (42, 35, "/faq-2/"),
    (37, 33, "/foreign-genetics-inc/"),
    (36, 32, "/gastro-pop/"),
]

PAUSE = 20          # seconds between writes; generous on purpose


def fetch_all() -> dict[int, dict]:
    out = {}
    for gid in (1, 2):
        r, _ = wp.request("GET", f"/redirection/v1/redirect?per_page=200&filterBy[group]={gid}")
        for it in r.get("items", []):
            out[it["id"]] = it
        time.sleep(PAUSE)
    return out


def target(rule: dict) -> str | None:
    data = rule.get("action_data")
    return data.get("url") if isinstance(data, dict) else data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry_run):
        ap.error("pass --dry-run or --apply")

    rules = fetch_all()
    print(f"{len(rules)} rules on the site\n")

    # Re-confirm each pair is still identical. The backup was taken earlier and
    # someone may have edited a rule by hand since; deleting on stale
    # information is how the wrong copy goes.
    planned = []
    for dead, keep, url in DUPLICATES:
        a, b = rules.get(dead), rules.get(keep)
        if not a or not b:
            print(f"SKIP {url}: id {dead if not a else keep} no longer exists")
            continue
        same = (target(a) == target(b)
                and a.get("action_code") == b.get("action_code")
                and a.get("action_type") == b.get("action_type")
                and bool(a.get("regex")) == bool(b.get("regex")))
        if not same:
            print(f"SKIP {url}: the two copies are no longer identical - "
                  f"{target(a)!r} vs {target(b)!r}. Look before deleting.")
            continue
        if a.get("hits"):
            print(f"SKIP {url}: id {dead} has {a['hits']} hits, so it is not "
                  f"the dormant copy any more.")
            continue
        planned.append((dead, keep, url, target(a)))
        print(f"  delete id {dead:>3} (0 hits)  keep id {keep:>3} "
              f"({b.get('hits')} hits)   {url} -> {target(a)}")

    if not planned:
        print("\nnothing to do")
        return 0
    if args.dry_run:
        print(f"\ndry run: {len(planned)} deletions planned, nothing sent")
        return 0

    deleted = []
    for dead, keep, url, dest in planned:
        time.sleep(PAUSE)
        try:
            # The plugin exposes no DELETE on /redirect/{id} — removal is a POST
            # to the bulk route, one id at a time here so a failure stops the
            # run with an exact record of what had already gone.
            wp.request("POST", "/redirection/v1/bulk/redirect/delete",
                       data={"items": str(dead)})
        except wp.WPError as exc:
            print(f"\nstopped at id {dead}: {exc}")
            print(f"deleted so far: {deleted}")
            return 1
        deleted.append(dead)
        print(f"  deleted {dead}  ({url})")

    time.sleep(PAUSE)
    after = fetch_all()
    print("\nverification:")
    ok = True
    for dead, keep, url, dest in planned:
        gone = dead not in after
        kept = keep in after
        print(f"  {url:<28} deleted={gone}  survivor present={kept}")
        ok = ok and gone and kept
    print(f"\n{len(deleted)} deleted. {'PASS' if ok else 'CHECK THIS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
