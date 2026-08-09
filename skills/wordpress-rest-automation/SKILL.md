---
name: wordpress-rest-automation
description: >
  Operating rules and a ready-made REST client for changing a WordPress site
  programmatically — content migrations, bulk edits across many pages, internal
  linking, publishing runs, media uploads, custom field writes, page-builder
  template changes. Reach for this at the START of any such job, before writing
  a client or touching the site, since most of what it prevents is cheaper to
  avoid than to diagnose: firewall blocks caused by the wrong User-Agent, writes
  that appear to save but never render, custom post types silently shadowing
  existing URLs, and placeholder text going public. Triggers on mentions of
  Application Passwords, wp-json, the WP REST API, ACF or JetEngine fields,
  Elementor templates, or moving and updating content across many pages at once
  — even when the user only describes the outcome they want. Also worth
  consulting when automated work starts returning captchas, 202s, 403s, 406s or
  unexplained 500s.
---

# Automating WordPress over the REST API

Most of the time lost on this kind of work goes to failures that present as
something other than what they are. A firewall challenge looks like a network
error. A cached template looks like a failed save. A charset limit looks like a
broken plugin. This skill exists so those hours are spent once, not per project.

## The rule that matters most

**Never send a browser User-Agent.** Send one that says what the software is:

```
<Agency>-ContentSync/1.0 (WordPress REST client; +https://clientsite.com)
```

Hosting firewalls carry rules against outdated browser strings, because that is
what malicious traffic claims to be. A spoofed Chrome string will get an entire
egress IP range greylisted, and because cloud tooling rotates IPs, that block
then follows you everywhere.

If being blocked ever tempts you to disguise the client better, that instinct is
the bug. Being honest about what you are is both the ethical answer and the one
that actually works — support teams can allowlist a named client, and cannot
help a fake browser.

## Start here

`scripts/wp_client.py` is a dependency-free REST client that already handles the
User-Agent, retries, staging defaults and credential loading. Copy it into the
project rather than writing another one — every project otherwise reinvents it,
usually without the retry logic.

```bash
cp scripts/wp_client.py <project>/tools/wp.py
python3 tools/wp.py whoami        # confirms auth and what the account can edit
```

Credentials come from an untracked `.env.wordpress`:

```ini
WP_SITE=https://staging.clientsite.com
WP_USER=wordpress-username        # the username, not the email address
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

Application Passwords (Users → Profile) are the right credential: revocable in
one click, and useless for signing in. Never the account password. Add
`.env.wordpress` to `.gitignore` before the first commit.

## Before writing anything

**Back up each record before you touch it.** One JSON file per post, committed.
This turns any mistake into a revert instead of an incident, and it is the
difference between "I can undo that" and "I need the client's database backup".

**Default to staging.** Reach production only when explicitly asked, and say so
when you do.

**Dry-run bulk operations first** and show the plan. A diff of what would change
catches mapping errors that no amount of careful coding does.

## When something fails

Match the symptom before theorising. These are the ones that cost real time:

| What you see | What it usually is |
|---|---|
| `202` with a tiny HTML body | Firewall captcha. Fix the User-Agent, slow down |
| `403` on `/batch/v1` | Host blocks the endpoint. Fall back to individual writes |
| `406` | Some WAFs reject browser UAs specifically. Try sending none |
| `401` | Username is probably the email; use the WP username |
| `500 rest_meta_database_error` | 4-byte characters in a 3-byte `utf8` column |
| `200` with an HTML body | A challenge page wearing a success code — check the body |
| Saved change does not render | Page builder cache, not a failed save |
| Content silently reverts | A stale wp-admin tab was saved over it |

`references/gotchas.md` explains each of these with the fix. Read it when you
hit one, or before starting a migration, since several are cheaper to avoid than
to diagnose.

## Two habits worth keeping

**Read the value back before concluding a write failed.** Caching makes a
successful write look like a failure often enough that "verify, then diagnose"
saves more time than it costs.

**Stop when the success rate collapses.** Aggressive retries are exactly what
firewalls greylist, so pushing through a block extends it. One job at a time,
back off in minutes, and if requests start consistently failing, stop and work
out why. Two concurrent jobs against a rate-limited host is how a slowdown
becomes an outage.

## Finishing a job

The gap between "the data is correct" and "the page is right" is where this work
usually goes wrong, because automated checks confirm the first and only a human
eye catches the second.

- **Look at the rendered page.** Links can be present, correct, resolving, and
  invisible because nothing styled them. Data checks will not tell you this.
- **Grep every field for `TODO FIXME XXX TBD PLACEHOLDER LOREM WIP`.**
  Placeholders that were harmless in drafts become public the moment you publish.
- **Check contrast** if you have set any colour. A brand colour that works on a
  dark section can be unreadable on a light one.
- **Report what actually happened.** A job that wrote 82 of 95 records wrote 82.
  Partial success reported as success is how the remaining 13 get discovered by
  the client.
