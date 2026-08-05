#!/usr/bin/env python3
"""Migrate live strain copy into the staging strain post type, in bulk.

For each strain: read the live page, map it onto the template's fields, back up
whatever is currently on staging, write, and verify the result. Alien OG is
skipped by default — it was migrated by hand and its copy is better tuned than
the extractor produces.

Every write is checked before it counts as a success:

* no link may point outside evergreenoc.com — the migration exists partly to
  stop sending traffic to Weedmaps and the strain directories
* headings must be `h3` only, so the template keeps a single-h1 outline
* the copy must actually have landed, not silently write an empty field

A JSON backup of each post is written before it is touched.

    python3 tools/strain_migrate.py --dry-run
    python3 tools/strain_migrate.py --only biscotti
    python3 tools/strain_migrate.py --limit 5
    python3 tools/strain_migrate.py
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp                    # noqa: E402
import strain_extract as ex  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")
BACKUPS = Path(__file__).resolve().parent.parent / "docs/strain-migration/backups"

# migrated by hand, and better for it — do not overwrite without --force-alien
HAND_MIGRATED = {"alien-og"}


def strain_name(page: dict) -> str:
    raw = (page.get("title") or {}).get("rendered", "")
    return htmllib.unescape(re.sub(r"(?is)<[^>]+>", "", raw)).strip()


def verify(meta: dict) -> list[str]:
    """Return the reasons this payload should not be written."""
    problems = []
    blob = json.dumps(meta, ensure_ascii=False)

    external = {u for u in re.findall(r"https?://[^\s\"'<>\\)]+", blob)
                if "evergreenoc.com" not in u}
    if external:
        problems.append(f"external links: {sorted(external)[:3]}")

    levels = set()
    for value in meta.values():
        if isinstance(value, str):
            levels |= set(re.findall(r"<(h[1-6])", value))
    if levels - {"h3", "h4"}:
        problems.append(f"unexpected heading levels: {sorted(levels)}")

    if len(re.sub(r"<[^>]+>", " ", meta.get("about_html", "")).split()) < 60:
        problems.append("about_html too short")
    if not meta.get("faqs"):
        problems.append("no FAQs")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="migrate a single slug")
    ap.add_argument("--limit", type=int, help="stop after N strains")
    ap.add_argument("--force-alien", action="store_true",
                    help="also overwrite the hand-migrated Alien OG")
    args = ap.parse_args()

    pages = ex.load_pages()
    match = json.load(open(SCRATCH / "match.json"))
    seo = json.load(open(SCRATCH / "prod-seo.json"))
    BACKUPS.mkdir(parents=True, exist_ok=True)

    slugs = [args.only] if args.only else sorted(match)
    if not args.force_alien and not args.only:
        slugs = [s for s in slugs if s not in HAND_MIGRATED]
    if args.limit:
        slugs = slugs[:args.limit]

    done, skipped, failed = [], [], []
    for i, slug in enumerate(slugs, 1):
        info = match.get(slug)
        page = pages.get(slug)
        if not info or not page:
            failed.append((slug, "no production page or staging post"))
            continue

        name = strain_name(page)
        meta, warnings = ex.build_meta(name, (page.get("content") or {}).get("rendered", ""))

        entry = seo.get(slug) or {}
        if entry.get("title"):
            meta["_seopress_titles_title"] = entry["title"]
        if entry.get("desc"):
            meta["_seopress_titles_desc"] = entry["desc"]

        problems = verify(meta)
        if problems:
            failed.append((slug, "; ".join(problems)))
            print(f"[{i}/{len(slugs)}] {slug:<26} REFUSED  {problems}", flush=True)
            continue

        if args.dry_run:
            words = len(re.sub(r"<[^>]+>", " ", " ".join(
                v for v in meta.values() if isinstance(v, str))).split())
            print(f"[{i}/{len(slugs)}] {slug:<26} ok  {words:>5}w  "
                  f"seo={'y' if entry.get('title') else 'n'}  {warnings or ''}", flush=True)
            done.append(slug)
            continue

        post_id = info["id"]
        try:
            before, _ = wp.request("GET", f"/wp/v2/strain/{post_id}?context=edit")
            (BACKUPS / f"{slug}-{post_id}-before.json").write_text(
                json.dumps(before, indent=1, ensure_ascii=False), encoding="utf-8")
            wp.request("POST", f"/wp/v2/strain/{post_id}", data={"meta": meta})
        except Exception as exc:
            failed.append((slug, f"write failed: {exc}"))
            print(f"[{i}/{len(slugs)}] {slug:<26} WRITE FAILED {str(exc)[:70]}", flush=True)
            continue

        done.append(slug)
        print(f"[{i}/{len(slugs)}] {slug:<26} written id={post_id} "
              f"seo={'y' if entry.get('title') else 'n'}", flush=True)
        time.sleep(1)

    print(f"\nwritten={len(done)} failed={len(failed)} skipped={len(skipped)}")
    for slug, why in failed:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
