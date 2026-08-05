#!/usr/bin/env python3
"""Migrate the live Alien OG copy into the staging `strain` post type.

Source : https://evergreenoc.com/strain/alien-og/  (3,297 words of body copy)
Target : https://staging2.evergreenoc.com/  strain #14169

The point of the migration is to keep the ranking copy intact, so the prose is
carried across close to verbatim. Two things are deliberately changed:

1. Outbound links are removed. The live page links out 27 times — 13 of them to
   Weedmaps (including the primary "Order Online" and "SHOP NOW" buttons), the
   rest to Leafly, AllBud, CannaConnection, Hytiva, Project CBD, Cali
   Connection, Yelp and Wikipedia. Anchors are unwrapped rather than deleted,
   so the sentence and its keywords survive; ordering CTAs now point at the
   internal /shop/ menu.

2. Placeholder copy left over from the Apple Jack build is replaced. The
   `steps_items` repeater still described Apple Jack and told visitors to check
   the Weedmaps menu.

Run:  python3 tools/strain_alien_og.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp  # noqa: E402

POST_ID = 14169
SHOP_URL = "https://staging2.evergreenoc.com/shop/"
STRAIN_HUB_URL = "https://staging2.evergreenoc.com/strain-hub/"


def rep(items: list[dict]) -> dict:
    """JetEngine stores repeaters as {"item-0": {...}, "item-1": {...}}."""
    return {f"item-{i}": v for i, v in enumerate(items)}


def normalize_headings(markup: str) -> str:
    """Keep in-content subheadings at the correct level for this template.

    The strain template already emits the page's only `h1` (the hero title) and
    an `h2` for each section headline. Anything inside a section's rich text
    sits a level below that, so subheadings are pinned to `h3` and nested ones
    to `h4`. That keeps a single-h1 outline instead of competing with the
    template's own headings.

    Colour for these — and for list copy — comes from the "Prose headings +
    lists (strain sections)" Elementor code snippet, which extends
    `.eg-prose-cream` / `.eg-prose-dark`. Those classes originally styled only
    `p` and `strong`, which is why headings and lists first rendered as
    unreadable greys.
    """
    def demote(m):
        level = int(m.group(1)[1])
        new = "h3" if level <= 3 else "h4"
        return "<%s>%s</%s>" % (new, m.group(2).strip(), new)

    out = re.sub(r'(?is)<(h[1-6])[^>]*>(.*?)</\1>', demote, markup)
    return re.sub(r'\n{3,}', '\n\n', out).strip()


# ---------------------------------------------------------------------------
# Buy Hero
# ---------------------------------------------------------------------------

BUY_HERO = {
    # live copy calls this "a balanced 50/50 hybrid"; the draft had it as Indica
    "strain_type": "Hybrid",
    "hero_title": "Alien OG Strain",
    "buy_kick": "Flower · Balanced Hybrid",
    "hero_lede": (
        "A powerful 50/50 hybrid of Tahoe OG and Alien Kush, with THC that often "
        "runs 22–28%. Expect a psychedelic cerebral buzz over a deep body high — "
        "an out-of-this-world experience built for experienced users."
    ),
    "thc": "22–28%",
    "cbd": "0–1%",
    "lineage": "Tahoe OG × Alien Kush",
    "timing": "Evening / nighttime",
    "buy_buttons": rep([
        {"style": "solid", "label": "Order for delivery", "url": SHOP_URL},
        {"style": "ghost", "label": "Reserve for pickup", "url": SHOP_URL},
    ]),
    "trust_items": rep([
        {"icon": "fas fa-shield-alt", "text": "Lab-tested"},
        {"icon": "fas fa-bolt", "text": "Same-day delivery"},
        {"icon": "fas fa-circle", "text": "Open 9AM–10PM"},
    ]),
}

# ---------------------------------------------------------------------------
# About  (live sections 1 + 2)
# ---------------------------------------------------------------------------

ABOUT = {
    "about_headline": (
        "Alien OG is a powerful hybrid cannabis strain that blends the potent "
        "genetics of Tahoe OG and Alien Kush."
    ),
    "about_html": """
<p>Alien OG is a powerful hybrid cannabis strain that blends the potent genetics of Tahoe OG and Alien Kush, resulting in a balanced 50/50 hybrid with soaring THC levels that often range between 22% and 28%. Known for its psychedelic cerebral buzz paired with a deep body high, Alien OG is ideal for experienced users seeking a strain that delivers both mental stimulation and physical relaxation.</p>

