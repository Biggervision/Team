#!/usr/bin/env python3
"""Apply the internal linking plan to the strain pages.

Source of truth is the internal linking sheet, which gives each strain three
outbound links: a parent link to the strain hub, and two (occasionally one)
related strains from the same family.

Links go into the body copy rather than into a list at the foot of the page,
because the sheet specifies real anchor text ("Fire OG", "our full strain
menu") and that only earns its weight sitting in prose:

* Where the copy already names the related strain, that existing mention is
  linked in place. True contextual linking, no new words. Applies to 25 of 188.
* Where it does not, a short sentence is added. The sentence states only what
  the sheet already asserts — that the two strains are in the same family and
  that we stock it — so nothing is claimed about a strain that isn't known.

The three links are spread across different sections rather than stacked in one
paragraph, so the page doesn't end in a block of links.

Note the parent link points at /strain-hub/, not the /strain/ the sheet names.
Staging carries both; /strain-hub/ is the newer page and the one chosen to
consolidate on.

    python3 tools/strain_internal_links.py --dry-run
    python3 tools/strain_internal_links.py --only biscotti
    python3 tools/strain_internal_links.py
"""

from __future__ import annotations

import argparse
import csv
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

SITE = "https://staging2.evergreenoc.com"
HUB_URL = f"{SITE}/strain-hub/"
HUB_ANCHOR = "our full strain menu"

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")
BACKUPS = Path(__file__).resolve().parent.parent / "docs/strain-migration/backups-links"

# where each link prefers to live, first field that exists wins
PLACEMENT = {
    "related_1": ["about_html", "effects_html", "flavor_html"],
    "related_2": ["effects_html", "flavor_html", "jar_html", "about_html"],
    "hub":       ["use_html", "jar_html", "cultivation_html", "about_html"],
}

# the sheet's family labels do not all read well mid-sentence
FAMILY_PHRASE = {
    "OG": "OG",
    "Classics": "classic",
    "Dessert / Gelato": "dessert-leaning",
    "Blue / Blueberry": "blueberry-leaning",
    "Exotic / Designer": "designer",
    "Z-family": "Z-family",
    "Runtz": "Runtz-family",
    "Popperz": "Popperz-family",
    "Citrus": "citrus-forward",
    "League Chew": "League Chew",
    "Marker": "Marker-family",
}


def slug_of(path: str) -> str:
    return path.strip().rstrip("/").split("/")[-1]


def anchor(url: str, text: str) -> str:
    return f'<a href="{url}">{text}</a>'


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def link_existing_mention(markup: str, text: str, url: str) -> str | None:
    """Wrap the first plain-text occurrence of `text`, if there is one.

    Only matches inside a paragraph or list item, never inside a heading or an
    existing anchor — linking a heading looks wrong and nesting anchors is
    invalid.
    """
    if not markup or not text:
        return None

    pattern = re.compile(
        r"(?<![\w>])" + r"[\s\-]+".join(re.escape(w) for w in text.split()) + r"(?![\w<])",
        re.I)

    out, changed = [], False
    for block in re.split(r"(<[^>]+>)", markup):
        if changed or block.startswith("<"):
            out.append(block)
            continue
        m = pattern.search(block)
        if m:
            out.append(block[:m.start()] + anchor(url, m.group(0)) + block[m.end():])
            changed = True
        else:
            out.append(block)
    if not changed:
        return None

    rebuilt = "".join(out)
    # reject if the new anchor landed inside a heading or another anchor
    for bad in re.finditer(r"(?is)<(h[1-6])[^>]*>.*?</\1>|<a\b[^>]*>.*?</a>", rebuilt):
        span = bad.group(0)
        if span.count("<a ") > 1 or (span.startswith("<h") and url in span):
            return None
    return rebuilt


def append_sentence(markup: str, sentence: str) -> str:
    return (markup.rstrip() + f"\n<p>{sentence}</p>").strip()


def place(meta: dict, kind: str, sentence: str, text: str, url: str) -> tuple[str, str]:
    """Add one link to the most suitable field. Returns (field, how)."""
    fields = [f for f in PLACEMENT[kind] if meta.get(f)]
    if not fields:
        fields = ["about_html"]
        meta.setdefault("about_html", "")

    # already linked from a previous run
    for f in PLACEMENT[kind] + ["about_html"]:
        if url in (meta.get(f) or ""):
            return f, "already linked"

    for f in fields:
        linked = link_existing_mention(meta[f], text, url)
        if linked:
            meta[f] = linked
            return f, "linked existing mention"

    target = fields[0]
    meta[target] = append_sentence(meta[target], sentence)
    return target, "added sentence"


