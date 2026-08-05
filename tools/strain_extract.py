#!/usr/bin/env python3
"""Turn a live strain page into field values for the staging strain template.

The live pages follow a consistent nine-section shape ("1. What Is X?",
"2. ... Composition Breakdown", ... "9. Why Choose Us"), so sections are located
by heading and mapped onto the template's fields.

Three things happen to the copy on the way through, all of them deliberate:

* Outbound links are unwrapped, not deleted. The anchors sit mid-sentence and
  carry keywords, so removing the link while keeping the words preserves the
  ranking value that the whole migration exists to protect.
* Headings are pinned to `h3`. The template already emits the page's only `h1`
  and an `h2` per section.
* Ordering CTAs are repointed at the internal menu instead of Weedmaps.

Structured values — the at-a-glance table, terpenes, FAQs, grow specs — are
pulled out of the prose into their repeaters so they render as designed rather
than as a wall of text.

Used by strain_migrate.py; can also be run alone to inspect one strain:

    python3 tools/strain_extract.py <slug> [--json]
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
from pathlib import Path

SHOP_URL = "https://staging2.evergreenoc.com/shop/"
STRAIN_HUB_URL = "https://staging2.evergreenoc.com/strain-hub/"

PROD_PAGES = ("/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1"
              "/scratchpad/prod-pages.json")

# Section heading -> internal key. Matched case-insensitively as a substring,
# in this order, so "how to use" is tested before the looser "use".
SECTION_PATTERNS = [
    ("about",       r"what\s+is\b"),
    ("composition", r"composition\s+breakdown"),
    ("effects",     r"effects?\s+and\s+benefits"),
    ("flavor",      r"flavou?r\s+and\s+aroma"),
    ("cultivation", r"cultivation\s+tips|growing\s+"),
    ("use",         r"how\s+to\s+use"),
    ("jar",         r"physical\s+appearance|appearance\s+of"),
    ("faq",         r"frequently\s+asked|^faqs?\b"),
    ("why",         r"why\s+choose"),
]

GLANCE_LABELS = ["THC Content", "CBD Content", "Lineage", "Flavor & Aroma",
                 "Flavor and Aroma", "Effects", "Primary Effects", "Best For",
                 "Genetics"]

GROW_LABELS = ["Difficulty", "Climate", "Plant Structure", "Flowering Time",
               "Indoor Yield", "Outdoor Yield", "Growing Techniques",
               "Growing Medium", "Bud Structure", "Coloration",
               "Trichome Coverage", "Temperature Control", "Humidity Management",
               "Nutrient Balance", "Pest Control", "Indoor Setup", "Outdoor Setup"]

# Sites the copy sends readers to. Unwrapping the anchor leaves the referral
# sentence behind ("refer to Weedmaps' guide to terpenes"), which still points
# customers at a directory, so the sentence goes too. Cali Connection is
# deliberately absent — it is the breeder, cited as lineage fact, not a referral.
REFERRAL_BRANDS = ("Weedmaps", "Leafly", "AllBud", "Hytiva", "CannaConnection",
                   "Project CBD", "Yelp", "Wikipedia", "Herbies", "Seedsman")

TERPENE_NAMES = ["Myrcene", "Limonene", "Caryophyllene", "Pinene", "Linalool",
                 "Terpinolene", "Humulene", "Ocimene", "Bisabolol", "Valencene"]


# ---------------------------------------------------------------------------
# html helpers
# ---------------------------------------------------------------------------


def text_of(markup: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"(?is)<[^>]+>", " ", markup))).strip()


def strip_links(markup: str) -> str:
    """Unwrap every anchor, keeping its text."""
    return re.sub(r"(?is)<a\b[^>]*>(.*?)</a>", r"\1", markup)


def to_h3(markup: str) -> str:
    def demote(m: re.Match) -> str:
        level = int(m.group(1)[1])
        tag = "h3" if level <= 3 else "h4"
        inner = text_of(m.group(2))
        return f"<{tag}>{inner}</{tag}>" if inner else ""
    return re.sub(r"(?is)<(h[1-6])[^>]*>(.*?)</\1>", demote, markup)


def strip_referrals(inner: str) -> str:
    """Drop sentences that exist only to send the reader to another site."""
    parts = re.split(r"(?<=[.!?])\s+", inner)
    kept = [p for p in parts
            if not any(b.lower() in text_of(p).lower() for b in REFERRAL_BRANDS)]
    return " ".join(kept).strip()


def clean_block(markup: str) -> str:
    """Reduce a section to clean paragraphs, lists and h3s."""
    out = strip_links(markup)
    out = re.sub(r"(?is)<(script|style|noscript|form|svg|iframe)[^>]*>.*?</\1>", "", out)
    out = to_h3(out)

    kept: list[str] = []
    for m in re.finditer(r"(?is)<(h3|h4|p|li)[^>]*>(.*?)</\1>", out):
        tag, inner = m.group(1).lower(), m.group(2)
        inner = re.sub(r"(?is)</?(?!strong\b|em\b|b\b|i\b)[a-z][^>]*>", "", inner).strip()
        # the source wraps text in <strong data-start=".." data-end=".."> — drop
        # the attributes so the stored markup stays readable in the editor
        inner = re.sub(r"(?is)<(strong|em|b|i)\b[^>]*>", r"<\1>", inner)
        inner = re.sub(r"(?is)<(b|i)>", lambda m: "<strong>" if m.group(1) == "b" else "<em>", inner)
        inner = re.sub(r"(?is)</(b|i)>", lambda m: "</strong>" if m.group(1) == "b" else "</em>", inner)
        inner = re.sub(r"\s+", " ", inner)
        inner = strip_referrals(inner)
        if len(text_of(inner)) < 2:
            continue
        kept.append((tag, inner))

    # collapse runs of <li> into a single list
    html_parts: list[str] = []
    i = 0
    while i < len(kept):
        tag, inner = kept[i]
        if tag == "li":
            items = []
            while i < len(kept) and kept[i][0] == "li":
                items.append(f"<li>{kept[i][1]}</li>")
                i += 1
            html_parts.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        html_parts.append(f"<{tag}>{inner}</{tag}>")
        i += 1

    # drop duplicate consecutive blocks (live pages repeat the intro in places)
    deduped: list[str] = []
    for part in html_parts:
        if not deduped or deduped[-1] != part:
            deduped.append(part)
    return "\n".join(deduped).strip()


def first_sentence(markup: str, limit: int = 190) -> str:
    body = text_of(markup)
    m = re.match(r"(.{40,%d}?[.!?])\s" % limit, body)
    return (m.group(1) if m else body[:limit]).strip()


# ---------------------------------------------------------------------------
# sectioning
# ---------------------------------------------------------------------------


def split_sections(markup: str) -> dict[str, str]:
    """Slice the page into named sections using its numbered headings."""
    heads = []
    for m in re.finditer(r"(?is)<(h[1-4])[^>]*>(.*?)</\1>", markup):
        title = text_of(m.group(2))
        if not title:
            continue
        heads.append((m.start(), m.end(), title))

    marks: list[tuple[int, str, str]] = []
    for start, end, title in heads:
        probe = re.sub(r"^\s*\d+[.)]\s*", "", title).strip()
        for key, pattern in SECTION_PATTERNS:
            if re.search(pattern, probe, re.I):
                if key not in [k for _, k, _ in marks]:
                    marks.append((end, key, title))
                break

    marks.sort()
    out: dict[str, str] = {}
    for i, (pos, key, title) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(markup)
        # trim the trailing heading of the next section
        chunk = markup[pos:stop]
        chunk = re.sub(r"(?is)<h[1-4][^>]*>[^<]*$", "", chunk)
        out[key] = chunk
        out[f"{key}__title"] = title
    return out


def strong_pairs(markup: str) -> list[tuple[str, str]]:
    """Pull every "Label: value" pair out of a block, however it is marked up.

    The live pages use three shapes interchangeably:
        <li><p><strong>Lineage:</strong> Tahoe OG x Alien Kush</p></li>
        <p><strong>Difficulty:</strong> Moderate<br> ...description...</p>
        <p><strong>THC Content: 22% - 28%</strong><br> ...description...</p>
    All three put the label in a leading <strong>; the value is either inside it
    after the colon, or in the text that follows up to the first <br>.
    """
    pairs: list[tuple[str, str]] = []
    for block in re.finditer(r"(?is)<(p|li)[^>]*>(.*?)</\1>", markup):
        # a block often stacks several labels separated by <br>, so treat each
        # line as its own candidate rather than taking only the first
        for line in re.split(r"(?i)<br\b[^>]*>", block.group(2)):
            m = re.search(r"(?is)<strong[^>]*>(.*?)</strong>(.*)$", line)
            if not m:
                continue
            head, rest = text_of(m.group(1)), m.group(2)
            if ":" in head:
                label, _, inline = head.partition(":")
                value = inline.strip()
            else:
                label, value = head.rstrip(":").strip(), ""
            if not value:
                value = text_of(rest)
            label = label.strip().rstrip(":").strip()
            value = re.sub(r"\s+", " ", value).strip().rstrip(".")
            if label and value and len(label) < 40:
                pairs.append((label, value))
    return pairs


def text_pairs(markup: str, labels: list[str], name: str = "") -> list[tuple[str, str]]:
    """Fallback for pages that write labels as plain text with no markup.

    Some strains render Growth Information as an unbroken run of
    "Climate: Warm and Stable <description> Plant Structure: ..." with nothing
    to anchor on but the label words themselves. The value is the short phrase
    before the description starts, and descriptions reliably open with the
    strain name or a stock phrase, so cut there.
    """
    plain = text_of(strip_links(markup))
    alt = "|".join(sorted((re.escape(l) for l in labels), key=len, reverse=True))
    hits = [(m.start(), m.end(), m.group(1)) for m in re.finditer(rf"\b({alt})\s*:\s*", plain)]
    stop_re = re.compile(
        rf"\b(?:{re.escape(name)}|This strain|These buds|The buds|The plant|It )\b" if name
        else r"\b(?:This strain|These buds|The buds|The plant|It )\b")

    rows: list[tuple[str, str]] = []
    for i, (start, end, label) in enumerate(hits):
        limit = hits[i + 1][0] if i + 1 < len(hits) else len(plain)
        chunk = plain[end:limit].strip()
        cut = stop_re.search(chunk)
        value = (chunk[:cut.start()] if cut else chunk).strip(" .,;")
        if not value:
            value = chunk[:60].strip()
        if value:
            rows.append((label, re.sub(r"\s+", " ", value)[:120]))
    return rows


def label_pairs(markup: str, labels: list[str], name: str = "") -> list[dict]:
    """Keep the wanted labels, in page order, first occurrence only.

    Marked-up labels are preferred; the plain-text scan only fills gaps the
    markup pass did not already cover.
    """
    wanted = {l.lower().replace("&", "and"): l for l in labels}
    rows, seen = [], set()

    def take(pairs):
        for label, value in pairs:
            key = label.lower().replace("&", "and")
            if key in wanted and key not in seen:
                seen.add(key)
                rows.append({"label": label, "value": value})

    take(strong_pairs(markup))
    take(text_pairs(markup, labels, name))
    return rows


def extract_faqs(markup: str) -> list[dict]:
    """Question/answer pairs, however the accordion happens to be marked up."""
    plain_blocks = []
    for m in re.finditer(r"(?is)<(h[2-5]|summary|p|div)[^>]*>(.*?)</\1>", markup):
        t = text_of(m.group(2))
        if t:
            plain_blocks.append(t)

    faqs, i = [], 0
    while i < len(plain_blocks):
        block = plain_blocks[i]
        if block.endswith("?") and 8 < len(block) < 160:
            answer = ""
            for nxt in plain_blocks[i + 1:i + 4]:
                if nxt.endswith("?"):
                    break
                if len(nxt) > 30:
                    answer = nxt
                    break
            answer = strip_referrals(answer)
            if answer:
                faqs.append({"question": block, "answer": answer})
                i += 1
                continue
        i += 1

    seen, out = set(), []
    for f in faqs:
        if f["question"].lower() in seen:
            continue
        seen.add(f["question"].lower())
        out.append(f)
    return out[:12]


def extract_terpenes(markup: str) -> list[dict]:
    plain = text_of(strip_links(markup))
    rows = []
    others = "|".join(TERPENE_NAMES)
    for name in TERPENE_NAMES:
        # the blurb may be introduced by a colon, by a parenthetical nickname
        # ("Myrcene (The Relaxant) A dominant terpene ..."), or by nothing at all
        m = re.search(
            rf"\b{name}\b\s*(?:\([^)]{{0,48}}\))?\s*[:–—-]?\s*"
            rf"(.{{20,400}}?)(?=(?:\b(?:{others})\b\s*(?:\([^)]{{0,48}}\))?\s*[:–—-]?)|$)",
            plain, re.I)
        if m:
            body = re.sub(r"\s+", " ", m.group(1)).strip()
            body = strip_referrals(body).strip(" ()")
            if len(body) > 25:
                rows.append({"name": name, "type": "", "text": body})
    return rows[:5]


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def pct(value: str) -> str:
    m = re.search(r"(\d{1,2}(?:\.\d)?\s*[%–-]{0,3}\s*\d{0,2}(?:\.\d)?\s*%?)", value or "")
    return re.sub(r"\s+", "", m.group(1)).replace("-", "–") if m else (value or "").strip()


def lineage_from_prose(markup: str) -> str:
    """Recover genetics when the page never labels them.

    Plenty of pages skip the Lineage row and just say it: "bred from Red Pop and
    RS11", "a cross of Gelato x Runtz". Without this those strains lose their
    parentage entirely, which is one of the few hard facts the page carries.
    """
    plain = text_of(strip_links(markup))
    patterns = [
        r"\b(?:bred|built|created|made)\s+(?:from|by crossing)\s+([A-Z][\w'’.-]*(?:\s+[A-Z0-9][\w'’.-]*){0,3}\s*(?:x|×|and)\s*[A-Z][\w'’.-]*(?:\s+[A-Z0-9][\w'’.-]*){0,3})",
        r"\bcross(?:ing)?\s+(?:of|between)\s+([A-Z][\w'’.-]*(?:\s+[A-Z0-9][\w'’.-]*){0,3}\s*(?:x|×|and)\s*[A-Z][\w'’.-]*(?:\s+[A-Z0-9][\w'’.-]*){0,3})",
        r"\b([A-Z][\w'’.-]*(?:\s+[A-Z0-9][\w'’.-]*){0,2}\s*(?:x|×)\s*[A-Z][\w'’.-]*(?:\s+[A-Z0-9][\w'’.-]*){0,2})\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, plain)
        if m:
            value = re.sub(r"\s+", " ", m.group(1)).strip(" .,")
            value = re.sub(r"\s+and\s+", " × ", value)
            value = re.sub(r"\s*x\s*", " × ", value, flags=re.I)
            if 6 < len(value) < 70:
                return value
    return ""


def db_safe(value):
    """Encode astral-plane characters so the database can store them.

    Staging's tables are 3-byte `utf8`, so any 4-byte character — the emoji the
    live copy uses as flourishes — makes the meta write fail outright with
    "Could not update the meta value ... in database". Encoding them as numeric
    HTML entities keeps them ASCII on disk while still rendering as the original
    character on the page, so nothing is lost from the source copy.
    """
    if isinstance(value, str):
        return "".join(c if ord(c) <= 0xFFFF else f"&#x{ord(c):X};" for c in value)
    if isinstance(value, dict):
        return {k: db_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [db_safe(v) for v in value]
    return value


def build_meta(name: str, page_html: str) -> tuple[dict, list[str]]:
    """Return (meta, warnings) for one strain."""
    warnings: list[str] = []
    sections = split_sections(page_html)
    for key, _ in SECTION_PATTERNS:
        if key not in sections and key not in ("composition", "use", "why"):
            warnings.append(f"missing section: {key}")

    about_src = sections.get("about", "")
    comp_src = sections.get("composition", "")
    about_html = clean_block(about_src + "\n" + comp_src)

    glance = label_pairs(about_src + " " + comp_src, GLANCE_LABELS, name)
    thc = next((r["value"] for r in glance if r["label"] == "THC Content"), "")
    cbd = next((r["value"] for r in glance if r["label"] == "CBD Content"), "")
    lineage = next((r["value"] for r in glance if r["label"] in ("Lineage", "Genetics")), "")
    if not lineage:
        lineage = lineage_from_prose(about_src)
        if lineage:
            warnings.append("lineage recovered from prose")

    body_text = text_of(page_html)
    if re.search(r"\b50/50 hybrid|balanced hybrid\b", body_text, re.I):
        stype = "Hybrid"
    elif re.search(r"\bindica[- ]dominant|strong indica|indica strain\b", body_text, re.I):
        stype = "Indica"
    elif re.search(r"\bsativa[- ]dominant|sativa strain\b", body_text, re.I):
        stype = "Sativa"
    else:
        stype = "Hybrid"
        warnings.append("strain_type defaulted to Hybrid")

    meta: dict = {
        "strain_type": stype,
        "hero_title": f"{name} Strain",
        "buy_kick": f"Flower · {stype}",
        "hero_lede": first_sentence(about_src),
        "thc": pct(thc),
        "cbd": pct(cbd),
        "lineage": lineage,
        "timing": "Evening / nighttime" if stype == "Indica" else "Any time of day",
        "otd_note": "Out-the-door · tax included",
        "buy_buttons": {
            "item-0": {"style": "solid", "label": "Order for delivery", "url": SHOP_URL},
            "item-1": {"style": "ghost", "label": "Reserve for pickup", "url": SHOP_URL},
        },
        "trust_items": {
            "item-0": {"icon": "fas fa-shield-alt", "text": "Lab-tested"},
            "item-1": {"icon": "fas fa-bolt", "text": "Same-day delivery"},
            "item-2": {"icon": "fas fa-circle", "text": "Open 9AM–10PM"},
        },
        "about_headline": first_sentence(about_src),
        "about_html": about_html,
        "glance": {f"item-{i}": r for i, r in enumerate(glance)},
        "effects_headline": f"What {name} actually feels like.",
        "effects_html": clean_block(sections.get("effects", "")),
        "flavor_headline": f"How {name} tastes and smells.",
        "flavor_html": clean_block(sections.get("flavor", "")),
        "jar_headline": "What to look for in the jar.",
        "jar_html": clean_block(sections.get("jar", "")),
        "cultivation_headline": f"Growing {name}.",
        "cultivation_html": clean_block(sections.get("cultivation", "")),
        "use_headline": "Ways to enjoy it.",
        "use_html": clean_block(sections.get("use", "")),
        "use_methods": {
            "item-0": {"label": "Flower",
                       "text": "Smoking the flower gives the fastest onset and the fullest "
                               "expression of the terpene profile."},
            "item-1": {"label": "Vaporizer",
                       "text": "Vaping at lower temperatures preserves the lighter terpenes, "
                               "giving cleaner flavour with less harshness."},
            "item-2": {"label": "Concentrates",
                       "text": "Trichome-heavy flower makes a strong candidate for solventless "
                               "extracts like rosin and bubble hash."},
            "item-3": {"label": "Edibles",
                       "text": "Edibles and concentrates produce longer-lasting effects — start "
                               "low, as onset is slower and potency builds."},
        },
        "steps_headline": "Three steps to<br>your door.",
        "steps_items": {
            "item-0": {"title": "Check the live menu",
                       "text": f"{name} rotates through the flower shelf. Check our live menu for "
                               "today's stock, or browse every strain we carry to plan a backup."},
            "item-1": {"title": "Order delivery or pickup",
                       "text": "Same-day delivery across Santa Ana and Orange County, or reserve "
                               "for pickup at 1320 E Edinger Ave. Every price is out-the-door."},
            "item-2": {"title": "Show your ID",
                       "text": "Have a valid government photo ID showing 21+. The driver verifies "
                               "at your door; for pickup, we check at the counter. That's it."},
        },
        "related_headline": f"If you like {name}…",
        "faq_headline": f"{name}, answered.",
        "cta_kick": "Open until 10PM · Delivering now",
        "cta_headline": f"Try {name}<br>today.",
        "cta_buttons": {
            "item-0": {"style": "solid", "label": "Order for delivery", "url": SHOP_URL},
            "item-1": {"style": "ghost", "label": "Browse all strains", "url": STRAIN_HUB_URL},
        },
        "cta_license": "⬡ Licensed CA Dispensary · 1320 E Edinger Ave · Santa Ana, CA 92705 · 21+",
    }

    terps = extract_terpenes(sections.get("flavor", "") + " " + comp_src)
    meta["terps"] = {f"item-{i}": t for i, t in enumerate(terps)}

    grow = label_pairs(sections.get("cultivation", ""), GROW_LABELS, name)
    meta["grow_specs"] = {f"item-{i}": r for i, r in enumerate(grow[:8])}

    faqs = extract_faqs(sections.get("faq", ""))
    meta["faqs"] = {f"item-{i}": f for i, f in enumerate(faqs)}

    # the live pages describe bud appearance under Growth Information rather
    # than in the appearance section, so look in both
    spec = label_pairs(sections.get("jar", "") + " " + sections.get("cultivation", ""),
                       ["Bud Structure", "Coloration", "Trichome Coverage",
                        "Aroma", "Plant Structure"], name)
    meta["spec"] = {f"item-{i}": r for i, r in enumerate(spec[:4])}

    # the Key Features block already lists the effects as a written phrase
    # ("Euphoric, tingly, deeply relaxing"), which beats guessing at adjectives
    effects_value = next((r["value"] for r in glance
                          if r["label"] in ("Effects", "Primary Effects")), "")
    candidates = [p.strip() for p in re.split(r",|/|\band\b", effects_value) if p.strip()]
    if not candidates:
        candidates = [w.capitalize() for w in re.findall(
            r"\b(euphoric|relaxing|uplifting|creative|focused|sleepy|tingly|calming|"
            r"energetic|happy|giggly|talkative|sedating)\b",
            text_of(sections.get("effects", "")), re.I)]
        warnings.append("pills derived from prose, not Key Features")
    pills, seen = [], set()
    for c in candidates:
        label = c[:1].upper() + c[1:]
        if label.lower() not in seen and 2 < len(label) < 28:
            seen.add(label.lower())
            pills.append({"label": label})
    meta["pills"] = {f"item-{i}": p for i, p in enumerate(pills[:6])}

    if not meta["about_html"]:
        warnings.append("about_html empty")
    if not faqs:
        warnings.append("no FAQs found")
    if not glance:
        warnings.append("no at-a-glance rows found")

    return db_safe(meta), warnings


def load_pages() -> dict:
    return json.load(open(PROD_PAGES, encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pages = load_pages()
    if args.slug not in pages:
        raise SystemExit(f"no production page cached for '{args.slug}'")
    page = pages[args.slug]
    name = htmllib.unescape(re.sub(r"(?is)<[^>]+>", "", (page.get("title") or {}).get("rendered", "")))
    meta, warnings = build_meta(name.strip(), (page.get("content") or {}).get("rendered", ""))

    if args.json:
        print(json.dumps(meta, indent=1, ensure_ascii=False))
        return 0

    print(f"=== {args.slug} ({name}) ===")
    for k, v in meta.items():
        s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        print(f"  {k:22} {len(s):>6}  {s[:70]}")
    print("\nwarnings:", warnings or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
