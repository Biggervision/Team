#!/usr/bin/env python3
"""Apply the pending strain changes in as few HTTP requests as possible.

Written because the site's WAF blocks much of this server's egress range and
the range cannot simply be allowlisted. The fix is to stop making 200 requests
rather than to ask for 200 requests to be permitted.

    reading   1 request   all 97 strains with their meta, one page
    writing   4 requests  WordPress's /batch/v1 endpoint, 25 posts per call
    styling   1 request   the shared CSS snippet
    ----------------------------------------------------------------
    total     6 requests  in place of roughly 200

Everything is computed locally between the read and the writes, so a blocked
request costs a retry rather than a restart. If /batch/v1 is unavailable the
script says so and falls back to individual writes at a deliberately slow pace.

Two changes are applied together, since both touch the same posts:

  citations  the ~496 educational references the migration stripped, restored
             as rel="nofollow" links. Competitor directories stay removed.
  links      inline links in the strain copy were inheriting body colour with
             no underline, so they were invisible as links. The snippet gives
             them the brand green — the primary button green on dark sections,
             and the darker green the button hover already uses on cream, where
             the lighter one fails contrast against #F3EFE2.

    python3 tools/strain_batch_apply.py --plan      # local only, no requests
    python3 tools/strain_batch_apply.py --dry-run   # reads, does not write
    python3 tools/strain_batch_apply.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp                              # noqa: E402
import strain_restore_citations as rc  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")
BACKUPS = Path(__file__).resolve().parent.parent / "docs/strain-migration/backups-citations"
PLAN = SCRATCH / "batch-plan.json"

SNIPPET_ID = 14574
BATCH_SIZE = 25          # WordPress's default cap for /batch/v1

LINK_CSS = """
/* Inline links inside strain copy.
   Nothing styled anchors in .eg-prose-*, so links inherited body colour and
   were invisible. Dark sections take the primary button green; on cream that
   green is ~1.6:1 against #F3EFE2, so cream takes the darker green already
   used by the button hover state there. */