<p>First introduced as a clone-only strain in California&rsquo;s Bay Area and later made available in seed form by Cali Connection, Alien OG quickly earned its reputation as one of the most potent OG hybrids in the cannabis world. Its signature lemon-pine aroma and frosty trichome-covered buds are loved by connoisseurs and medical users alike.</p>

<p>Alien OG&rsquo;s high begins with a euphoric cerebral lift that clears away stress and negative thoughts. This is followed by a tingling full-body calm that&rsquo;s perfect for unwinding after a long day. Whether you&rsquo;re lounging on a weekend or looking to shut off the noise of a stressful week, Alien OG delivers an &ldquo;out-of-this-world&rdquo; experience that lives up to its name.</p>

<h3>Why Is Alien OG a Popular Choice?</h3>
<p>Alien OG has achieved cult-like status for its combination of potency, flavor, and reliable effects:</p>
<ul>
<li><strong>High Potency for Seasoned Users:</strong> With THC often hitting 28%, Alien OG is not for the faint of heart &mdash; it&rsquo;s a go-to for experienced users or medical patients who need serious relief.</li>
<li><strong>Classic OG Flavor Profile:</strong> Expect citrusy lemon, earthy pine, and a skunky backbone that&rsquo;s unmistakably OG. This terpene-rich strain offers not just potency, but depth of flavor.</li>
<li><strong>Dual-Action Effects:</strong> Alien OG strikes a unique balance between uplifting mental energy and soothing physical sedation, offering a versatile high.</li>
<li><strong>Medical Benefits Without Heavy Sedation:</strong> Perfect for those managing chronic pain, stress, or fatigue, Alien OG helps relax the body while keeping the mind elevated.</li>
<li><strong>Widely Respected Genetics:</strong> Alien OG&rsquo;s lineage from Alien Kush and Tahoe OG places it among some of the most respected family trees in cannabis, similar to other West Coast staples like Original SFV OG.</li>
</ul>

<h3>Alien OG Strain Composition Breakdown</h3>
<p>Alien OG stands out for its potent cannabinoid profile and rich concentration of therapeutic terpenes, working together to create a deeply immersive and long-lasting experience. Whether you&rsquo;re seeking intense relaxation, stress relief, or mood elevation, Alien OG&rsquo;s chemical makeup supports both recreational and medical use through a phenomenon known as the entourage effect &mdash; where cannabinoids and terpenes interact synergistically to enhance the overall effect.</p>
<ul>
<li><strong>THC Content: 22%&ndash;28%.</strong> Alien OG is a high-THC strain, ideal for users with moderate to high tolerance. Its elevated THC levels contribute to a euphoric mental uplift followed by a deeply relaxing full-body experience.</li>
<li><strong>CBD Content: ~0&ndash;1%.</strong> With very low CBD levels, Alien OG focuses entirely on delivering THC-driven effects. It&rsquo;s better suited for users seeking stress relief, mood elevation, and evening-time relaxation over non-intoxicating wellness use.</li>
<li><strong>CBG Content: ~0.5&ndash;1%.</strong> Present in trace amounts, cannabigerol (CBG) adds subtle therapeutic benefits including anti-inflammatory and mood-regulating effects, enhancing Alien OG&rsquo;s relaxing nature.</li>
<li><strong>CBN Content: Trace.</strong> Cannabinol (CBN) appears in minimal levels and may slightly increase the strain&rsquo;s sedative effects &mdash; particularly beneficial for muscle relaxation or mild sleep support.</li>
</ul>

