#!/usr/bin/env python3
"""
One-time migration: reads the existing hand-coded Feast blog-cards out of
index.html and writes them into data/feast.yml as structured entries.

Run this ONCE from the repo root:
    python scripts/migrate_html_to_yaml.py

After this you edit data/feast.yml (not index.html directly) to add new
Feast posts. build_site.py regenerates the HTML and build_feed.py
regenerates feed.xml from that same file.

NOTE: run this against an index.html where the known malformed tags have
already been fixed (see the two bugs flagged separately: the stray extra
<h2> after "Severance", and the </h3> that should be </h2> after "My Tarot
Collection on Display") -- otherwise a couple of entries will parse oddly.
"""
import re
import sys
from datetime import datetime

import yaml
from bs4 import BeautifulSoup
from dateutil import parser as dateparser


def clean_text(text: str) -> str:
    """Collapse whitespace left over from stripping inline tags (<a>, <br>,
    etc.) out of a paragraph so words don't get jammed together."""
    return re.sub(r"\s+", " ", text or "").strip()

SOURCE_FILE = "index.html"
OUTPUT_FILE = "data/feast.yml"


def parse_date(raw_text: str):
    try:
        return dateparser.parse(raw_text.strip()).date()
    except (ValueError, TypeError, OverflowError):
        return None


def extract_background_url(style_attr: str):
    if not style_attr or "url(" not in style_attr:
        return None
    start = style_attr.find("url(") + 4
    end = style_attr.find(")", start)
    return style_attr[start:end].strip("'\"")


def extract_background_extra(style_attr: str):
    """Some cards fine-tune image cropping with background-position/-size/
    -repeat alongside background-image. Preserve those declarations so the
    regenerated HTML doesn't lose custom cropping on those cards."""
    if not style_attr:
        return None
    # Strip out the background-image:url(...) declaration, keep the rest.
    start = style_attr.find("background-image")
    if start == -1:
        return style_attr.strip() or None
    url_end = style_attr.find(")", start)
    remainder = (style_attr[:start] + style_attr[url_end + 1 :]).strip()
    remainder = remainder.strip("; ").strip()
    return remainder or None


class QuotedDumper(yaml.SafeDumper):
    """Keeps multi-line summaries readable as YAML block scalars."""


def str_presenter(dumper, data):
    if "\n" in data or len(data) > 80:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


QuotedDumper.add_representer(str, str_presenter)


def main():
    try:
        with open(SOURCE_FILE, encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"Could not find {SOURCE_FILE} in the current directory.", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.blog-card")

    posts = []
    for card in cards:
        heading = card.select_one(".description h2")
        if not heading:
            continue

        link_tag = heading.find("a")
        title = clean_text(heading.get_text(" ", strip=True))
        raw_href = link_tag["href"] if (link_tag and link_tag.get("href")) else None
        # A couple of live-site links are missing their opening quote, e.g.
        # <a href=https://example.com/"> -- the parser then reads a stray
        # trailing " as part of the URL. Strip that artifact off.
        link = raw_href.rstrip('"\'') if raw_href else None

        subtitle_tag = card.select_one(".description h3")
        subtitle = clean_text(subtitle_tag.get_text(" ", strip=True)) if subtitle_tag else None

        desc_p = card.select_one(".description p")
        summary = clean_text(desc_p.get_text(" ", strip=True)) if desc_p else ""

        date_li = card.select_one("li.date")
        date_raw = clean_text(date_li.get_text(" ", strip=True)) if date_li else None
        post_date = parse_date(date_raw) if date_raw else None

        photo_div = card.select_one(".photo")
        photo_style = photo_div.get("style", "") if photo_div else ""
        image = extract_background_url(photo_style) if photo_div else None
        image_extra_style = extract_background_extra(photo_style) if photo_div else None
        image_alt = photo_div.get("aria-label") if photo_div else None

        tags = [clean_text(a.get_text(" ", strip=True)) for a in card.select(".tags a")]

        post = {
            "title": title,
            "link": link,
            "date": post_date if post_date else None,
            # Fallback display text for dates like "July & August, 2024"
            # that don't parse into a real calendar date.
            "date_raw": None if post_date else date_raw,
            "subtitle": subtitle,
            "summary": summary,
            "image": image,
            "image_extra_style": image_extra_style,
            "image_alt": image_alt,
            "tags": tags,
        }
        # Drop empty/None fields so the YAML file stays clean and easy to hand-edit.
        post = {k: v for k, v in post.items() if v not in (None, "", [])}
        posts.append(post)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(
            posts,
            f,
            Dumper=QuotedDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    linkless = [p["title"] for p in posts if "link" not in p]
    print(f"Migrated {len(posts)} posts to {OUTPUT_FILE}")
    if linkless:
        print("These posts have no link and won't appear in the RSS feed until you add one:")
        for t in linkless:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
