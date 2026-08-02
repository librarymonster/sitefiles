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