<p><strong>Entourage Effect.</strong> Alien OG is a textbook example of the &ldquo;entourage effect,&rdquo; where its potent combination of cannabinoids and terpenes work together to enhance both therapeutic and recreational benefits. The synergy between THC and myrcene delivers fast-acting, full-body relaxation with calming, almost sedative qualities. Limonene adds an uplifting cerebral spark, promoting mood elevation and helping to reduce anxiety. Meanwhile, caryophyllene&rsquo;s direct interaction with CB2 receptors supports stress relief and anti-inflammatory effects, making Alien OG a well-rounded option for deep relaxation without mental fog.</p>
""".strip(),
    "glance": rep([
        {"label": "THC Content", "value": "22–28%"},
        {"label": "CBD Content", "value": "~0–1%"},
        {"label": "Lineage", "value": "Tahoe OG × Alien Kush"},
        {"label": "Flavor & Aroma", "value": "Lemon, pine, earthy, slightly sweet"},
        {"label": "Effects", "value": "Euphoric, tingly, deeply relaxing"},
        {"label": "Best For", "value": "Chronic pain, stress, fatigue, anxiety"},
    ]),
}

# ---------------------------------------------------------------------------
# Effects  (live section 3)
# ---------------------------------------------------------------------------

EFFECTS = {
    "effects_headline": "Euphoria first, then a full-body calm that settles in for hours.",
    "effects_html": """
<p>Alien OG is well-regarded for delivering a powerful blend of euphoria and relaxation, offering both cerebral stimulation and full-body calm. Users commonly report an immediate head rush that uplifts mood and clears the mind, followed by a tingling body sensation that promotes deep physical ease. At higher doses, some may experience mildly psychedelic effects, making this strain ideal for introspection, meditation, or creative downtime. Because of its potent nature, Alien OG is often reserved for evening or nighttime use, especially for those looking to unwind or manage pain after a long day.</p>

<h3>Mental and Physical Relief</h3>
<p>Alien OG&rsquo;s rich cannabinoid and terpene profile makes it effective for both mental and physical wellness. On the mental health side, it has been reported to help reduce anxiety, manage chronic stress, and elevate mood &mdash; making it a potential option for individuals dealing with mild to moderate depression.</p>
<p>Physically, Alien OG excels at relieving chronic pain, muscle tension, and general fatigue. Its strong indica influence may also support appetite stimulation and reduce nausea, offering broad appeal for medical cannabis users. These therapeutic effects stem from the synergistic interplay of THC and its dominant terpenes like myrcene and caryophyllene.</p>

<h3>Medical Use Cases</h3>
<p>Thanks to its potency and therapeutic versatility, Alien OG is commonly used by patients to help manage:</p>
<ul>
<li>Stress-related conditions</li>
<li>Anxiety and PTSD</li>
<li>Muscle spasms and migraines</li>
<li>Mild insomnia (particularly when struggling to fall asleep)</li>
<li>Chronic pain conditions, including arthritis and fibromyalgia</li>
</ul>

<h3>Side Effects and Usage Tips</h3>
<p>Like many high-THC strains, Alien OG may produce side effects such as dry mouth, dry eyes, or dizziness, particularly when consumed in large amounts. In some cases, users may experience mild paranoia &mdash; a common issue with potent strains high in THC. To minimize discomfort, it&rsquo;s recommended to start with a low dose, especially for new or low-tolerance users. Always stay hydrated and consume in a comfortable, familiar setting.</p>
""".strip(),
    "pills": rep([
        {"label": "Euphoric"},
        {"label": "Tingly"},
        {"label": "Deeply relaxing"},
        {"label": "Mildly psychedelic"},
        {"label": "Pain relief"},
        {"label": "Stress relief"},
    ]),
}

# ---------------------------------------------------------------------------
# Flavor  (live section 4)
# ---------------------------------------------------------------------------

FLAVOR = {
    "flavor_headline": "Lemon zest on the inhale, pine and earth on the way out.",
    "flavor_html": """
<p>Alien OG offers a bold, layered flavor and aroma profile that reflects its rich OG Kush heritage and terpene-heavy composition. From the moment you open the jar to the last exhale, Alien OG is a sensory experience that balances pungency with sweetness, ideal for connoisseurs and casual users alike.</p>

<h3>Flavor Profile</h3>
<p>On the inhale, Alien OG delivers a sweet burst of citrus &mdash; most notably lemon zest &mdash; followed by a woody, pine-forward finish. As the smoke or vapor settles, subtle earthy undertones emerge, grounding the flavor and giving it a classic OG structure. This balance of sweet, sour, and herbal notes makes Alien OG both flavorful and complex.</p>

<h3>Aroma Profile</h3>
<p>Alien OG&rsquo;s aromatic intensity is immediately noticeable. Cracking open a nug releases a rush of sharp citrus backed by pine and fresh herbs. As the flower breaks down further, a skunky and slightly diesel-like aroma becomes more pronounced &mdash; a signature trait of high-quality OG strains. This pungent bouquet can fill a room quickly, so it&rsquo;s worth noting for users seeking discretion.</p>

