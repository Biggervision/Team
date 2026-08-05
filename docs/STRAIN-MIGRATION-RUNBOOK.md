# Strain migration runbook

How to move a live strain page from `evergreenoc.com` into the new JetEngine
strain template on `staging2.evergreenoc.com` without losing keywords.

Written from the Alien OG migration (strain `14169`). 95 strains remain.

---

## Part 0 — One-time setup (already done, do not repeat)

Three things were changed once and apply to every strain from here on. They are
recorded so nobody redoes or accidentally reverts them.

| What | Where | Why |
|---|---|---|
| `show_in_rest: true` on all strain fields | Strain post type, id `2` | Fields were invisible to the REST API — `meta` came back `null` and `POST /wp/v2/strain` rejected a meta payload. Nothing could be written programmatically until this was set. |
| Cultivation + How to Use sections added | Strain post type, id `2` | The template had no home for two live sections, the larger being 678 words of grow-side keywords. Tabs sit after Flavor so field order follows the live page. |
| "Prose headings + lists (strain sections)" | Elementor snippet `14574` | `.eg-prose-cream` / `.eg-prose-dark` styled only `p` and `strong`, so `h3`, `ul` and `li` fell through to defaults that vanish against one background or the other. |

Scripts: `tools/strain_cpt_enable_rest.py`, and the snippet body is in the
commit history. Pre-change backups are in `docs/strain-migration/`.

**JetEngine gotcha:** `show_in_rest` is not in JetEngine's field schema and does
not appear in the UI, but JetEngine honours the key when present. It was tested
on one field before rolling out to all 40. If a *new* field is ever added to the
strain post type, it will not be REST-writable until this key is set on it.

---

## Part 1 — Per-strain process

### 1. Fetch the live page

Production sits behind SiteGround bot protection that answers roughly half of
burst requests with a captcha (HTTP 202) instead of HTML. It clears on retry, so
loop rather than failing:

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
for i in $(seq 1 15); do
  curl -s -m 30 -A "$UA" -L "https://evergreenoc.com/strain/<slug>/" -o /tmp/<slug>.html
  [ "$(stat -c%s /tmp/<slug>.html)" -gt 50000 ] && break
  sleep 1
done
```

A short page (a few hundred bytes) means the captcha, not a missing page.
`tools/wp.py` already handles this automatically for API calls.

### 2. Find the staging post

```bash
python3 tools/wp.py raw GET "/wp/v2/strain?search=<name>&status=any&_fields=id,slug,status"
```

96 strains exist in the CPT; most are drafts. Match on slug, not title.

### 3. Back up before touching anything

```bash
python3 tools/wp.py get strain <id> > docs/strain-migration/<slug>-<id>-before.json
```

### 4. Extract and map the copy

Pull headings, paragraphs and list items in document order, then map live
sections to fields:

| Live section | Fields |
|---|---|
| What Is *X*? | `about_headline`, `about_html` |
| Strain Composition Breakdown | `about_html` (continues), `glance` repeater |
| Effects and Benefits | `effects_headline`, `effects_html`, `pills` |
| Flavor and Aroma | `flavor_headline`, `flavor_html`, `terps` |
| Cultivation Tips | `cultivation_headline`, `cultivation_html`, `grow_specs` |
| How to Use | `use_headline`, `use_html`, `use_methods` |
| Physical Appearance | `jar_headline`, `jar_html`, `spec` |
| FAQs | `faq_headline`, `faqs` |
| Why Choose Us | CTA fields |

Hero facts (`thc`, `cbd`, `lineage`, `strain_type`, `timing`) come from the live
Key Features block. `strain_type` only accepts `Sativa`, `Indica` or `Hybrid`.

### 5. Apply the content rules

These are the rules that took several passes to get right on Alien OG. Follow
them and the page renders correctly first time.

**Strip every outbound link.** Alien OG had 27 — 13 to Weedmaps including the
primary ordering buttons, the rest to Leafly, AllBud, CannaConnection, Hytiva,
Project CBD, Cali Connection, Yelp and Wikipedia. Unwrap the anchor, keep the
sentence: the link text is usually mid-sentence and carries keywords. Ordering
CTAs point at `/shop/`, secondary CTAs at `/strain-hub/`.

**Headings are `h3`.** The template emits the page's only `h1` (hero) and an
`h2` per section headline, so in-content subheadings sit one level below.
`normalize_headings()` in `tools/strain_alien_og.py` enforces this — never emit
`h1` or `h2` from a field.

**Repeaters are keyed objects,** not arrays: `{"item-0": {...}, "item-1": {...}}`.
Use the `rep()` helper.

**Check for placeholder copy from the reference build.** The Alien OG draft still
carried Apple Jack text in `steps_items` telling visitors to check the Weedmaps
menu. Grep every field for the wrong strain name before writing.

**Carry the production SEO title over.** Drafts default to `<Name> - Evergreen`,
which is weaker than the title production actually ranks under. Set
`_seopress_titles_title` and `_seopress_titles_desc`.

### 6. Write

Copy `tools/strain_alien_og.py`, swap `POST_ID` and the content blocks, then:

```bash
python3 tools/strain_<slug>.py --dry-run   # field list + sizes
python3 tools/strain_<slug>.py
```

If the write fails on rate limiting, retry — the challenge is served at the edge
and never reaches WordPress, so no partial write can have occurred:

```bash
for a in 1 2 3 4; do
  python3 tools/strain_<slug>.py 2>&1 | tail -2 | grep -q "wrote" && break
  sleep 20
