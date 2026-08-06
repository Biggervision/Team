#!/usr/bin/env python3
"""Put the educational citations back, as nofollow links.

The migration stripped every outbound link. That was right for the competitor
directories — linking to Leafly's or AllBud's page for a strain from our own
page for that strain hands authority to the site we are trying to outrank — but
it also took out the references, and this is health content where citing
Wikipedia, PubMed or Mayo Clinic is a trust signal worth having.

So: references come back, competitors stay gone, and everything restored is
rel="nofollow" so readers get the citation while no ranking authority leaves
the site.

What counts as a reference is decided by domain *and path*, because the same
host can be both. weedmaps.com/learn/... is a glossary; weedmaps.com/strains/...
competes with us for the exact query the page targets. Same for leafly.com/news
against leafly.com/strains.

Some citations cannot be restored in place: the migration deleted whole
sentences that named a referral site ("see Project CBD's guide to..."), so
there is no anchor text left to wrap. Those are reported rather than
reinvented, since writing a new sentence to hold a link is a content decision.

    python3 tools/strain_restore_citations.py --report
    python3 tools/strain_restore_citations.py --dry-run
    python3 tools/strain_restore_citations.py
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
import wp  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")
BACKUPS = Path(__file__).resolve().parent.parent / "docs/strain-migration/backups-citations"

PROSE = ("about_html", "effects_html", "flavor_html",
         "jar_html", "cultivation_html", "use_html")

# Reference sources. Reputable health, science and general-knowledge only.
CITATION_HOSTS = (
    "en.wikipedia.org", "pmc.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
    "projectcbd.org", "mayoclinic.org", "my.clevelandclinic.org",
    "health.harvard.edu", "healthline.com", "medicalnewstoday.com",
    "who.int", "fda.gov", "nida.nih.gov", "apa.org", "psychiatry.org",
    "sciencedirect.com", "karger.com", "adai.uw.edu", "news.wsu.edu",
    "lcb.wa.gov", "norml.org", "sleepfoundation.org", "helpguide.org",
    "examine.com", "goodrx.com", "psychiatryadvisor.com", "jeffersonhealth.org",
    "www1.racgp.org.au", "caps.byu.edu",
)

# Hosts that are references on some paths and rivals on others.
MIXED_HOSTS = {
    "leafly.com": (re.compile(r"/(news|learn|info)/"), re.compile(r"/strains/")),
    "weedmaps.com": (re.compile(r"/learn/"), re.compile(r"/(strains|dispensaries)/")),
}


def is_citation(url: str) -> bool:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0].lower()
    for mixed, (good, bad) in MIXED_HOSTS.items():
        if host.endswith(mixed):
            return bool(good.search(url)) and not bad.search(url)
    return any(host.endswith(h) for h in CITATION_HOSTS)


def text_of(markup: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"(?is)<[^>]+>", " ", markup))).strip()


def citations_for(page_html: str) -> list[tuple[str, str]]:
    """(anchor text, url) for every reference on the original page."""
    out, seen = [], set()
    for m in re.finditer(r'(?is)<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page_html):
        url, anchor = m.group(1), text_of(m.group(2))
        if not anchor or len(anchor) < 3 or not url.startswith("http"):
            continue
        if not is_citation(url):
            continue
        key = (anchor.lower(), url)
        if key in seen:
            continue
        seen.add(key)
        out.append((anchor, url))
    return out


def relink(markup: str, anchor: str, url: str) -> str | None:
    """Wrap the first unlinked occurrence of `anchor` in a nofollow link."""
    if not markup or url in markup:
        return None
    pattern = re.compile(
        r"(?<![\w>])" + r"[\s\-]+".join(re.escape(w) for w in anchor.split()) + r"(?![\w<])",
        re.I)
    parts = re.split(r"(<[^>]+>)", markup)
    inside_anchor = False
    for i, part in enumerate(parts):
        if part.startswith("<"):
            low = part.lower()
            if low.startswith("<a "):
                inside_anchor = True
            elif low.startswith("</a"):
                inside_anchor = False
            continue
        if inside_anchor:
            continue
        m = pattern.search(part)
        if m:
            parts[i] = (part[:m.start()]
                        + f'<a href="{url}" rel="nofollow noopener" target="_blank">'
                        + m.group(0) + "</a>" + part[m.end():])
            return "".join(parts)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="show what would come back, no site calls")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()

    pages = json.load(open(SCRATCH / "prod-pages.json"))
    names = json.load(open(SCRATCH / "strain-names.json"))
    BACKUPS.mkdir(parents=True, exist_ok=True)

    if args.report:
        total, hosts = 0, {}
        for slug, page in pages.items():
            for anchor, url in citations_for((page.get("content") or {}).get("rendered", "")):
                total += 1
                host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
                hosts[host] = hosts.get(host, 0) + 1
        print(f"citations available to restore: {total}\n")
        for host, n in sorted(hosts.items(), key=lambda x: -x[1]):
            print(f"  {n:>4}  {host}")
        return 0

    targets = {args.only: names[args.only]} if args.only else names
    restored = placed = missing = 0
    per_strain = {}
    failed = []

    for i, (slug, info) in enumerate(sorted(targets.items()), 1):
        page = pages.get(slug)
        if not page:
            continue
        cites = citations_for((page.get("content") or {}).get("rendered", ""))
        if not cites:
            continue
        try:
            post, _ = wp.request("GET", f"/wp/v2/strain/{info['id']}?context=edit")
            meta = post.get("meta") or {}
            working = {f: meta.get(f, "") or "" for f in PROSE}
            before = dict(working)

            hit = miss = 0
            for anchor, url in cites:
                done = False
                for field in PROSE:
                    out = relink(working[field], anchor, url)
                    if out:
                        working[field] = out
                        done = True
                        break
                hit += done
                miss += not done

            restored += hit
            missing += miss
            changed = {k: v for k, v in working.items() if v != before[k]}
            per_strain[slug] = (hit, miss)

            if not changed:
                print(f"[{i}/{len(targets)}] {slug:<22} nothing to place "
                      f"({miss} had no anchor text left)", flush=True)
                continue

            if args.dry_run:
                print(f"[{i}/{len(targets)}] {slug:<22} would restore {hit}, "
                      f"{miss} unplaceable", flush=True)
                placed += 1
                continue

            (BACKUPS / f"{slug}-{info['id']}-before-citations.json").write_text(
                json.dumps(post, indent=1, ensure_ascii=False), encoding="utf-8")
            wp.request("POST", f"/wp/v2/strain/{info['id']}", data={"meta": changed})
            placed += 1
            print(f"[{i}/{len(targets)}] {slug:<22} restored {hit} in "
                  f"{len(changed)} field(s), {miss} unplaceable", flush=True)
            time.sleep(0.5)
        except Exception as exc:
            failed.append((slug, str(exc)[:90]))
            print(f"[{i}/{len(targets)}] {slug:<22} FAILED {str(exc)[:70]}", flush=True)

    print(f"\nstrains updated={placed}  citations restored={restored}  "
          f"unplaceable={missing}  failed={len(failed)}")
    for slug, why in failed:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