<p>Together, these terpenes not only create Alien OG&rsquo;s signature lemon-pine funk, but also support the overall effects users love: mental clarity, mood stabilization, and deep relaxation.</p>
""".strip(),
    "terps": rep([
        {
            "name": "Myrcene",
            "type": "Earthy / herbal",
            "text": (
                "The most dominant terpene in Alien OG. Myrcene contributes to its calming and "
                "sedative effects, and is known for enhancing the impact of THC through increased "
                "cell permeability — helping deliver fast-acting, full-body relaxation."
            ),
        },
        {
            "name": "Limonene",
            "type": "Citrus / lemon zest",
            "text": (
                "Responsible for Alien OG's sharp citrus and lemon-zest aroma. It brings "
                "mood-enhancing and anxiety-reducing effects, offering a bright mental clarity "
                "that complements the strain's otherwise relaxing nature."
            ),
        },
        {
            "name": "Caryophyllene",
            "type": "Peppery / spice",
            "text": (
                "This spicy, peppery terpene is unique for its interaction with the body's CB2 "
                "receptors, making it especially effective for stress relief and anti-inflammatory "
                "benefits. It deepens the strain's therapeutic potential and rounds out its OG "
                "flavor profile."
            ),
        },
    ]),
}

# ---------------------------------------------------------------------------
# Cultivation  (live section 5 — new section, 678 words preserved)
# ---------------------------------------------------------------------------

CULTIVATION = {
    "cultivation_headline": "Moderate difficulty, dense buds, and a real sensitivity to humidity.",
    "cultivation_html": """
<p>Growing Alien OG can be a rewarding experience for cultivators seeking a high-THC, terpene-rich hybrid. While not overly difficult, Alien OG is best suited for those with some prior experience due to its dense buds and climate-sensitive structure. Originally a clone-only strain, Alien OG is now widely available in seed form from breeders like Cali Connection, making it accessible for both indoor and outdoor growers.</p>

<h3>Growing Techniques</h3>
<p>Alien OG responds well to Low-Stress Training (LST) and Screen of Green (ScrOG) methods. These techniques help control canopy height, improve light penetration, and increase overall bud production. Regular pruning and low-stress training improve airflow and maximize light distribution for optimal yields.</p>

<h3>Indoor and Outdoor Setup</h3>
<p><strong>Indoor:</strong> Use dehumidifiers and fans to maintain optimal airflow and keep relative humidity below 50% during flowering. Proper ventilation helps prevent mold, especially around Alien OG&rsquo;s dense, resin-heavy buds. Maintain temperatures between 68&ndash;80&deg;F.</p>
<p><strong>Outdoor:</strong> Choose a location with full sun exposure and minimal risk of rain in late flowering. Protective coverings or raised beds can improve drainage and shield plants from seasonal moisture.</p>

<h3>Medium, Nutrients and Pest Control</h3>
<p><strong>Growing medium:</strong> Use organic soil to enhance terpene richness and flavor, or choose hydroponics for faster growth and higher yields. Both methods can be successful depending on your cultivation goals and setup.</p>
<p><strong>Nutrient balance:</strong> Use bloom-stage nutrients high in phosphorus and potassium to support bud density and resin development. Avoid nitrogen-heavy feeds during late flowering to prevent leafy growth and muted flavors.</p>
<p><strong>Pest control:</strong> Regularly inspect plants for common pests like spider mites and aphids. Use organic treatments such as neem oil or insecticidal soap, or introduce beneficial insects like ladybugs for natural pest control.</p>

