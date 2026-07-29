# Bringing the Feast RSS Kit into `sitefiles`

This folder is ready to drop straight into your existing `librarymonster/sitefiles`
repo alongside the changelog pipeline you already have. It adds a **second,
independent** GitHub Actions workflow that:

1. Regenerates the Feast cards on your homepage from `data/feast.yml`
2. Regenerates `feed.xml` (a real RSS feed for the Feast section) from the same file
3. Commits both files if anything changed
4. Deploys just `index.html` and `feed.xml` to Neocities — using the exact same
   `bcomnes/deploy-to-neocities@v3` action and `NEOCITIES_API_TOKEN` secret your
   `marss-neocities.yml` workflow already uses, so **no new secret setup needed**.

It runs completely separately from `marss-neocities.yml` — different trigger paths,
different files touched — so the two won't race or interfere with each other.

## What's in this folder

```
index.html                          <- your homepage, with the 51 hand-coded
                                        Feast cards replaced by two markers
data/feast.yml                      <- all 51 Feast posts as structured data
templates/feast_card.html.j2        <- the HTML template used to render each card
scripts/build_site.py               <- regenerates the Feast cards in index.html
scripts/build_feed.py               <- regenerates feed.xml
scripts/migrate_html_to_yaml.py     <- the one-time script that produced feast.yml
                                        (already run — you don't need to run it again)
requirements.txt                    <- Python deps for the two build scripts
.github/workflows/feast-neocities.yml
feed.xml                            <- a freshly-built sample, so you can see the
                                        output before it ever touches your repo
```

## Step 1 — Add the files to your repo

```bash
git clone https://github.com/librarymonster/sitefiles.git
cd sitefiles
```

Copy in the new pieces (leave `changelog.md`, `package.json`, `plans.txt`, and
`.github/workflows/marss-neocities.yml` exactly as they are):

```bash
cp -r /path/to/this/folder/data .
cp -r /path/to/this/folder/templates .
cp /path/to/this/folder/scripts/build_site.py scripts/build_site.py
cp /path/to/this/folder/scripts/build_feed.py scripts/build_feed.py
cp /path/to/this/folder/scripts/migrate_html_to_yaml.py scripts/migrate_html_to_yaml.py
cp /path/to/this/folder/requirements.txt .
cp /path/to/this/folder/.github/workflows/feast-neocities.yml .github/workflows/
cp /path/to/this/folder/index.html .          # first time index.html enters this repo
```

(`scripts/` doesn't exist yet in `sitefiles`, so the `cp` commands above will create it.)

## Step 2 — Commit and push

```bash
git add .
git commit -m "Add Feast RSS feed pipeline alongside the changelog feed"
git push
```

That's it — pushing to `main` triggers `feast-neocities.yml` immediately (it also
runs daily at 8am Central as a safety net, and you can always trigger it by hand
from the Actions tab).

## Step 3 — Watch it run and check the live site

Open the **Actions** tab on GitHub, watch the "Build Feast feed and homepage,
deploy to Neocities" run go green, then check:

- [https://monsterbyte.lol/](https://monsterbyte.lol/) — Feast section should look the same, plus a few small fixes (see below)
- [https://monsterbyte.lol/feed.xml](https://monsterbyte.lol/feed.xml) — your new RSS feed

## Important: index.html becomes git-managed from here on

Since this workflow both reads *and rewrites* `index.html`, **git is now the
source of truth for your homepage** — not the Neocities web editor. If you edit
`index.html` directly on Neocities going forward, that change will get
overwritten the next time this workflow runs (daily, or on any push touching
`data/feast.yml`). Make homepage edits in the repo and push them instead.

Everything outside the Feast section is untouched — header, sidebar, Snacks
panel, other page sections, all your other Neocities files. The deploy step
only ever pushes `index.html` and `feed.xml`, nothing else gets touched or removed.

## A few things this fixes along the way

While migrating your 51 existing posts into `data/feast.yml`, I found and fixed
three small pre-existing bugs in your live HTML that were affecting content
(not just cosmetic — worth knowing about):

1. **"My Tarot Collection on Display"** — a typo (`lol./p>` instead of `lol.</p>`)
   was merging the card's description with the "Visit the Cauldron" read-more
   text into one garbled sentence. Cleaned up.
2. **"New Webpage: The Colophon"** — a mismatched closing tag (`<h3>...</h2>`)
   was causing the subtitle and description to run together. Cleaned up.
3. **"Vaporwave Trauma.exe"** — its Etsy link was missing the opening quote
   in the HTML (`href=https://...">`), which appended a stray `"` onto the
   URL and likely broke the link for visitors. Fixed.

Everything else — all 51 titles, links, dates (including the ones that show as
ranges like "July & August, 2024"), tags, and custom image cropping — round-trips
byte-for-byte equivalent through the new pipeline.

## Adding a new Feast post from now on

1. Open `data/feast.yml` and add a new entry at the **top** of the list (newest first):

```yaml
- title: Your New Post Title
  link: /post/your-post.html          # or an external URL (Etsy, AO3, MakerTube, etc.)
  date: 2026-07-29
  subtitle: An optional subtitle       # omit this line if there isn't one
  summary: A short description of the post.
  image: /post/your-image.webp         # omit if there's no image
  image_alt: Alt text for the image    # omit if there's no image
  tags:
    - Tag One
    - Tag Two
```

2. Commit and push. The workflow rebuilds the homepage and the feed, and deploys
   both automatically. If a post genuinely has no fixed date, use `date_raw:
   "Winter 2024"` instead of `date:` and that text will display as-is (it just
   won't get a `pubDate` in the RSS feed).

## Field reference

| Field | Required? | Notes |
|---|---|---|
| `title` | yes | Card heading text |
| `link` | yes* | *Required for the post to appear in feed.xml; optional for the homepage card |
| `date` | no | ISO format `YYYY-MM-DD`; renders as "Month D, YYYY" |
| `date_raw` | no | Freeform fallback text if there's no exact date (e.g. "Summer 2024") |
| `subtitle` | no | Renders as the `<h3>` under the title |
| `summary` | yes | The card's description paragraph |
| `image` | no | Path or URL for the background image |
| `image_extra_style` | no | Extra CSS like `background-position`/`background-size` for custom cropping |
| `image_alt` | no | Alt text for the image (used as `aria-label`) |
| `tags` | no | List of tag strings |

## Validating the feed

Once deployed, you can sanity-check the feed at the
[W3C Feed Validator](https://validator.w3.org/feed/check.cgi?url=https%3A%2F%2Fmonsterbyte.lol%2Ffeed.xml).
