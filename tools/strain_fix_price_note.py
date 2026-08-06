#!/usr/bin/env python3
"""Clear the developer placeholder out of the price area, and finish pricing.

The strain build shipped with `price_note` set to

    / eighth · TODO(Pro): confirm live price

which renders in the hero. It went unnoticed while the pages were drafts and
became publicly visible on all 97 the moment they were published — 89 of them
still carried it.

Two different fixes, depending on whether we stock the strain:

* stocked (per the Weedmaps menu): write the real price and a note naming the
  unit that price is for
* not stocked: clear both fields, so the hero simply omits the price rather
  than showing a note addressed to a developer

Images are left alone here; they are handled separately.

    python3 tools/strain_fix_price_note.py --dry-run
    python3 tools/strain_fix_price_note.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp                       # noqa: E402
import strain_apply_menu as am  # noqa: E402

SCRATCH = Path("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad")

PLACEHOLDER = re.compile(r"todo", re.I)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    names = json.load(open(SCRATCH / "strain-names.json"))
    menu = json.load(open(SCRATCH / "wm-map.json"))

    priced, cleared, skipped, failed = [], [], [], []

    for i, (slug, info) in enumerate(sorted(names.items()), 1):
        pid = info["id"]
        try:
            post, _ = wp.request("GET", f"/wp/v2/strain/{pid}?context=edit&_fields=id,meta")
            meta = post.get("meta") or {}
            note = (meta.get("price_note") or "").strip()
            price = (meta.get("price") or "").strip()
            entry = menu.get(slug) or {}

            if entry.get("available"):
                want_price = am.money(entry["price"])
                want_note = am.price_note(entry)
                action = "price"
            else:
                want_price, want_note, action = "", "", "clear"

            if price == want_price and note == want_note:
                skipped.append(slug)
                continue

            if args.dry_run:
                print(f"[{i}/{len(names)}] {slug:<24} {action:<6} "
                      f"{note!r} -> {want_note!r}", flush=True)
                (priced if action == "price" else cleared).append(slug)
                continue

            wp.request("POST", f"/wp/v2/strain/{pid}",
                       data={"meta": {"price": want_price, "price_note": want_note}})
            (priced if action == "price" else cleared).append(slug)
            print(f"[{i}/{len(names)}] {slug:<24} {action:<6} "
                  f"price={want_price or '(none)':<7} note={want_note or '(none)'}", flush=True)
            time.sleep(0.4)
        except Exception as exc:
            failed.append((slug, str(exc)[:100]))
            print(f"[{i}/{len(names)}] {slug:<24} FAILED {str(exc)[:70]}", flush=True)

    print(f"\npriced={len(priced)} cleared={len(cleared)} "
          f"already-correct={len(skipped)} failed={len(failed)}")
    for slug, why in failed:
        print(f"  FAILED {slug}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