<h3>Temperature and Humidity</h3>
<p>Lowering nighttime temperatures to 55&ndash;65&deg;F during the final weeks of flowering can enhance trichome production and bring out subtle purple hues, boosting both potency and visual appeal. Alien OG&rsquo;s dense buds are prone to mold and mildew, so maintain humidity below 50% during flowering and use oscillating fans or exhaust systems to ensure adequate airflow throughout the canopy.</p>
""".strip(),
    "grow_specs": rep([
        {"label": "Difficulty", "value": "Moderate"},
        {"label": "Climate", "value": "Warm, dry, low humidity"},
        {"label": "Plant Structure", "value": "Medium height, dense trichome-rich buds"},
        {"label": "Flowering Time", "value": "9–10 weeks"},
        {"label": "Indoor Yield", "value": "≈400–450g/m²"},
        {"label": "Outdoor Harvest", "value": "Late October"},
        {"label": "Techniques", "value": "LST and ScrOG"},
        {"label": "Growing Medium", "value": "Organic soil or hydroponics"},
    ]),
}

# ---------------------------------------------------------------------------
# How to Use  (live section 6 — new section)
# ---------------------------------------------------------------------------

HOW_TO_USE = {
    "use_headline": "One strain, several ways to enjoy it.",
    "use_html": (
        "<p>Alien OG&rsquo;s high potency and rich terpene profile make it suitable for multiple "
        "consumption methods, each offering a unique experience. Whether you&rsquo;re looking for "
        "fast relief, flavor, or long-lasting effects, this strain delivers.</p>"
    ),
    "use_methods": rep([
        {"label": "Flower", "text": "Smoking the flower delivers the fastest onset and the fullest expression of the lemon-pine terpene profile."},
        {"label": "Vaporizer", "text": "Vaping at lower temperatures preserves limonene and myrcene, giving a cleaner flavor with less harshness."},
        {"label": "Concentrates", "text": "Alien OG's heavy trichome coverage makes it a strong candidate for solventless extracts like rosin and bubble hash."},
        {"label": "Edibles", "text": "Edibles and concentrates produce longer-lasting effects — start low, as onset is slower and potency builds."},
    ]),
}

# ---------------------------------------------------------------------------
# In the Jar  (live section 7)
# ---------------------------------------------------------------------------

JAR = {
    "jar_headline": "Dense, grape-shaped nugs under a thick coat of frost.",
    "jar_html": """
<p>Alien OG is visually striking and instantly recognizable for its dense, compact bud structure, often described as grape-shaped with a thick, resinous texture. These tightly formed nugs are heavily coated in trichomes &mdash; the crystal-like glands responsible for producing the plant&rsquo;s cannabinoids and terpenes. This trichome density not only indicates high potency but also makes Alien OG a top choice for concentrate extraction.</p>

<p>The coloration of Alien OG adds to its appeal, with hues that range from bright mint green to deep olive, depending on phenotype and environmental conditions. The buds are accented by vivid orange pistils, which wind through the flower and stand out against the shimmering backdrop of amber and milky-white trichomes. As the plant reaches peak maturity &mdash; typically near the end of its 9&ndash;10 week flowering cycle &mdash; these trichomes become more prominent, signaling optimal cannabinoid and terpene production.</p>

<p>This frosty resin coating does more than enhance bag appeal. It plays a key role in Alien OG&rsquo;s psychoactive strength and extractability, especially for users interested in producing solventless concentrates like rosin or bubble hash.</p>

