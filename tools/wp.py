#!/usr/bin/env python3
"""Evergreen OC — WordPress REST client.

A dependency-free command line client for making updates to the Evergreen OC
WordPress site through the WordPress REST API.

Defaults to the **staging** site, https://staging2.evergreenoc.com. Production
(https://evergreenoc.com) is only targeted when WP_SITE says so explicitly, and
the client prints a warning when it does.

Credentials are never stored in this repo. They are read from the environment,
or from an untracked `.env.wordpress` file at the repo root:

    WP_SITE=https://staging2.evergreenoc.com
    WP_USER=your-wordpress-username
    WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

`WP_APP_PASSWORD` is an *Application Password* (WP Admin -> Users -> Profile ->
Application Passwords), not the account's login password. Spaces in it are
optional; they are stripped before use.

Usage examples:

    python3 tools/wp.py whoami
    python3 tools/wp.py list pages --search "delivery"
    python3 tools/wp.py get pages 10048
    python3 tools/wp.py get pages 10048 --field content --raw > home.html
    python3 tools/wp.py update pages 10048 --title "New title"
    python3 tools/wp.py update pages 10048 --content-file home.html
    python3 tools/wp.py create posts --title "Hello" --content "<p>Hi</p>" --status draft
    python3 tools/wp.py upload ./promo.jpg --title "Spring promo"
    python3 tools/wp.py raw GET /wp/v2/settings

Both sites sit behind SiteGround bot protection, which serves a captcha
interstitial instead of the API response when the calling IP is rate limited.
The challenge is bursty rather than a sustained block, so a prompt retry clears
it; every request here sends a browser User-Agent and retries automatically.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.wordpress"

STAGING_SITE = "https://staging2.evergreenoc.com"
PRODUCTION_SITE = "https://evergreenoc.com"

# Work happens on staging unless WP_SITE explicitly says otherwise.
DEFAULT_SITE = STAGING_SITE

# Identify the tool honestly. This started out as a spoofed Chrome string,
# picked to get past what looked like a UA-based block, and that was the cause
# of most of the trouble that followed: SiteGround's WAF carries rules against
# outdated Chrome user agents, because that is what malicious traffic tends to
# claim to be. Tripping those rules repeatedly greylisted the whole egress
# range into the captcha service.
#
# A descriptive agent saying what the software is and where to complain about
# it is both the honest answer and the one that stops the blocks. Never put a
# browser string here.
USER_AGENT = "EvergreenOC-ContentSync/1.0 (WordPress REST client; +https://evergreenoc.com)"

# This file has twice reverted to an older commit that still carried the spoofed
# string, and the first request afterwards re-earned a greylisting. Refusing to
# start is cheaper than another block, so fail loudly rather than send it.
if any(token in USER_AGENT for token in ("Mozilla", "Chrome", "Safari", "Gecko")):
    raise SystemExit(
        "refusing to run: USER_AGENT is a browser string. That is what greylists "
        "the egress range. Check out the current tools/wp.py before retrying."
    )

TIMEOUT = 60

# SiteGround rate limits per IP and answers challenged requests with a captcha
# interstitial. Measured on staging it hits ~50% of requests in a burst but
# clears on the very next attempt, so retry fast first and only then back off.
CAPTCHA_RETRIES = 8
CAPTCHA_BACKOFF = [0.5, 1, 2, 4, 8, 15, 30]


class WPError(RuntimeError):
    pass


class CaptchaChallenge(RuntimeError):
    pass


# --------------------------------------------------------------------------
# credentials
# --------------------------------------------------------------------------


def load_env_file(path: Path = ENV_FILE) -> None:
    """Load KEY=VALUE lines from an untracked env file without overriding
    variables already present in the real environment."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_warned_production = False


