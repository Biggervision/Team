#!/usr/bin/env python3
"""Add the Cultivation and How to Use sections to the strain template.

The strain post type gained `cultivation_*` and `use_*` fields, and the copy
was migrated into them — but adding fields to a post type does not add anything
to the layout, so that copy was stored and invisible. This builds the two
missing sections into the Elementor single template.

Target: elementor_library #14266 ("single-post", condition include/singular/strain).
That one template renders all 96 strains, so it is backed up before any write.

Rather than authoring new widgets from scratch, each section is deep-copied
from an existing one that already has every style setting dialled in, then
rebound to the new fields:

  Cultivation  <- clone of Appearance (dark)   fields: cultivation_headline,
                                                       cultivation_html,
                                                       grow_specs via .eg-spec
  How to Use   <- clone of The Strain (cream)  fields: use_headline,
                                                       use_html,
                                                       use_methods via .eg-glance

Both repeaters carry label/value-shaped data, which is exactly what .eg-spec
(dark) and .eg-glance (cream) already style. Sections are inserted after Flavor
so the page order follows the field tab order, which also keeps the existing
cream/dark alternation unbroken. The numbered eyebrows are resequenced.

Run:  python3 tools/strain_template_sections.py [--dry-run]
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

TEMPLATE_ID = 14266

# eyebrow labels in final page order
EYEBROWS = [
    "01 · The Strain",
    "02 · Effects",
    "03 · Flavor & Aroma",
    "04 · Cultivation",
    "05 · How to Use",
    "06 · Appearance",
    "07 · How to Order",
    "08 · Similar Strains",
    "09 · FAQ",
]


def new_id(used: set[str]) -> str:
    """Elementor element ids are 7 hex chars and must be unique per document."""
    while True:
        candidate = "%07x" % random.randrange(16**7)
        if candidate not in used:
            used.add(candidate)
            return candidate


def collect_ids(elements: list, into: set[str]) -> set[str]:
    for el in elements:
        if el.get("id"):
            into.add(el["id"])
        collect_ids(el.get("elements") or [], into)
    return into


def reid(element: dict, used: set[str]) -> dict:
    element["id"] = new_id(used)
    for child in element.get("elements") or []:
        reid(child, used)
    return element


def walk(element: dict):
    yield element
    for child in element.get("elements") or []:
        yield from walk(child)


def rebind(container: dict, headline: str, html: str,
           repeater_source: str, repeater_format: str, repeater_class: str) -> dict:
    """Point a cloned section's three widgets at the new fields."""
    fields = [e for e in walk(container)
              if e.get("widgetType") == "jet-listing-dynamic-field"]
    repeaters = [e for e in walk(container)
                 if e.get("widgetType") == "jet-listing-dynamic-repeater"]

    if len(fields) < 2 or not repeaters:
        raise SystemExit(f"unexpected section shape: {len(fields)} fields, {len(repeaters)} repeaters")

    fields[0]["settings"]["dynamic_field_post_meta_custom"] = headline
    fields[1]["settings"]["dynamic_field_post_meta_custom"] = html

    rep = repeaters[0]["settings"]
    rep["dynamic_field_source"] = repeater_source
    rep["dynamic_field_format"] = repeater_format
    rep["_css_classes"] = repeater_class
    return container


def set_eyebrow(container: dict, text: str) -> None:
    for el in walk(container):
        if el.get("widgetType") == "heading":
            el["settings"]["title"] = text
            return


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tpl, _ = wp.request("GET", f"/wp/v2/elementor_library/{TEMPLATE_ID}?context=edit")
    meta = tpl.get("meta") or {}
    data = json.loads(meta["_elementor_data"])
    print(f"template: {(tpl.get('title') or {}).get('raw')}  sections={len(data)}")

    if any("cultivation_headline" in json.dumps(sec) for sec in data):
        print("Cultivation section already present — nothing to do.")
        return 0

    used = collect_ids(data, set())

    # index 4 is Appearance (dark), index 1 is The Strain (cream)
    cultivation = reid(copy.deepcopy(data[4]), used)
    rebind(cultivation,
           headline="cultivation_headline",
           html="cultivation_html",
           repeater_source="grow_specs",
           repeater_format='<div class="sl">%label%</div><div class="sv">%value%</div>',
           repeater_class="eg-spec")
    set_eyebrow(cultivation, "04 · Cultivation")

    how_to_use = reid(copy.deepcopy(data[1]), used)
    rebind(how_to_use,
           headline="use_headline",
           html="use_html",
           repeater_source="use_methods",
           repeater_format='<div class="gl">%label%</div><div class="gv">%text%</div>',
           repeater_class="eg-glance")
    set_eyebrow(how_to_use, "05 · How to Use")

    data[4:4] = [cultivation, how_to_use]

    # resequence the numbered eyebrows across the prose sections
    numbered = [sec for sec in data
                if any(e.get("widgetType") == "heading" for e in walk(sec))]
    for sec, label in zip(numbered, EYEBROWS):
        set_eyebrow(sec, label)

    print(f"sections after insert: {len(data)}")
    for i, sec in enumerate(data):
        heads = [e["settings"].get("title") for e in walk(sec)
                 if e.get("widgetType") == "heading"]
        binds = [e["settings"].get("dynamic_field_post_meta_custom") for e in walk(sec)
                 if e.get("widgetType") == "jet-listing-dynamic-field"]
        binds = [b for b in binds if b]
        print(f"  [{i}] {heads[0] if heads else '(no eyebrow)':<22} {binds[:2]}")

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    wp.request("POST", f"/wp/v2/elementor_library/{TEMPLATE_ID}", data={
        "meta": {"_elementor_data": json.dumps(data, ensure_ascii=False)},
    })
    print(f"\nwrote template {TEMPLATE_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