<p>From a cultivator&rsquo;s perspective, Alien OG&rsquo;s visual cues &mdash; such as trichome coverage, pistil color, and bud shape &mdash; are critical indicators of harvest readiness. Under natural light or magnification, these features reflect the strain&rsquo;s premium genetics and quality-focused cultivation potential. Whether you&rsquo;re a casual user or a seasoned grower, Alien OG&rsquo;s appearance sets clear expectations: potency, flavor, and high extract value.</p>
""".strip(),
    "spec": rep([
        {"label": "Bud Structure", "value": "Dense, grape-shaped, resin-coated"},
        {"label": "Coloration", "value": "Mint to olive green with orange pistils"},
        {"label": "Trichome Coverage", "value": "Thick and frosty"},
        {"label": "Best Use", "value": "Flower or solventless extraction"},
    ]),
}

# ---------------------------------------------------------------------------
# Order Steps — replaces the leftover Apple Jack / Weedmaps copy
# ---------------------------------------------------------------------------

STEPS = {
    "steps_headline": "Three steps to<br>your door.",
    "steps_items": rep([
        {
            "title": "Check the live menu",
            "text": "Alien OG rotates through the flower shelf. Check our live menu for today's stock, or browse every strain we carry to plan a backup.",
        },
        {
            "title": "Order delivery or pickup",
            "text": "Same-day delivery across Santa Ana and Orange County, or reserve for pickup at 1320 E Edinger Ave. Every price is out-the-door.",
        },
        {
            "title": "Show your ID",
            "text": "Have a valid government photo ID showing 21+. The driver verifies at your door; for pickup, we check at the counter. That's it.",
        },
    ]),
}

# ---------------------------------------------------------------------------
# Related / FAQ / CTA
# ---------------------------------------------------------------------------

RELATED = {"related_headline": "If you like Alien OG…"}

FAQ = {
    "faq_headline": "Alien OG, answered.",
    "faqs": rep([
        {"question": "What are the effects of Alien OG?",
         "answer": "Alien OG delivers a balanced experience, starting with an uplifting cerebral buzz followed by deep body relaxation. It's often described as euphoric, calming, and mildly psychedelic at higher doses."},
        {"question": "Is Alien OG an indica or sativa?",
         "answer": "Alien OG is a 50/50 hybrid, but its effects lean slightly toward the indica side due to its strong body high and relaxing properties."},
        {"question": "What does Alien OG taste and smell like?",
         "answer": "Alien OG has a lemon-pine flavor with earthy undertones. Its aroma is sharp and citrusy, with hints of skunk and fresh herbs — true to its OG Kush lineage."},
        {"question": "How strong is Alien OG?",
         "answer": "Alien OG is considered a high-THC strain, typically ranging from 22% to 28%. It's best suited for users with moderate to high tolerance or those seeking potent therapeutic effects."},
        {"question": "What medical conditions can Alien OG help with?",
         "answer": "Many medical users turn to Alien OG for relief from stress, anxiety, chronic pain, muscle tension, insomnia, and PTSD. Its calming effects can also help with appetite stimulation and nausea."},
        {"question": "How long do Alien OG effects last?",
         "answer": "The effects of Alien OG typically last 2 to 3 hours, depending on the dose and method of consumption. Edibles and concentrates may produce longer-lasting effects."},
        {"question": "Can Alien OG cause side effects?",
         "answer": "Yes. Common side effects include dry mouth, dry eyes, and, in some cases, paranoia or dizziness — especially at higher doses. Start with a low dose to avoid discomfort."},
        {"question": "Is Alien OG good for sleep?",
         "answer": "While not a heavy sedative, Alien OG's body-relaxing effects make it helpful for winding down before bed, especially for those with mild insomnia or evening stress."},
        {"question": "Is Alien OG suitable for beginners?",
         "answer": "Due to its high potency, Alien OG is generally better for intermediate to experienced users. Beginners should start with small doses and monitor effects closely."},
    ]),
}

CTA = {
    "cta_kick": "Open until 10PM · Delivering now",
    "cta_headline": "Try Alien OG<br>today.",
    "cta_buttons": rep([
        {"style": "solid", "label": "Order for delivery", "url": SHOP_URL},
        {"style": "ghost", "label": "Browse all strains", "url": STRAIN_HUB_URL},
    ]),
    "cta_license": "⬡ Licensed CA Dispensary · 1320 E Edinger Ave · Santa Ana, CA 92705 · 21+",
}

# SEOPress — the live page ranks under this title; the draft had a weaker one.
SEO = {
    "_seopress_titles_title": "Alien OG Effects: Euphoria, Relaxation & Relief",
    "_seopress_titles_desc": (
        "Alien OG is a 50/50 hybrid of Tahoe OG and Alien Kush with 22–28% THC. "
        "Explore its effects, lemon-pine flavor, terpenes and grow tips — "
        "available for same-day delivery in Santa Ana."
    ),
}


def build() -> dict:
    meta: dict = {}
    for block in (BUY_HERO, ABOUT, EFFECTS, FLAVOR, CULTIVATION,
                  HOW_TO_USE, JAR, STEPS, RELATED, FAQ, CTA, SEO):
        meta.update(block)
    # pin in-content subheadings below the template's own h1/h2
    for key in [k for k in meta if k.endswith("_html")]:
        meta[key] = normalize_headings(meta[key])
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    meta = build()
    print(f"fields to write: {len(meta)}")
    for k, v in meta.items():
        s = v if isinstance(v, str) else json.dumps(v)
        print(f"  {k:22} {len(s):>6} chars")

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    wp.request("POST", f"/wp/v2/strain/{POST_ID}", data={"meta": meta})
    print(f"\nwrote {len(meta)} fields to strain/{POST_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