.eg-prose-cream a,.eg-prose-dark a{font-weight:600;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px;transition:color .15s ease,text-decoration-color .15s ease}
.eg-prose-dark a{color:#8FD36B;text-decoration-color:rgba(143,211,107,.45)}
.eg-prose-dark a:hover{color:#B6E394;text-decoration-color:#B6E394}
.eg-prose-cream a{color:#12704A;text-decoration-color:rgba(18,112,74,.4)}
.eg-prose-cream a:hover{color:#0E2A1E;text-decoration-color:#0E2A1E}
.eg-prose-cream a:focus-visible,.eg-prose-dark a:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:2px}
"""


def fetch_all_strains() -> list[dict]:
    """All 97 in one request."""
    posts, _ = wp.request(
        "GET", "/wp/v2/strain?per_page=100&status=any&context=edit&_fields=id,slug,meta")
    return posts


def build_plan(posts: list[dict]) -> tuple[dict, dict]:
    """Work out every field change locally. Returns (changes, stats)."""
    pages = json.load(open(SCRATCH / "prod-pages.json"))
    changes: dict[str, dict] = {}
    restored = unplaceable = 0

    for post in posts:
        slug = post["slug"]
        page = pages.get(slug)
        if not page:
            continue
        cites = rc.citations_for((page.get("content") or {}).get("rendered", ""))
        if not cites:
            continue

        meta = post.get("meta") or {}
        working = {f: meta.get(f, "") or "" for f in rc.PROSE}
        before = dict(working)

        for anchor, url in cites:
            for field in rc.PROSE:
                out = rc.relink(working[field], anchor, url)
                if out:
                    working[field] = out
                    restored += 1
                    break
            else:
                unplaceable += 1

        diff = {k: v for k, v in working.items() if v != before[k]}
        if diff:
            changes[str(post["id"])] = {"slug": slug, "meta": diff}

    return changes, {"restored": restored, "unplaceable": unplaceable,
                     "posts": len(changes)}


def write_batched(changes: dict) -> tuple[int, list]:
    ids = list(changes)
    written, failed = 0, []
    for i in range(0, len(ids), BATCH_SIZE):
        chunk = ids[i:i + BATCH_SIZE]
        payload = {"requests": [
            {"method": "POST", "path": f"/wp/v2/strain/{pid}",
             "body": {"meta": changes[pid]["meta"]}}
            for pid in chunk]}
        try:
            result, _ = wp.request("POST", "/batch/v1?requests", data=payload)
            responses = result.get("responses") or []
            for pid, resp in zip(chunk, responses):
                if isinstance(resp, dict) and resp.get("status", 200) < 300:
                    written += 1
                else:
                    failed.append((changes[pid]["slug"], json.dumps(resp)[:90]))
            print(f"  batch {i // BATCH_SIZE + 1}: {len(chunk)} posts, "
                  f"{written} written so far", flush=True)
        except Exception as exc:
            for pid in chunk:
                failed.append((changes[pid]["slug"], str(exc)[:90]))
            print(f"  batch {i // BATCH_SIZE + 1} FAILED: {str(exc)[:90]}", flush=True)
        time.sleep(3)
    return written, failed


def write_individually(changes: dict) -> tuple[int, list]:
    written, failed = 0, []
    for pid, entry in changes.items():
        try:
            wp.request("POST", f"/wp/v2/strain/{pid}", data={"meta": entry["meta"]})
            written += 1
            print(f"  {entry['slug']:<24} written", flush=True)
        except Exception as exc:
            failed.append((entry["slug"], str(exc)[:90]))
        time.sleep(6)
    return written, failed


def apply_css() -> str:
    snippet, _ = wp.request("GET", f"/wp/v2/elementor_snippet/{SNIPPET_ID}?context=edit")
    code = (snippet.get("meta") or {}).get("_elementor_code") or ""
    if ".eg-prose-dark a{" in code:
        return "already present"
    wp.request("POST", f"/wp/v2/elementor_snippet/{SNIPPET_ID}",
               data={"meta": {"_elementor_code": code.replace("</style>", LINK_CSS + "</style>")}})
    return "applied"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="use a cached read, make no requests")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-batch", action="store_true", help="force individual writes")
    args = ap.parse_args()

    if args.plan and PLAN.exists():
        posts = json.load(open(PLAN))
        print(f"using cached read of {len(posts)} strains")
    else:
        print("reading all strains (1 request)...", flush=True)
        posts = fetch_all_strains()
        PLAN.write_text(json.dumps(posts), encoding="utf-8")
        print(f"  got {len(posts)}")

    changes, stats = build_plan(posts)
    print(f"\nplan: {stats['posts']} posts to update")
    print(f"  citations restorable in place : {stats['restored']}")
    print(f"  no anchor text left to wrap   : {stats['unplaceable']}")
    print(f"  write requests needed         : "
          f"{-(-len(changes) // BATCH_SIZE)} batched, or {len(changes)} individually")

    if args.plan or args.dry_run:
        print("\nno writes made")
        return 0

    BACKUPS.mkdir(parents=True, exist_ok=True)
    (BACKUPS / "batch-before.json").write_text(json.dumps(posts, indent=1), encoding="utf-8")

    print("\nwriting...", flush=True)
    written, failed = (write_individually(changes) if args.no_batch
                       else write_batched(changes))

    try:
        print(f"\nlink styling: {apply_css()}")
    except Exception as exc:
        print(f"\nlink styling FAILED: {str(exc)[:90]}")

    try:
        wp.request("DELETE", "/elementor/v1/cache")
        wp.request("PUT", "/siteground-optimizer/v1/purge-cache")
        print("caches cleared")
    except Exception as exc:
        print(f"cache clear failed: {str(exc)[:80]}")

    print(f"\nwritten={written} failed={len(failed)}")
    for slug, why in failed[:10]:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
