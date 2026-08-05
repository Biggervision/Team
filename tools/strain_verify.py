#!/usr/bin/env python3
"""Audit every migrated strain on staging.

Reads each strain back from the site rather than trusting what was sent, and
checks the things that would actually hurt: a link still pointing off-site, a
heading level competing with the template's own, placeholder copy naming the
wrong strain, or a section that silently came through empty.

    python3 tools/strain_verify.py            # summary + anything wrong
    python3 tools/strain_verify.py --full     # one line per strain
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")

# fields that are expected to be blank until pricing is decided
ALLOWED_EMPTY = {"price", "price_note"}

PROSE_FIELDS = ["about_html", "effects_html", "flavor_html", "jar_html",
                "cultivation_html", "use_html"]


def audit(slug: str, post: dict) -> tuple[dict, list[str]]:
    meta = post.get("meta") or {}
    jet = {k: v for k, v in meta.items() if not k.startswith("_")}
    blob = json.dumps(meta, ensure_ascii=False)
    problems: list[str] = []

    external = {u for u in re.findall(r"https?://[^\s\"'<>\\)]+", blob)
               if "evergreenoc.com" not in u}
    if external:
        problems.append(f"external link {sorted(external)[0]}")

    if "weedmaps" in blob.lower():
        problems.append("mentions Weedmaps")

    levels = set()
    for v in meta.values():
        if isinstance(v, str):
            levels |= set(re.findall(r"<(h[1-6])", v))
    if levels - {"h3", "h4"}:
        problems.append(f"heading levels {sorted(levels)}")

    # Placeholder copy from the reference build leaking through. Only the
    # template-authored fields matter here — the prose legitimately name-checks
    # other strains in its "explore similar strains" round-up, and those are
    # our own products, so they are wanted rather than a defect.
    name = re.sub(r"\s+Strain$", "", meta.get("hero_title", "")).strip()
    authored = json.dumps({k: meta.get(k) for k in
                           ("hero_title", "hero_lede", "buy_kick", "steps_items",
                            "cta_headline", "related_headline", "faq_headline")},
                          ensure_ascii=False)
    for other in ("Apple Jack", "Alien OG"):
        if name and other.lower() != name.lower() and other.lower() in authored.lower():
            problems.append(f"placeholder copy mentions {other}")

    empty = [k for k, v in jet.items()
             if v in ("", [], {}, None) and k not in ALLOWED_EMPTY]
    if empty:
        problems.append(f"empty: {','.join(sorted(empty))}")

    words = len(re.sub(r"<[^>]+>", " ", " ".join(
        v for v in meta.values() if isinstance(v, str))).split())
    if words < 600:
        problems.append(f"thin ({words} words)")

    stats = {
        "words": words,
        "filled": sum(1 for k, v in jet.items() if v not in ("", [], {}, None)),
        "total": len(jet),
        "seo": bool(meta.get("_seopress_titles_title")),
        "repeaters": {k: len(meta.get(k) or {}) for k in
                      ("glance", "pills", "terps", "grow_specs", "spec", "faqs")},
    }
    return stats, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    match = json.load(open(SCRATCH / "match.json"))
    rows, bad = [], []
    for i, slug in enumerate(sorted(match), 1):
        pid = match[slug]["id"]
        try:
            post, _ = wp.request("GET", f"/wp/v2/strain/{pid}?context=edit")
        except Exception as exc:
            bad.append((slug, [f"read failed: {exc}"]))
            continue
        stats, problems = audit(slug, post)
        rows.append((slug, stats))
        if problems:
            bad.append((slug, problems))
        if args.full:
            r = stats["repeaters"]
            print(f"{slug:<26}{stats['words']:>6}w  {stats['filled']}/{stats['total']}  "
                  f"seo={'y' if stats['seo'] else 'n'}  "
                  f"gl{r['glance']} pi{r['pills']} tp{r['terps']} "
                  f"gs{r['grow_specs']} sp{r['spec']} faq{r['faqs']}  "
                  f"{'; '.join(problems) if problems else ''}", flush=True)

    print(f"\naudited {len(rows)} strains")
    if rows:
        total_words = sum(s["words"] for _, s in rows)
        print(f"  total migrated copy : {total_words:,} words")
        print(f"  average per strain  : {total_words // len(rows):,} words")
        print(f"  with SEO title      : {sum(1 for _, s in rows if s['seo'])}/{len(rows)}")
        for key in ("glance", "pills", "terps", "grow_specs", "spec", "faqs"):
            n = sum(1 for _, s in rows if s["repeaters"][key])
            print(f"  {key:11} populated: {n}/{len(rows)}")

    print(f"\nstrains with problems: {len(bad)}")
    for slug, problems in bad:
        print(f"  {slug}: {'; '.join(problems)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
