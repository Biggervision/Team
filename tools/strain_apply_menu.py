#!/usr/bin/env python3
"""Set price and featured image on strains we actually stock.

Reads the match between strain pages and the live Weedmaps menu, then for each
strain that is genuinely on the menu as flower: writes the price, rewrites the
price note to name the unit that price is for, and sideloads the product photo
as the featured image.

Two deliberate limits:

* Only loose flower counts. The Indica/Sativa/Hybrid categories also carry
  infused prerolls, blunts and vapes; quoting a strain page's price off a
  five-pack of prerolls would misprice it for the customer.
* The unit is carried through rather than assumed. Most matches are eighths but
  some are quarters or half-ounces, so the note says which — a $150 half-ounce
  labelled "per eighth" would be a serious misquote.

Strains not on the menu are left untouched, with their price blank, so the page
never advertises a price for something that cannot be bought.

    python3 tools/strain_apply_menu.py --dry-run
    python3 tools/strain_apply_menu.py --only zamosa
    python3 tools/strain_apply_menu.py
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")
BACKUPS = Path(__file__).resolve().parent.parent / "docs/strain-migration/backups-menu"

UNIT_LABEL = {
    "1/8 oz": "eighth",
    "1/4 oz": "quarter",
    "1/2 oz": "half ounce",
    "1 oz": "ounce",
    "1 g": "gram",
    "2 g": "2 grams",
}


def money(value) -> str:
    if value is None:
        return ""
    return f"${value:,.0f}" if float(value).is_integer() else f"${value:,.2f}"


def price_note(entry: dict) -> str:
    label = (entry.get("label") or "").strip()
    unit = UNIT_LABEL.get(label, label or "unit")
    note = f"per {unit} · live menu price"
    if entry.get("on_sale") and entry.get("original") and entry["original"] != entry["price"]:
        note += f" · was {money(entry['original'])}"
    return note


def fetch_image(url: str) -> tuple[bytes, str, str]:
    req = urllib.request.Request(url, headers={"Accept": "image/*"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        ctype = resp.headers.get("content-type", "image/jpeg").split(";")[0]
    name = url.split("/")[-1].split("?")[0]
    if "." not in name:
        name += mimetypes.guess_extension(ctype) or ".jpg"
    return data, ctype, name


def upload_image(url: str, title: str) -> int | None:
    data, ctype, filename = fetch_image(url)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", filename)[:90]
    media, _ = wp.request(
        "POST", "/wp/v2/media", body=data, content_type=ctype,
        extra_headers={"Content-Disposition": f'attachment; filename="{safe}"'})
    mid = media.get("id")
    if mid:
        wp.request("POST", f"/wp/v2/media/{mid}", data={
            "title": title,
            "alt_text": title,
        })
    return mid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()

    mapping = json.load(open(SCRATCH / "wm-map.json"))
    strains = json.load(open(SCRATCH / "strain-names.json"))
    BACKUPS.mkdir(parents=True, exist_ok=True)

    targets = {k: v for k, v in mapping.items() if v.get("available")}
    if args.only:
        targets = {k: v for k, v in targets.items() if k == args.only}

    done, failed = [], []
    for i, (slug, entry) in enumerate(sorted(targets.items()), 1):
        pid = strains[slug]["id"]
        name = strains[slug]["name"]
        meta = {"price": money(entry["price"]), "price_note": price_note(entry)}

        if args.dry_run:
            print(f"[{i}/{len(targets)}] {slug:<22} {meta['price']:<7} "
                  f"{meta['price_note']:<42} img={'yes' if entry.get('image') else 'no'}", flush=True)
            done.append(slug)
            continue

        try:
            before, _ = wp.request("GET", f"/wp/v2/strain/{pid}?context=edit")
            (BACKUPS / f"{slug}-{pid}-before-menu.json").write_text(
                json.dumps(before, indent=1, ensure_ascii=False), encoding="utf-8")

            payload = {"meta": meta}
            if entry.get("image") and not before.get("featured_media"):
                mid = upload_image(entry["image"], f"{name} — Evergreen OC")
                if mid:
                    payload["featured_media"] = mid
            wp.request("POST", f"/wp/v2/strain/{pid}", data=payload)
            done.append(slug)
            print(f"[{i}/{len(targets)}] {slug:<22} {meta['price']:<7} "
                  f"{meta['price_note']:<42} "
                  f"featured={payload.get('featured_media', before.get('featured_media') or 'none')}",
                  flush=True)
        except Exception as exc:
            failed.append((slug, str(exc)[:130]))
            print(f"[{i}/{len(targets)}] {slug:<22} FAILED {str(exc)[:90]}", flush=True)

    print(f"\nupdated={len(done)} failed={len(failed)}")
    for slug, why in failed:
        print(f"  FAILED {slug}: {why}")

    absent = [k for k, v in mapping.items() if not v.get("available")]
    print(f"\nleft untouched (not on the menu): {len(absent)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
