#!/usr/bin/env python3
"""
Builds feed.xml (RSS 2.0) from data/feast.yml.

Run from the repo root:
    python scripts/build_feed.py
"""
import sys
from datetime import datetime, time, timezone
from urllib.parse import urljoin

import yaml
from feedgen.feed import FeedGenerator

SITE_URL = "https://monsterbyte.lol"
DATA_FILE = "data/feast.yml"
OUTPUT_FILE = "feed.xml"
MAX_ITEMS = 20  # keep the feed to the most recent N posts


def absolute_url(href: str) -> str:
    return urljoin(SITE_URL + "/", href)


def main():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            posts = yaml.safe_load(f) or []
    except FileNotFoundError:
        print(f"Could not find {DATA_FILE} in the current directory.", file=sys.stderr)
        sys.exit(1)

    fg = FeedGenerator()
    fg.title("Library Monster — Feast")
    fg.link(href=f"{SITE_URL}/", rel="alternate")
    fg.link(href=f"{SITE_URL}/feed.xml", rel="self")
    fg.description("Latest posts from the Feast section of monsterbyte.lol")
    fg.language("en")

    # data/feast.yml is ordered newest-first, same as the site itself.
    added = 0
    for post in posts:
        if added >= MAX_ITEMS:
            break

        link = post.get("link")
        title = post.get("title")
        if not link or not title:
            continue  # nothing for a feed reader to open

        summary_parts = [p for p in (post.get("subtitle"), post.get("summary")) if p]
        summary = " — ".join(summary_parts)

        pub_date = None
        if post.get("date"):
            pub_date = datetime.combine(post["date"], time.min, tzinfo=timezone.utc)

        fe = fg.add_entry(order="append")
        fe.title(title)
        fe.link(href=absolute_url(link))
        fe.guid(absolute_url(link), permalink=True)
        fe.description(summary or title)
        for tag in post.get("tags", []):
            fe.category(term=tag)
        if pub_date:
            fe.pubDate(pub_date)

        added += 1

    fg.rss_file(OUTPUT_FILE, pretty=True)
    print(f"Wrote {added} item(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
