# Skills

Reusable Claude Code skills for this agency. A skill is a folder Claude reads
automatically when the work matches it, so the same hard-won rules apply on
every account without anyone having to paste them into a chat.

## wordpress-rest-automation

Everything learned on the Evergreen OC migration, written so it applies to any
WordPress site: the User-Agent rule that stops hosting firewalls from blocking
you, how to tell a captcha from a network error, why a saved change sometimes
does not render, and a dependency-free REST client that already handles all of
it.

### Install it on another account

Two ways, depending on where you want it to apply.

**One machine, all projects** — copy the folder into your personal skills
directory:

```bash
cp -r skills/wordpress-rest-automation ~/.claude/skills/
```

**One repo, everyone who works in it** — copy it into the project instead, and
commit it:

```bash
mkdir -p .claude/skills
cp -r /path/to/skills/wordpress-rest-automation .claude/skills/
```

**From the packaged file** — `wordpress-rest-automation.skill` is the same
content zipped up. In Claude Desktop or the web app, upload it and click
*Save skill*; it then travels with your account rather than a single machine.

Either way, start a new session afterwards. Claude picks the skill up on its
own the next time a job involves the WordPress REST API — there is nothing to
type.

### What is inside

| File | What it is |
|---|---|
| `SKILL.md` | The operating rules, loaded whenever the skill triggers |
| `references/gotchas.md` | Twelve failure modes with symptoms and fixes, read on demand |
| `scripts/wp_client.py` | The REST client to copy into a project as `tools/wp.py` |
| `evals/evals.json` | The test prompts used to check the skill actually helps |

### Does it help?

Measured by running the same task twice, once with the skill and once without:

| Test | With skill | Without |
|---|---|---|
| Planning a bulk migration | 8/8 | 4/8 |
| Diagnosing a live block | 6/6 | 6/6 |

The value is concentrated at the planning stage — the skill prevents the
mistakes, it does not add much once you are already debugging one.