done
```

### 7. Verify before previewing

```python
import sys, re, json
sys.path.insert(0, 'tools'); import wp
m = wp.request("GET", "/wp/v2/strain/<id>?context=edit")[0]["meta"]
blob = json.dumps(m)

ext = [u for u in set(re.findall(r'https?://[^\s"\'<>\\]+', blob))
       if 'evergreenoc.com' not in u]
print("external links:", ext or "none")

lv = set()
for v in m.values():
    if isinstance(v, str): lv |= set(re.findall(r'<(h[1-6])', v))
print("heading levels:", sorted(lv), "-- expect ['h3'] only")

jet = {k: v for k, v in m.items() if not k.startswith('_')}
print("populated:", sum(1 for v in jet.values() if v not in ('', [], {}, None)), "/", len(jet))
```

Pass criteria: **no external links**, **`h3` only**, **39+/40 fields populated**.

### 8. Preview

```
https://staging2.evergreenoc.com/?post_type=strain&p=<id>&preview=true
```

Requires a logged-in wp-admin session. Check both background treatments —
sections alternate cream and dark, and colour bugs only ever showed on one.

### 9. Publish

Only after review, and only once `price` is filled in. Leave as draft otherwise.

---

## Part 2 — What's still outstanding

### Price is blank

There is a price field on the page and it is empty, because nobody has said what
a strain costs. The note beside it still reads "confirm live price."

Being handled later, once all 96 strains are loaded.

---

## Part 2b — The template (done)

The Cultivation and How to Use sections now exist on the page. Recorded here so
the next person knows how it was built and what to watch for.

**The template is `14266`** — not any of the three templates with "Strain" in
the name. Those are unused leftovers. The live one is titled "Elementor Single
Post #14266" and is the only one whose display condition is
`include/singular/strain`. Confirm from a rendered page (`elementor-page-<id>`
in the body class) rather than from template titles.

**Sections were cloned, not authored.** Cultivation is a copy of Appearance
(dark) and How to Use a copy of The Strain (cream), each rebound to the new
fields. Cloning inherits every typography and spacing setting, so the new
sections match the rest of the page automatically. Both new repeaters hold
label/value data, so they reuse `.eg-spec` (dark) and `.eg-glance` (cream).

They sit after Flavor, which keeps page order matching field-tab order and
preserves the existing cream/dark alternation. Numbered eyebrows were
resequenced to 01–09.

**Empty sections hide themselves.** A strain with no Cultivation copy would
otherwise render an empty labelled band — the field widgets drop out on their
own but the container and eyebrow do not. Both containers carry
`eg-optional-sect`, and the prose snippet hides any such section containing no
JetEngine output:

```css
.eg-optional-sect:not(:has(.jet-listing)){display:none!important}
```

So un-migrated strains look exactly as they did before, and a section appears
the moment that strain gets copy. No cleanup pass needed later.

### Cache: the step that looks like a failed save

After writing `_elementor_data`, the front end kept serving the old layout —
including on pages never fetched before, so it was not page caching. Purging
SiteGround alone does nothing here. Elementor caches the rendered document
separately and must be cleared first:

```bash
DELETE /elementor/v1/cache          # Elementor — this is the one that matters
PUT    /siteground-optimizer/v1/purge-cache   # then SiteGround
```

`purge-cache` is **PUT**, not POST; POST returns a confusing 404. If a template
edit appears not to have saved, re-read `_elementor_data` over REST before
assuming the write failed — it is almost always the cache.

---

## Part 3 — Reference

### Field schema

40 fields across 11 tabs. `_html` fields are WYSIWYG; the rest are text unless
noted.

```
Buy Hero          strain_type(select) hero_title buy_kick hero_lede thc cbd
                  lineage timing price price_note otd_note
                  buy_buttons[style,label,url]  trust_items[icon,text]
About             about_headline about_html  glance[label,value]
Effects           effects_headline effects_html  pills[label]
Flavor            flavor_headline flavor_html  terps[name,type,text]
Cultivation       cultivation_headline cultivation_html  grow_specs[label,value]
How to Use        use_headline use_html  use_methods[label,text]
In the Jar        jar_headline jar_html  spec[label,value]
Order Steps       steps_headline  steps_items[title,text]
Related           related_headline
FAQ               faq_headline  faqs[question,answer]
CTA               cta_kick cta_headline  cta_buttons[style,label,url]  cta_license
```

### Prose colour palette

Set by the WPCode global stylesheet plus snippet `14574`:

| | Cream sections | Dark sections |
|---|---|---|
| `p`, `li` | `#4A5A4E` | `#D9D4C4` |
| `strong`, `h2`–`h4` | `#0E2A1E` | `#F3EFE2` |
| bullet dash | `#1f8a5f` | `#8fd36b` |

The template decides which class a section gets, so content must never hardcode
a colour — it would be wrong on one of the two backgrounds.

### Rollback

| To undo | How |
|---|---|
| One strain's content | Restore from `docs/strain-migration/<slug>-<id>-before.json` |
| Heading/list CSS | Delete Elementor snippet `14574` |
| Post type schema | Restore `docs/strain-migration/strain-cpt-before-rest-migration.json` via `POST /jet-engine/v2/edit-post-type/2` |
| Template sections | Restore `docs/strain-migration/template-14266-before-new-sections.json` into `_elementor_data` on `14266`, then clear the Elementor cache |