def build_updates(row: dict, meta: dict) -> tuple[dict, list[str]]:
    """Return the changed prose fields plus a log of what happened."""
    working = {k: meta.get(k, "") for k in
               ("about_html", "effects_html", "flavor_html",
                "jar_html", "cultivation_html", "use_html")}
    before = dict(working)
    log = []

    family = FAMILY_PHRASE.get(row["Family"].strip(), row["Family"].strip())

    rel = [("related_1", row.get("Link 2 - related strain"), row.get("Anchor 2")),
           ("related_2", row.get("Link 3 - related strain"), row.get("Anchor 3"))]
    for i, (kind, target, text) in enumerate(rel):
        target = (target or "").strip()
        text = (text or "").strip()
        if not target or not text:
            continue
        url = f"{SITE}/strain/{slug_of(target)}/"
        if i == 0:
            sentence = (f"If you want to compare, {anchor(url, text)} is another "
                        f"{family} pick on our shelf.")
        else:
            sentence = (f"{anchor(url, text)} sits in the same {family} group if "
                        f"you are working your way through them.")
        field, how = place(working, kind, sentence, text, url)
        log.append(f"{text} -> {field} ({how})")

    hub_sentence = (f"Browse {anchor(HUB_URL, HUB_ANCHOR)} to see everything we are "
                    f"carrying right now.")
    field, how = place(working, "hub", hub_sentence, HUB_ANCHOR, HUB_URL)
    log.append(f"{HUB_ANCHOR} -> {field} ({how})")

    changed = {k: v for k, v in working.items() if v != before.get(k)}
    return changed, log


def verify(meta: dict, row: dict) -> list[str]:
    blob = json.dumps(meta, ensure_ascii=False)
    problems = []

    external = {u for u in re.findall(r'https?://[^\s"\'<>\\)]+', blob)
                if "evergreenoc.com" not in u}
    if external:
        problems.append(f"external link {sorted(external)[0]}")

    expected = {HUB_URL}
    for col in ("Link 2 - related strain", "Link 3 - related strain"):
        t = (row.get(col) or "").strip()
        if t:
            expected.add(f"{SITE}/strain/{slug_of(t)}/")
    for url in expected:
        if url not in blob:
            problems.append(f"missing link {url}")

    for field, value in meta.items():
        if isinstance(value, str) and re.search(r"(?is)<a\b[^>]*>(?:(?!</a>).)*<a\b", value):
            problems.append(f"nested anchor in {field}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open(SCRATCH / "links.csv"))
            if (r.get("Strain page") or "").startswith("/strain/")]
    match = json.load(open(SCRATCH / "match.json"))
    BACKUPS.mkdir(parents=True, exist_ok=True)

    if args.only:
        rows = [r for r in rows if slug_of(r["Strain page"]) == args.only]
    if args.limit:
        rows = rows[:args.limit]

    done, failed = 0, []
    for i, row in enumerate(rows, 1):
        slug = slug_of(row["Strain page"])
        if slug not in match:
            failed.append((slug, "no staging post"))
            continue
        pid = match[slug]["id"]

        post, _ = wp.request("GET", f"/wp/v2/strain/{pid}?context=edit")
        meta = post.get("meta") or {}
        changed, log = build_updates(row, meta)

        merged = dict(meta)
        merged.update(changed)
        problems = verify(merged, row)
        if problems:
            failed.append((slug, "; ".join(problems)))
            print(f"[{i}/{len(rows)}] {slug:<24} REFUSED {problems}", flush=True)
            continue

        if args.dry_run:
            print(f"[{i}/{len(rows)}] {slug:<24} {'; '.join(log)}", flush=True)
            done += 1
            continue

        if not changed:
            print(f"[{i}/{len(rows)}] {slug:<24} already linked, nothing to do", flush=True)
            done += 1
            continue

        (BACKUPS / f"{slug}-{pid}-before-links.json").write_text(
            json.dumps(post, indent=1, ensure_ascii=False), encoding="utf-8")
        wp.request("POST", f"/wp/v2/strain/{pid}", data={"meta": changed})
        done += 1
        print(f"[{i}/{len(rows)}] {slug:<24} {len(changed)} field(s) | {'; '.join(log)}", flush=True)

    print(f"\nprocessed={done} failed={len(failed)}")
    for slug, why in failed:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
