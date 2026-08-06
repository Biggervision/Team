#!/usr/bin/env python3
"""Publish the strain pages with noindex set.

Publishing is what makes the strain URLs resolve — 95 of them currently 404,
which also breaks the 184 internal links pointing at them. Redirects are the
wrong tool for that; the URLs are correct and simply have no published post
behind them yet.

noindex is set per-post via SEOPress rather than relying on staging's
robots.txt. A robots.txt disallow stops crawling but does not prevent the URL
being indexed without content, whereas the meta tag does.

    IMPORTANT: this is a staging-only state. These pages exist to rank, so the
    noindex has to be cleared before the work reaches production or the whole
    migration is wasted. Run with --deindex false to lift it.

    python3 tools/strain_publish.py --only zamosa --dry-run
    python3 tools/strain_publish.py --only zamosa
    python3 tools/strain_publish.py
    python3 tools/strain_publish.py --deindex false     # lift noindex
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")

# SEOPress stores the "do not display in search results" checkbox as "yes"
NOINDEX_ON = "yes"
NOINDEX_OFF = ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--deindex", default="true", choices=["true", "false"])
    ap.add_argument("--publish", default="true", choices=["true", "false"])
    args = ap.parse_args()

    strains = json.load(open(SCRATCH / "strain-names.json"))
    if args.only:
        strains = {k: v for k, v in strains.items() if k == args.only}

    noindex = NOINDEX_ON if args.deindex == "true" else NOINDEX_OFF
    done, failed, skipped = [], [], []

    for i, (slug, info) in enumerate(sorted(strains.items()), 1):
        pid = info["id"]
        try:
            post, _ = wp.request("GET", f"/wp/v2/strain/{pid}?context=edit"
                                        "&_fields=id,status,link,meta")
            meta = post.get("meta") or {}
            want_status = "publish" if args.publish == "true" else post.get("status")

            payload = {}
            if post.get("status") != want_status:
                payload["status"] = want_status
            if meta.get("_seopress_robots_index") != noindex:
                payload["meta"] = {"_seopress_robots_index": noindex}

            if not payload:
                skipped.append(slug)
                print(f"[{i}/{len(strains)}] {slug:<24} already correct", flush=True)
                continue

            if args.dry_run:
                print(f"[{i}/{len(strains)}] {slug:<24} would set {list(payload)}", flush=True)
                done.append(slug)
                continue

            result, _ = wp.request("POST", f"/wp/v2/strain/{pid}", data=payload)
            done.append(slug)
            print(f"[{i}/{len(strains)}] {slug:<24} {result.get('status'):<8} "
                  f"noindex={'on' if noindex else 'off'}  {result.get('link')}", flush=True)
            time.sleep(0.5)
        except Exception as exc:
            failed.append((slug, str(exc)[:110]))
            print(f"[{i}/{len(strains)}] {slug:<24} FAILED {str(exc)[:80]}", flush=True)

    print(f"\nchanged={len(done)} unchanged={len(skipped)} failed={len(failed)}")
    for slug, why in failed:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
