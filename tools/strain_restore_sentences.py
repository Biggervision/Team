#!/usr/bin/env python3
"""Restore the citation sentences the migration deleted.

The link-stripping pass removed whole sentences that named a referral site
("For more on cannabis and mental health, see Project CBD's guide..."), so for
about 143 references there is no anchor text left to wrap and the earlier
restore could not place them.

This puts the original sentence back, word for word from the live page, with
its citation relinked as rel="nofollow". Nothing is rewritten or invented — if
the sentence cannot be found in the source it is skipped and reported.

Two safeguards worth knowing about:

* A sentence is only restored if its link is a citation. Plenty of the deleted
  sentences pointed at Leafly's or AllBud's page for the strain, and those stay
  deleted; that removal was the point of the exercise.
* Any other link inside the restored sentence is unwrapped, so a sentence that
  cited one good source and one competitor comes back carrying only the good
  one.

Each sentence returns to the section it came from, so the cultivation citation
lands in the cultivation copy rather than at the foot of the page.

    python3 tools/strain_restore_sentences.py --plan
    python3 tools/strain_restore_sentences.py --dry-run
    python3 tools/strain_restore_sentences.py
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
import wp                              # noqa: E402
import strain_extract as ex            # noqa: E402
import strain_restore_citations as rc  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")
BACKUPS = Path(__file__).resolve().parent.parent / "docs/strain-migration/backups-sentences"

# which extractor section maps to which stored field
SECTION_FIELD = {
    "about": "about_html", "composition": "about_html",
    "effects": "effects_html", "flavor": "flavor_html",
    "cultivation": "cultivation_html", "use": "use_html",
    "jar": "jar_html",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def clean_sentence(fragment: str, keep_url: str) -> str | None:
    """Keep the citation link, unwrap every other link, tidy the markup."""
    out = re.sub(r"(?is)<a\b(?![^>]*\b" + re.escape(keep_url) + r")[^>]*>(.*?)</a>", r"\1", fragment)
    out = re.sub(r'(?is)<a\b[^>]*href="' + re.escape(keep_url) + r'"[^>]*>(.*?)</a>',
                 lambda m: f'<a href="{keep_url}" rel="nofollow noopener" target="_blank">'
                           f'{re.sub(r"(?is)<[^>]+>", "", m.group(1)).strip()}</a>', out)
    out = re.sub(r"(?is)</?(?!a\b|/a|strong\b|/strong|em\b|/em)[a-z][^>]*>", "", out)
    out = re.sub(r"\s+", " ", out).strip()
    if keep_url not in out or len(ex.text_of(out)) < 25:
        return None
    return out


def sentences_for(page_html: str, wanted: set[str]) -> dict[str, list[str]]:
    """Find the original sentence carrying each wanted citation, by section."""
    sections = ex.split_sections(page_html)
    found: dict[str, list[str]] = {}

    for key, field in SECTION_FIELD.items():
        chunk = sections.get(key)
        if not chunk:
            continue
        for block in re.finditer(r"(?is)<(p|li)[^>]*>(.*?)</\1>", chunk):
            inner = block.group(2)
            if "<a" not in inner.lower():
                continue
            for part in SENTENCE_SPLIT.split(inner):
                for m in re.finditer(r'(?is)href="([^"]+)"', part):
                    url = m.group(1)
                    if url not in wanted or not rc.is_citation(url):
                        continue
                    cleaned = clean_sentence(part, url)
                    if cleaned:
                        found.setdefault(field, []).append(cleaned)
                        wanted.discard(url)
                    break
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()

    pages = json.load(open(SCRATCH / "prod-pages.json"))
    names = json.load(open(SCRATCH / "strain-names.json"))
    BACKUPS.mkdir(parents=True, exist_ok=True)

    cached = SCRATCH / "batch-plan.json"
    if args.plan and cached.exists():
        posts = {p["slug"]: p for p in json.load(open(cached))}
        print(f"using cached read of {len(posts)} strains")
    else:
        print("reading all strains (1 request)...", flush=True)
        got, _ = wp.request("GET", "/wp/v2/strain?per_page=100&status=any"
                                   "&context=edit&_fields=id,slug,meta")
        posts = {p["slug"]: p for p in got}
        cached.write_text(json.dumps(list(posts.values())), encoding="utf-8")
        print(f"  got {len(posts)}")

    targets = [args.only] if args.only else sorted(posts)
    changes, restored, skipped = {}, 0, 0

    for slug in targets:
        post, page = posts.get(slug), pages.get(slug)
        if not post or not page:
            continue
        html_src = (page.get("content") or {}).get("rendered", "")
        meta = post.get("meta") or {}

        # citations that are not already on the page
        wanted = {url for _, url in rc.citations_for(html_src)
                  if not any(url in (meta.get(f) or "") for f in rc.PROSE)}
        if not wanted:
            continue

        before_count = len(wanted)
        by_field = sentences_for(html_src, wanted)
        if not by_field:
            skipped += before_count
            continue

        working = {}
        for field, sentences in by_field.items():
            current = meta.get(field, "") or ""
            add = [s for s in sentences if ex.text_of(s)[:60] not in ex.text_of(current)]
            if not add:
                continue
            working[field] = (current.rstrip() + "\n"
                              + "\n".join(f"<p>{s}</p>" for s in add)).strip()
            restored += len(add)
        skipped += len(wanted)

        if working:
            changes[post["id"]] = {"slug": slug, "meta": working}

    print(f"\nplan: {len(changes)} posts")
    print(f"  citation sentences restorable : {restored}")
    print(f"  still not placeable           : {skipped}")

    if args.plan or args.dry_run:
        for pid, e in list(changes.items())[:5]:
            field = next(iter(e["meta"]))
            tail = ex.text_of(e["meta"][field])[-140:]
            print(f"\n  {e['slug']} [{field}] …{tail}")
        return 0

    written, failed = 0, []
    for i, (pid, entry) in enumerate(changes.items(), 1):
        try:
            before, _ = wp.request("GET", f"/wp/v2/strain/{pid}?context=edit")
            (BACKUPS / f"{entry['slug']}-{pid}-before.json").write_text(
                json.dumps(before, indent=1, ensure_ascii=False), encoding="utf-8")
            wp.request("POST", f"/wp/v2/strain/{pid}", data={"meta": entry["meta"]})
            written += 1
            print(f"[{i}/{len(changes)}] {entry['slug']:<24} "
                  f"{len(entry['meta'])} field(s)", flush=True)
        except Exception as exc:
            failed.append((entry["slug"], str(exc)[:80]))
            print(f"[{i}/{len(changes)}] {entry['slug']:<24} FAILED {str(exc)[:60]}", flush=True)
        time.sleep(5)

    print(f"\nwritten={written} failed={len(failed)}")
    for slug, why in failed[:10]:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
