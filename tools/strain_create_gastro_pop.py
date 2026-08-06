#!/usr/bin/env python3
"""Create the Gastro Pop strain page.

Gastro Pop was the one strain with an old page but no replacement, so its URL
was left 404 while every other strain moved across. It is absent from both the
production sitemap and the REST page listing that fed the bulk migration, which
is why it slipped through — the page itself is live and returns 200, so the
copy was there to migrate all along.

Source is the rendered production page rather than the old staging page. Both
carry the same nine sections and the same wording, but the staging copy stores
the FAQ accordion as flat markup the extractor cannot pair up, so it yielded
zero FAQs against production's nine.

SEO title and description come from the existing staging page, which mirrors
production's.

The page is created as a draft, matching the other 96, and carries the hub link
every strain gets. Its two related-strain links are deliberately absent: the
internal linking sheet has no row for Gastro Pop, so there is nothing to
implement, and inventing relationships is a content decision rather than a
mechanical one.

    python3 tools/strain_create_gastro_pop.py
"""
