#!/usr/bin/env python3
"""Hide the Cultivation and How to Use sections on strains that have no copy yet.

Both sections were added to the strain template before most strains have any
content for them. The dynamic field widgets carry `hide_if_empty`, so they drop
out on their own — but the container and its numbered eyebrow do not, leaving
an empty labelled band on every strain not yet migrated. That is currently 95 of
96, including the two published ones.

This tags both containers with `eg-optional-sect` and adds a rule to the
existing prose snippet that hides such a section when it contains no JetEngine
output at all. Once a strain gets Cultivation copy, a `.jet-listing` wrapper
appears inside and the section shows itself.

Run:  python3 tools/strain_template_optional.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

TEMPLATE_ID = 14266
SNIPPET_ID = 14574
MARKER = "eg-optional-sect"

RULE = """
/* Optional sections (Cultivation, How to Use): a strain without that copy
   renders the container and its eyebrow but no JetEngine output, which reads
   as an empty band. Hide until there is something to show. */
.eg-optional-sect:not(:has(.jet-listing)){display:none!important}
"""


def walk(el: dict):
    yield el
    for child in el.get("elements") or []:
        yield from walk(child)


def target_containers(data: list) -> list[dict]:
    """The two sections bound to the cultivation_* / use_* fields."""
    wanted = {"cultivation_headline", "use_headline"}
    out = []
    for section in data:
        binds = {e.get("settings", {}).get("dynamic_field_post_meta_custom")
                 for e in walk(section)}
        if binds & wanted:
            out.append(section)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tpl, _ = wp.request("GET", f"/wp/v2/elementor_library/{TEMPLATE_ID}?context=edit")
    data = json.loads(tpl["meta"]["_elementor_data"])

    targets = target_containers(data)
    if len(targets) != 2:
        raise SystemExit(f"expected 2 optional sections, found {len(targets)}")

    for section in targets:
        settings = section.setdefault("settings", {})
        classes = settings.get("css_classes", "")
        if MARKER not in classes.split():
            settings["css_classes"] = f"{classes} {MARKER}".strip()
        eyebrow = next((e["settings"].get("title") for e in walk(section)
                        if e.get("widgetType") == "heading"), "?")
        print(f"  {section['id']}  {eyebrow:<20} classes -> '{settings['css_classes']}'")

    snippet, _ = wp.request("GET", f"/wp/v2/elementor_snippet/{SNIPPET_ID}?context=edit")
    code = snippet["meta"]["_elementor_code"]
    if MARKER in code:
        print("snippet already carries the rule")
        new_code = code
    else:
        new_code = code.replace("</style>", RULE + "</style>")
        print(f"snippet: {len(code)} -> {len(new_code)} chars")

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    wp.request("POST", f"/wp/v2/elementor_library/{TEMPLATE_ID}",
               data={"meta": {"_elementor_data": json.dumps(data, ensure_ascii=False)}})
    print("template updated")

    if new_code != code:
        wp.request("POST", f"/wp/v2/elementor_snippet/{SNIPPET_ID}",
                   data={"meta": {"_elementor_code": new_code}})
        print("snippet updated")

    wp.request("DELETE", "/elementor/v1/cache")
    wp.request("PUT", "/siteground-optimizer/v1/purge-cache")
    print("caches cleared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
