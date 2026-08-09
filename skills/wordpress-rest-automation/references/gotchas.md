# Gotchas reference

Each failure below, with the fix. SKILL.md's symptom table links here.

Field notes for any tool that talks to the WordPress REST API — Claude Code, a
script, a scraper, an integration.

Written from a 97-page content migration, but the failures below are not
specific to that project. Most of them present as something other than what
they are, which is why they cost hours rather than minutes.

**Each item is tagged with where it applies:**

| Tag | Applies to |
|---|---|
| `[ANY]` | Any host, any site |
| `[HOST]` | Hosting firewalls generally — examples here are SiteGround |
| `[WP]` | WordPress itself |
| `[PLUGIN]` | A specific plugin — Elementor, JetEngine, etc. |
| `[US]` | Our own process, not the software |

---

## The one rule

**Never send a browser User-Agent. Say what your software actually is.**

Hosting firewalls block outdated browser strings on sight, because that is what
malicious traffic pretends to be. On the project this came from, one wrong
header greylisted an entire IP range and cost most of a working day.

```
✅  YourAgency-ContentSync/1.0 (WordPress REST client; +https://clientsite.com)
❌  Mozilla/5.0 (Macintosh...) Chrome/126.0.0.0 Safari/537.36
```

If you are ever tempted to spoof a browser to get past a block, that instinct
is the bug. The fix for being blocked is to identify the client properly, not
to disguise it better.

---

## Before you start

1. Create an **Application Password** (Users → Profile), never the login
   password. It is revocable in one click and cannot be used to sign in.
2. Set a **descriptive User-Agent** with a contact URL.
3. **Tell the host before a bulk job.** A heads-up costs a support ticket;
   being greylisted mid-run costs a day.