def warn_if_production(site: str) -> None:
    """Say so, once, when a command is pointed at the live site."""
    global _warned_production
    if not _warned_production and site.rstrip("/") == PRODUCTION_SITE:
        _warned_production = True
        print(
            "WARNING: targeting PRODUCTION (evergreenoc.com), not staging. "
            "Changes here are live to customers.",
            file=sys.stderr,
        )


def credentials() -> tuple[str, str, str]:
    load_env_file()
    site = (os.environ.get("WP_SITE") or DEFAULT_SITE).rstrip("/")
    warn_if_production(site)
    user = os.environ.get("WP_USER", "")
    # Application passwords are displayed in space-separated groups of four.
    password = (os.environ.get("WP_APP_PASSWORD") or "").replace(" ", "")
    if not user or not password:
        raise WPError(
            "Missing credentials. Set WP_USER and WP_APP_PASSWORD in the "
            f"environment or in {ENV_FILE}.\n"
            "Create an Application Password at "
            f"{site}/wp-admin/profile.php (Users -> Profile -> Application "
            "Passwords)."
        )
    return site, user, password


# --------------------------------------------------------------------------
# transport
# --------------------------------------------------------------------------


def request(
    method: str,
    route: str,
    params: dict | None = None,
    data: dict | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
    extra_headers: dict | None = None,
):
    """Call the WordPress REST API, retrying past SiteGround's rate limiter.

    A captcha challenge is served by the edge and never reaches WordPress, so
    retrying is safe even for POSTs — no write can have been applied.
    """
    for attempt in range(CAPTCHA_RETRIES + 1):
        try:
            return _request_once(method, route, params, data, body, content_type, extra_headers)
        except CaptchaChallenge:
            if attempt == CAPTCHA_RETRIES:
                raise WPError(
                    "SiteGround bot protection returned a captcha instead of the "
                    f"API response, and it did not clear after {CAPTCHA_RETRIES} "
                    "retries. The site is rate limiting this IP. Either wait and "
                    "retry, or allow the IP in Site Tools -> Security."
                ) from None
            delay = CAPTCHA_BACKOFF[min(attempt, len(CAPTCHA_BACKOFF) - 1)]
            print(
                f"note: rate limited by SiteGround, retrying in {delay}s "
                f"({attempt + 1}/{CAPTCHA_RETRIES})",
                file=sys.stderr,
            )
            time.sleep(delay)
    raise WPError("unreachable")


