# Working in this repo

## WordPress automation — read before touching a live site

Full detail: [`docs/wordpress-automation-playbook.md`](docs/wordpress-automation-playbook.md)

These few are worth repeating here, because getting any of them wrong costs
hours and none of them are obvious from the error message.

**Never send a browser User-Agent.** Hosting firewalls block outdated browser
strings on sight, because that is what malicious traffic pretends to be. Send a
descriptive one naming the software and where to complain about it:

```
YourAgency-ContentSync/1.0 (WordPress REST client; +https://clientsite.com)
```

If a block tempts you to disguise the client better, that instinct is the bug.
Identify it properly instead.

**Stop when the success rate collapses.** Aggressive retries are what firewalls
greylist. One job at a time, back off in minutes, and if requests start failing
consistently, stop — continuing renews the block rather than getting through.

**Read the value back before believing a write failed.** Page builders cache
rendered output independently of the host cache, so a saved change can look
like a failed save. Clear the builder cache first, then the host.

**Back up every record before writing to it.** One JSON file per post in
`docs/*/backups*/` turns any mistake into a one-line revert.

**Look at the rendered page when the job is done.** Automated checks confirm
data, not design. Links can be present, correct, resolving, and invisible.

**Grep for `TODO FIXME XXX TBD PLACEHOLDER LOREM` before publishing anything.**
Placeholders that were harmless in drafts go public the moment you publish.

## Credentials

WordPress access uses an Application Password in an untracked `.env.wordpress`
at the repo root — never the account login password, never committed. See
`.env.wordpress.example`.

## Tooling

`tools/wp.py` is the WordPress REST client everything else builds on. It sets
the correct User-Agent, retries firewall challenges, and defaults to staging —
production is only reached when `WP_SITE` says so, and it warns when it does.