4. Check the **database charset** if content may contain emoji (see #5).
5. **Back up every record before writing to it.** One JSON file per post, kept
   in the repo, turns any mistake into a one-line revert.

---

## What will bite you

### 1. The block is invisible in the host's logs `[HOST]`

**Symptom** — Requests return `HTTP 202` with a tiny HTML body that
meta-refreshes to a captcha URL. Support replies: *"we see normal 200 OK
responses, your IP isn't blocked."*

**Cause** — The challenge is served by the edge firewall, *in front of* PHP.
WordPress never receives the request, so it never reaches the site's access log.

**Fix** — Send support the response headers, not a description:

```http
HTTP/2 202
sg-captcha: challenge          ← names the security layer directly
server: nginx
```

Any host has an equivalent header. Find it and quote it.

---

### 2. Your IP rotates, so one allowlist entry is useless `[ANY]`

**Symptom** — Host allowlists the IP you sent; you are still blocked.

**Cause** — Cloud tooling egresses from a pool. We saw eight different
addresses in under a minute.

**Fix** — Sample it, then give the host the whole range:

```bash
for i in $(seq 1 30); do curl -s https://api.ipify.org; echo; done | sort -u
```

Better still, fix the User-Agent so no allowlist is needed at all.

---

### 3. Retrying harder makes it permanent `[ANY]`

**Symptom** — A half-working job stops working entirely and stays broken for
hours.

**Cause** — Aggressive retry loops are exactly the pattern a firewall
greylists. Running two jobs at once doubles it.

**Fix** — One job at a time. Back off in minutes, not milliseconds. **If the
success rate drops toward zero, stop** — continuing renews the timer rather
than getting through.

---

### 4. Page builders cache separately from the host `[PLUGIN]`

**Symptom** — You edit a template, the change saves, and the page still shows
the old version — even on URLs never visited before. Looks exactly like a
failed save.

**Cause** — The builder caches rendered output independently. Purging the host
cache does nothing for it.

**Fix** — Clear the builder first, then the host. For Elementor on SiteGround:

```
DELETE /wp-json/elementor/v1/cache                     ← this one matters
PUT    /wp-json/siteground-optimizer/v1/purge-cache    ← PUT, not POST
```

`POST` to that purge route returns a confusing 404.

**Before assuming a write failed, read the value back over the API.** It is
almost always cached, not broken.

---

### 5. Emoji silently break database writes `[WP]`

**Symptom** — `HTTP 500 rest_meta_database_error` — *"Could not update the meta
value of X in database."* Only some records fail.

**Cause** — The table is 3-byte `utf8`, which cannot store 4-byte characters.
Any emoji in the content kills the write.

**Fix** — Encode astral characters as HTML entities before writing. They still
render correctly and store as plain ASCII:

```python
"".join(c if ord(c) <= 0xFFFF else f"&#x{ord(c):X};" for c in text)
```

The alternative is converting the table to `utf8mb4`, which is a hosting task.

---

### 6. Custom field plugins hide their data from the API `[PLUGIN]`

**Symptom** — `meta` comes back `null`, and posting a meta payload is rejected
outright.

**Cause** — Fields are not registered for REST.

**Fix** — Expose them. With JetEngine specifically, the `show_in_rest` flag is
neither in the field schema nor in the UI, but the plugin honours it if you
write it into the post type definition anyway. Test on one field, confirm by
re-reading a post, then roll out.

**Any field added later needs the same flag** or it will silently fail to save.

---

### 7. An open wp-admin tab will wipe your work `[WP]`

**Symptom** — Content written via the API reverts to its old state, with no
error anywhere.

**Cause** — An edit screen opened *before* the API write, then saved, submits
the stale form it loaded with — overwriting everything.

**Fix** — Close or reload wp-admin tabs before running a job, and again before
saving anything by hand afterwards. If content reverts, check the post's
`modified` timestamp — it names the culprit.

---

### 8. Custom post types swallow a whole URL path `[WP]`

**Symptom** — Existing pages under `/thing/` start returning 404 the moment a
custom post type is registered with that rewrite slug.

**Cause** — The post type claims the entire path. Old pages still exist in
wp-admin but have no working URL.

**Fix** — If old and new share a slug, **the URL is unchanged: publish, don't
redirect.** A 301 there would intercept the URL before the new post could serve
it, and point it at itself. Only genuinely orphaned URLs need redirects.

When you do add one, make it an **exact, non-regex match**. A prefix rule on
`/thing/` will swallow every `/thing/<slug>/` page beneath it.

---

### 9. Draft posts are 404s, and internal links to them are dead `[WP]`

**Symptom** — A link audit passes — every link present, correct, pointing
somewhere real — yet the links do not work.

**Cause** — The targets are unpublished. The link is right; the page is not
there yet.

**Fix** — Audit two things separately: *is the link correct*, and *would it
load for a visitor*. Publishing is the fix, not a redirect.

---

### 10. "It's there" is not "you can see it" `[US]`

**Symptom** — Links verified present and resolving, but invisible on the page.
The client finds them by browsing; the audit never would.

**Cause** — The theme styled paragraphs and bold text but never anchors, so
links inherited body colour with no underline.

**Fix** — After any content job, **look at the rendered page.** Automated
checks confirm data, not design.

Check contrast too — a brand colour that works on a dark band can be
unreadable on a light one. Anything below roughly 4.5:1 against its background
fails.

---

### 11. Grep for developer notes before publishing `[US]`

**Symptom** — A field reading `TODO(Pro): confirm live price` rendered publicly
on 89 pages the moment they were published.

**Cause** — Placeholders left by whoever built the template. Harmless while
everything was a draft.

**Fix** — Before publishing, scan every field:

```
TODO  FIXME  XXX  TBD  PLACEHOLDER  LOREM  WIP  CHANGEME
```

Treat a TODO as a real task: resolve it, or remove the note. Do not leave it
standing.

---

### 12. Every host's firewall has different rules `[HOST]`

**Symptom** — The header that fixes one site breaks another.

**Cause** — On one project SiteGround challenged browser user-agents, while a
Fastly-fronted storefront did the exact opposite: `406` to browser strings,
and requests with *no* User-Agent served normally.

**Fix** — Test each host with a handful of requests before assuming. Document
what worked, per host, in the repo.

---

## Reading the response

| Code | Usually means | Do this |
|---|---|---|
| `202` | Firewall captcha challenge, not a real response | Fix the User-Agent; slow down |
| `403` | WAF rule, or a blocked endpoint (`/batch/v1` often is) | Fall back to individual requests |
| `406` | Some WAFs reject browser UAs specifically | Try with no User-Agent |
| `401` | App Password wrong, or username is the email | Use the WP username, not the email |
| `500` | `rest_meta_database_error` — charset, see #5 | Encode 4-byte characters |
| `200` + HTML | A challenge page wearing a success code | Check the body, not just the status |

---

## Working with hosting support

- **Lead with evidence.** Response headers, exact status codes, timestamps and
  the full IP range. *"It's blocked"* gets *"our logs look fine."*
- **Ask which layer.** WordPress, `.htaccess`, or the edge firewall? Different
  teams, different fixes.
- **Do not ask them to switch off security rules.** If support offers, decline.
  On the project this came from, the rules were right and our header was wrong.
- **Ask for delisting, not just allowlisting.** Existing greylist entries
  persist after an allowlist is added and will keep challenging you until they
  are cleared or expire.

---

## Reusing this on a new account

1. Swap the User-Agent for `<YourAgency>-<Tool>/1.0 (+https://clientsite.com)`.
2. Confirm the host. `[HOST]` items reference SiteGround; other hosts have
   equivalents under different header names.
3. Confirm the stack. `[PLUGIN]` items reference Elementor and JetEngine.
   Different builder, same lesson — check whether it caches separately, and
   whether custom fields are exposed to REST.
4. `[ANY]`, `[WP]` and `[US]` items apply everywhere, unchanged.
