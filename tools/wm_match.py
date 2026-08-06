#!/usr/bin/env python3
"""Match strain pages to live Weedmaps menu items.

The menu names products for shoppers, not for machines. The same strain can
appear as any of:

    ⚫️ MEGA Z (DARK) (3.5g)
    Teds Budz | Lemon Tree | 3.5g
    Zangbanger | Indoor Flower | 3.5g      <- strain sits in the brand slot
    Sour Power OG

so a name is reduced to candidate phrases — the whole thing, and each
pipe-separated segment — with emoji, weights, and packaging words stripped from
each. A strain matches if any candidate equals its name.

Only flower categories are considered (Indica / Sativa / Hybrid). Concentrates
and edibles carry strain names too, but a strain page priced off a gram of
badder would be wrong.

Where several items match, the one closest to an eighth wins, since that is the
unit the page's price note quotes, preferring items that are actually orderable.

    python3 tools/wm_match.py            # summary
    python3 tools/wm_match.py --full     # per-strain detail
    python3 tools/wm_match.py --json OUT # write the mapping
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")

FLOWER_CATEGORIES = {"Indica", "Sativa", "Hybrid"}

# Those categories also carry infused prerolls, blunts and vapes, which are
# priced per unit rather than per weight. Quoting a strain page's eighth off a
# five-pack of infused prerolls would misprice it for the customer, so anything
# that is not loose flower is excluded.
NOT_FLOWER = re.compile(
    r"\b(infused|pre[\s-]?roll|prerolls?|blunt|joint|cart|cartridge|vape|"
    r"disposable|dispo|diamond|resin|rosin|sauce|badder|shatter|hash|"
    r"gummies|gummy|edible|drink|tincture|pod)\b", re.I)

# packaging and format words that are never part of a strain name
NOISE = re.compile(
    r"\b(indoor|outdoor|greenhouse|flower|bag|bags|jar|smalls|mylar|"
    r"black|white|grey|gray|label|top\s*shelf|premium|exotic|pack|packs|"
    r"preroll|pre[- ]roll|infused|oz|ounce|gram|grams|g|lb)\b", re.I)

WEIGHT = re.compile(r"\(?\b\d+(?:\.\d+)?\s*(?:g|gram|grams|oz|mg)\b\)?|\b\d/\d\b|#\d+", re.I)


def strip_emoji(s: str) -> str:
    return "".join(c for c in s if unicodedata.category(c) not in ("So", "Sk", "Cf"))


def normalise(s: str) -> str:
    s = strip_emoji(s)
    s = WEIGHT.sub(" ", s)
    s = NOISE.sub(" ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def candidates(name: str) -> set[str]:
    """Every phrase in a product name that might be the strain."""
    out = {normalise(name)}
    for part in re.split(r"[|/–—-]", name):
        n = normalise(part)
        if n:
            out.add(n)
    return {c for c in out if len(c) > 2}


def is_unit_priced(item: dict) -> bool:
    """True when the price is per item rather than per weight."""
    label = ((item.get("price") or {}).get("label") or "").lower()
    return not label or "each" in label or "pk" in label or "pack" in label


def eighth_score(item: dict) -> tuple:
    """Rank candidate items: orderable first, then closest to an eighth."""
    price = item.get("price") or {}
    label = (price.get("label") or "").lower()
    net = price.get("complianceNetMg") or price.get("compliance_net_mg") or 0
    is_eighth = "1/8" in label or net == 3500
    orderable = bool(item.get("isOnlineOrderable", item.get("is_online_orderable")))
    return (not orderable, not is_eighth, abs((net or 0) - 3500))


def item_price(item: dict) -> dict:
    p = item.get("price") or {}
    return {
        "price": p.get("price"),
        "label": p.get("label"),
        "on_sale": p.get("onSale", p.get("on_sale")),
        "original": p.get("originalPrice", p.get("original_price")),
    }


def item_image(item: dict) -> str | None:
    img = item.get("avatarImage") or item.get("avatar_image") or {}
    if isinstance(img, dict):
        return (img.get("largeUrl") or img.get("large_url")
                or img.get("originalUrl") or img.get("original_url"))
    return None


def build(strains: dict, menu: list[dict]) -> dict:
    flower = [i for i in menu
              if (i.get("category") or {}).get("name") in FLOWER_CATEGORIES
              and not NOT_FLOWER.search(i.get("name", ""))
              and not is_unit_priced(i)]

    index: dict[str, list[dict]] = {}
    for item in flower:
        for c in candidates(item.get("name", "")):
            index.setdefault(c, []).append(item)

    result = {}
    for slug, info in strains.items():
        key = normalise(info["name"])
        hits = index.get(key, [])

        if not hits and len(key.split()) >= 2:
            # Brand prefixes are not always pipe-separated: "710 Labs Cherry
            # Zest #4 Flower 14g" hides the strain mid-string. Fall back to a
            # whole-word containment match — but only for multi-word names.
            # A one-word name like "Runtz" would otherwise swallow Rainbow
            # Runtz, Black Runtz and White Runtz, which are different strains.
            probe = re.compile(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])")
            hits = [i for i in flower if probe.search(normalise(i.get("name", "")))]

        if not hits:
            result[slug] = {"available": False, "matches": 0}
            continue
        best = sorted(hits, key=eighth_score)[0]
        result[slug] = {
            "available": True,
            "matches": len(hits),
            "menu_name": best.get("name"),
            "menu_slug": best.get("slug"),
            "orderable": bool(best.get("isOnlineOrderable", best.get("is_online_orderable"))),
            "category": (best.get("category") or {}).get("name"),
            **item_price(best),
            "image": item_image(best),
        }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--json", help="write the mapping to this path")
    args = ap.parse_args()

    menu = json.load(open(SCRATCH / "wm-menu.json"))
    strains = json.load(open(SCRATCH / "strain-names.json"))
    mapping = build(strains, menu)

    have = {k: v for k, v in mapping.items() if v["available"]}
    print(f"strains          : {len(mapping)}")
    print(f"on the menu      : {len(have)}")
    print(f"not on the menu  : {len(mapping) - len(have)}")
    if have:
        priced = [v for v in have.values() if v.get("price") is not None]
        imaged = [v for v in have.values() if v.get("image")]
        print(f"  with a price   : {len(priced)}")
        print(f"  with an image  : {len(imaged)}")
        eighths = [v for v in priced if "1/8" in (v.get("label") or "")]
        print(f"  priced per 1/8 : {len(eighths)}")

    if args.full:
        print()
        for slug, v in sorted(mapping.items()):
            if v["available"]:
                print(f"  {slug:<24} ${v['price']:<7} {v['label']:<9} "
                      f"{'orderable' if v['orderable'] else 'not orderable':<14} {v['menu_name'][:44]}")
            else:
                print(f"  {slug:<24} -- not on menu")

    if args.json:
        Path(args.json).write_text(json.dumps(mapping, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
