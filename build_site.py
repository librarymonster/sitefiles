#!/usr/bin/env python3
"""
Regenerates the Feast section of index.html from data/feast.yml.

Requires two marker comments already placed in index.html, wrapping the
Feast blog-cards (put these where the cards currently live, replacing the
hand-written <div class="blog-card">...</div> blocks between them):

    <!-- FEAST:START -->
    <!-- FEAST:END -->

Run from the repo root:
    python scripts/build_site.py
"""
import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

DATA_FILE = "data/feast.yml"
INDEX_FILE = "index.html"
TEMPLATE_DIR = "templates"
TEMPLATE_NAME = "feast_card.html.j2"
START_MARKER = "<!-- FEAST:START -->"
END_MARKER = "<!-- FEAST:END -->"


def load_posts():
    with open(DATA_FILE, encoding="utf-8") as f:
        posts = yaml.safe_load(f) or []
    for post in posts:
        d = post.get("date")
        post["date_display"] = d.strftime("%B %-d, %Y") if d else post.get("date_raw", "")
    return posts


def render_cards(posts):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True
    )
    template = env.get_template(TEMPLATE_NAME)
    rendered = [
        template.render(post=post, is_alt=(i % 2 == 0))
        for i, post in enumerate(posts)
    ]
    return "\n".join(rendered)


def inject_into_index(cards_html: str):
    index_path = Path(INDEX_FILE)
    if not index_path.exists():
        print(f"Could not find {INDEX_FILE} in the current directory.", file=sys.stderr)
        sys.exit(1)

    html = index_path.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    if not pattern.search(html):
        print(
            f"Couldn't find {START_MARKER} / {END_MARKER} markers in {INDEX_FILE}.\n"
            "Add them around your Feast blog-card block first (see this script's docstring).",
            file=sys.stderr,
        )
        sys.exit(1)

    replacement = f"{START_MARKER}\n{cards_html}\n{END_MARKER}"
    new_html = pattern.sub(replacement, html, count=1)
    index_path.write_text(new_html, encoding="utf-8")


def main():
    posts = load_posts()
    cards_html = render_cards(posts)
    inject_into_index(cards_html)
    print(f"Rendered {len(posts)} Feast cards into {INDEX_FILE}")


if __name__ == "__main__":
    main()