def _request_once(
    method: str,
    route: str,
    params: dict | None = None,
    data: dict | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
    extra_headers: dict | None = None,
):
    """Make a single REST call and return (payload, response_headers)."""
    site, user, password = credentials()

    route = route if route.startswith("/") else "/" + route
    url = f"{site}/wp-json{route}"
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url += "?" + urllib.parse.urlencode(clean, doseq=True)

    payload = body
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        content_type = content_type or "application/json"

    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {token}",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if content_type:
        headers["Content-Type"] = content_type
    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(url, data=payload, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            resp_headers = dict(resp.headers)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            detail = json.loads(raw.decode("utf-8"))
            message = detail.get("message", raw.decode("utf-8", "replace")[:500])
            code = detail.get("code", "")
        except Exception:
            message = raw.decode("utf-8", "replace")[:500]
            code = ""
        hint = ""
        if exc.code == 401:
            hint = (
                "\nHint: 401 means the username or Application Password was "
                "rejected. Confirm WP_USER is the WordPress username (not the "
                "email) and that the Application Password has not been revoked."
            )
        elif exc.code == 403:
            hint = (
                "\nHint: 403 usually means the account lacks the capability for "
                "this action, or a security plugin blocked the request."
            )
        raise WPError(f"HTTP {exc.code} {code} on {method.upper()} {url}: {message}{hint}") from None
    except urllib.error.URLError as exc:
        raise WPError(f"Could not reach {url}: {exc.reason}") from None

    text = raw.decode("utf-8", "replace")
    if text.lstrip().startswith("<"):
        if "sgcaptcha" in text:
            raise CaptchaChallenge()
        raise WPError(f"Expected JSON from {url} but received HTML:\n{text[:400]}")
    try:
        return json.loads(text) if text else None, resp_headers
    except json.JSONDecodeError:
        raise WPError(f"Could not parse JSON from {url}:\n{text[:400]}") from None


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def rendered(value) -> str:
    """WordPress returns many fields as {'rendered': ..., 'raw': ...}."""
    if isinstance(value, dict):
        return value.get("raw") or value.get("rendered") or ""
    return "" if value is None else str(value)


def summarize(item: dict) -> str:
    title = rendered(item.get("title")).strip() or "(no title)"
    return (
        f"{item.get('id'):>7}  {item.get('status', ''):<8} "
        f"{title[:58]:<58} {item.get('link', '')}"
    )


def read_content(args) -> str | None:
    if getattr(args, "content_file", None):
        return Path(args.content_file).read_text(encoding="utf-8")
    return getattr(args, "content", None)


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------


def cmd_whoami(args) -> int:
    site, user, _ = credentials()
    me, _ = request("GET", "/wp/v2/users/me", params={"context": "edit"})
    env = "STAGING" if site == STAGING_SITE else ("PRODUCTION" if site == PRODUCTION_SITE else "custom")
    print(f"Site        : {site}  [{env}]")
    print(f"Connected as: {me.get('name')} (username: {me.get('slug')}, id: {me.get('id')})")
    print(f"Email       : {me.get('email', 'n/a')}")
    print(f"Roles       : {', '.join(me.get('roles', [])) or 'n/a'}")

    caps = me.get("capabilities", {}) or {}
    wanted = ["edit_posts", "publish_posts", "edit_pages", "upload_files", "manage_options"]
    granted = [c for c in wanted if caps.get(c)]
    print(f"Can         : {', '.join(granted) or 'no editing capabilities'}")

    settings, _ = request("GET", "/wp/v2/settings")
    print(f"Site title  : {settings.get('title')}")
    print(f"Front page  : id {settings.get('page_on_front')}")
    return 0


def cmd_list(args) -> int:
    params = {
        "per_page": args.per_page,
        "page": args.page,
        "search": args.search,
        "status": args.status,
        "orderby": args.orderby,
        "order": args.order,
        "context": "edit",
        "_fields": "id,status,title,link,modified",
    }
    items, headers = request("GET", f"/wp/v2/{args.type}", params=params)
    total = headers.get("X-WP-Total", "?")
    pages = headers.get("X-WP-TotalPages", "?")
    print(f"{len(items)} of {total} {args.type} (page {args.page} of {pages})\n")
    print(f"{'ID':>7}  {'STATUS':<8} {'TITLE':<58} LINK")
    for item in items:
        print(summarize(item))
    return 0


def cmd_get(args) -> int:
    item, _ = request("GET", f"/wp/v2/{args.type}/{args.id}", params={"context": "edit"})
    if args.field:
        value = item.get(args.field)
        print(rendered(value) if args.raw else json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(item, indent=2, ensure_ascii=False))
    return 0


def cmd_update(args) -> int:
    payload: dict = {}
    if args.title is not None:
        payload["title"] = args.title
    if args.status is not None:
        payload["status"] = args.status
    if args.slug is not None:
        payload["slug"] = args.slug
    content = read_content(args)
    if content is not None:
        payload["content"] = content
    if args.meta:
        payload.update(json.loads(args.meta))
    if not payload:
        raise WPError("Nothing to update. Pass --title, --content, --content-file, --status, --slug or --meta.")

    if not args.yes:
        current, _ = request("GET", f"/wp/v2/{args.type}/{args.id}", params={"context": "edit"})
        print(f"About to update {args.type}/{args.id}: {rendered(current.get('title'))}")
        print(f"Fields       : {', '.join(payload)}")
        print(f"Link         : {current.get('link')}")
        if input("Proceed? [y/N] ").strip().lower() not in {"y", "yes"}:
            print("Aborted.")
            return 1

    item, _ = request("POST", f"/wp/v2/{args.type}/{args.id}", data=payload)
    print(f"Updated {args.type}/{item.get('id')} -> {item.get('link')} (status: {item.get('status')})")
    return 0


def cmd_create(args) -> int:
    payload = {"title": args.title, "status": args.status}
    content = read_content(args)
    if content is not None:
        payload["content"] = content
    if args.slug:
        payload["slug"] = args.slug
    if args.meta:
        payload.update(json.loads(args.meta))
    item, _ = request("POST", f"/wp/v2/{args.type}", data=payload)
    print(f"Created {args.type}/{item.get('id')} -> {item.get('link')} (status: {item.get('status')})")
    return 0


def cmd_upload(args) -> int:
    path = Path(args.file)
    if not path.is_file():
        raise WPError(f"No such file: {path}")
    import mimetypes

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    item, _ = request(
        "POST",
        "/wp/v2/media",
        body=path.read_bytes(),
        content_type=mime,
        extra_headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )
    print(f"Uploaded media/{item.get('id')} -> {item.get('source_url')}")
    if args.title:
        request("POST", f"/wp/v2/media/{item['id']}", data={"title": args.title})
        print(f"Title set to: {args.title}")
    return 0


def cmd_raw(args) -> int:
    data = json.loads(args.data) if args.data else None
    result, headers = request(args.method, args.route, data=data)
    if args.headers:
        for key in ("X-WP-Total", "X-WP-TotalPages"):
            if key in headers:
                print(f"{key}: {headers[key]}", file=sys.stderr)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wp.py",
        description="WordPress REST client for the Evergreen OC site.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("whoami", help="verify the connection and show account capabilities")

    p_list = sub.add_parser("list", help="list pages, posts, media or any post type")
    p_list.add_argument("type", nargs="?", default="pages")
    p_list.add_argument("--search")
    p_list.add_argument("--status", default="any")
    p_list.add_argument("--per-page", type=int, default=25)
    p_list.add_argument("--page", type=int, default=1)
    p_list.add_argument("--orderby", default="modified")
    p_list.add_argument("--order", default="desc", choices=["asc", "desc"])

    p_get = sub.add_parser("get", help="fetch one item as JSON")
    p_get.add_argument("type")
    p_get.add_argument("id")
    p_get.add_argument("--field", help="print only this field, e.g. content")
    p_get.add_argument("--raw", action="store_true", help="print the field unquoted")

    p_update = sub.add_parser("update", help="update an existing item")
    p_update.add_argument("type")
    p_update.add_argument("id")
    p_update.add_argument("--title")
    p_update.add_argument("--content")
    p_update.add_argument("--content-file")
    p_update.add_argument("--status")
    p_update.add_argument("--slug")
    p_update.add_argument("--meta", help="extra fields as a JSON object")
    p_update.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")

    p_create = sub.add_parser("create", help="create a new item")
    p_create.add_argument("type")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--content")
    p_create.add_argument("--content-file")
    p_create.add_argument("--status", default="draft")
    p_create.add_argument("--slug")
    p_create.add_argument("--meta", help="extra fields as a JSON object")

    p_upload = sub.add_parser("upload", help="upload a file to the media library")
    p_upload.add_argument("file")
    p_upload.add_argument("--title")

    p_raw = sub.add_parser("raw", help="call any REST route directly")
    p_raw.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    p_raw.add_argument("route", help="e.g. /wp/v2/settings")
    p_raw.add_argument("--data", help="request body as a JSON object")
    p_raw.add_argument("--headers", action="store_true", help="print pagination headers to stderr")

    return parser


COMMANDS = {
    "whoami": cmd_whoami,
    "list": cmd_list,
    "get": cmd_get,
    "update": cmd_update,
    "create": cmd_create,
    "upload": cmd_upload,
    "raw": cmd_raw,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except WPError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
