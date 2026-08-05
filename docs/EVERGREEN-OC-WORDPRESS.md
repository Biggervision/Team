# Evergreen OC — WordPress connection

How Claude connects to **https://evergreenoc.com** to make updates to the site.

## The site

| | |
|---|---|
| URL | https://evergreenoc.com |
| Site title | Evergreen — *Premier Licensed Super Store* |
| Platform | WordPress |
| Theme | `hello-elementor` |
| Page builder | **Elementor Pro 4.1.5** (`elementor`, `pro-elements`, `elementskit-lite`, `rometheme-for-elementor`) |
| SEO | SEOPress |
| Other plugins | Klaviyo, Redirection, FileBird, MonsterInsights (Google Analytics) |
| Host | SiteGround (`sg-security`, `siteground-optimizer`) |
| Front page | Page ID `10048` (static front page) |

## How the connection works

There is no WordPress connector in the Claude connector directory for
self-hosted sites (only WordPress.com), and Composio has no WordPress toolkit.
The connection is made directly against the **WordPress REST API** at
`https://evergreenoc.com/wp-json/`, authenticated with an
**Application Password** over HTTPS.

The REST API is confirmed reachable and fully exposed:

```
namespaces : wp/v2, elementor/v1, elementor-pro/v1, seopress/v1, filebird/v1,
             klaviyo/v1, redirection/v1, sg-security/v1, monsterinsights/v1, ...
routes     : /wp/v2/posts  /wp/v2/pages  /wp/v2/media  /wp/v2/users/me  /wp/v2/settings
auth       : application-passwords enabled
             -> https://evergreenoc.com/wp-admin/authorize-application.php
```

### One gotcha: SiteGround bot protection

Requests without a browser `User-Agent` are intercepted by SiteGround's
`sg-security` plugin and answered with a captcha interstitial
(`/.well-known/sgcaptcha/`) instead of the API response. `tools/wp.py` always
sends a browser User-Agent, which clears the challenge. If the API ever starts
returning captcha HTML again, the server's IP needs to be allowed in
**Site Tools → Security → Blocked IPs / Anti-bot**.

## Setup (one time, ~2 minutes)

1. Log in to https://evergreenoc.com/wp-admin.
2. Go to **Users → Profile** (`/wp-admin/profile.php`), scroll to
   **Application Passwords**.
3. Enter a name — e.g. `Claude` — and click **Add New Application Password**.
4. Copy the generated password. It is shown **once** and looks like
   `abcd EFGH 1234 ijkl MNOP 5678`.
5. Create an untracked `.env.wordpress` at the repo root:

   ```bash
   cp .env.wordpress.example .env.wordpress
   ```

   ```ini
   WP_SITE=https://evergreenoc.com
   WP_USER=your-wordpress-username
   WP_APP_PASSWORD=abcd EFGH 1234 ijkl MNOP 5678
   ```

   `WP_USER` is the WordPress **username**, not the email address.
   `.env.wordpress` is listed in `.gitignore` and is never committed.
   Environment variables take precedence over the file if both are set.

6. Verify:

   ```bash
   python3 tools/wp.py whoami
   ```

   Expected output:

   ```
   Site        : https://evergreenoc.com
   Connected as: <name> (username: <slug>, id: <n>)
   Roles       : administrator
   Can         : edit_posts, publish_posts, edit_pages, upload_files, manage_options
   Site title  : Evergreen
   Front page  : id 10048
   ```

The Application Password can be revoked at any time from the same
**Users → Profile** screen, which instantly cuts off this access.

## Using it

```bash
# What can I reach?
python3 tools/wp.py whoami

# Find things
python3 tools/wp.py list pages --search "delivery"
python3 tools/wp.py list posts --status publish --per-page 10
python3 tools/wp.py list media --search "logo"

# Read
python3 tools/wp.py get pages 10048
python3 tools/wp.py get pages 10048 --field content --raw > /tmp/home.html

# Write (prompts for confirmation; -y to skip)
python3 tools/wp.py update pages 10048 --title "New title"
python3 tools/wp.py update pages 10048 --content-file /tmp/home.html
python3 tools/wp.py update posts 123 --status draft -y

# Create
python3 tools/wp.py create posts --title "Hello" --content "<p>Hi</p>" --status draft

# Media
python3 tools/wp.py upload ./promo.jpg --title "Spring promo"

# Anything else
python3 tools/wp.py raw GET /wp/v2/settings
python3 tools/wp.py raw GET "/wp/v2/pages?per_page=100&_fields=id,title"
```

`update` asks for confirmation before writing and prints the target page's
title and link first. Pass `-y` only when the change is already reviewed.

## Working with Elementor pages

Most public-facing pages on this site are **built in Elementor**, not the
WordPress block editor. That changes how edits must be made:

- `/wp/v2/pages/<id>` `content.rendered` returns Elementor's *generated*
  markup. **Writing to `content` does not change an Elementor page** — the
  builder re-renders from its own data on the next save or CSS regeneration,
  discarding the change.
- Elementor stores the real layout in the `_elementor_data` post meta as a
  JSON widget tree, with `_elementor_css` holding the generated stylesheet.
- Safe things to change over the plain REST API: **title, slug, status,
  excerpt, featured image, menu order, SEOPress meta**, and anything on
  non-Elementor posts.
- For layout or copy inside an Elementor page, the reliable routes are
  editing `_elementor_data` directly (requires the meta field to be exposed,
  and the Elementor CSS cache to be regenerated afterwards) or making the
  change in the Elementor editor UI.

Before changing any Elementor page, take a backup of the current state:

```bash
python3 tools/wp.py get pages 10048 > backups/page-10048-$(date +%F).json
```

The repo also carries an `elementor-html-conversion` skill for turning HTML
designs into Elementor build specs, which is the better path for new sections.

## Safety notes

- This is a **live production site** for a licensed cannabis dispensary.
  Publishing changes affects real customers, and compliance-sensitive copy
  (licence numbers, disclaimers, age gating) should not be edited casually.
- Default to `--status draft` for new content and let a human publish.
- Take a JSON backup before editing any existing page.
- Never commit `.env.wordpress`, and revoke the Application Password in
  **Users → Profile** when access is no longer needed.
