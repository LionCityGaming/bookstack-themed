# bookstack-themed

A nicer look for a normal BookStack install. There's no fork and no theme to keep updated: it's one block of
CSS/JS you paste into BookStack's settings, plus a few optional Python scripts for the banner images.

![Example page banner](docs/preview/banner-p11.png)

<img src="docs/preview/hero-books-home.png" width="49%"> <img src="docs/preview/cover-books-operations.png" width="24%"> <img src="docs/preview/thumb-p14.png" width="24%">

## What you get

- **Every book has its own colour.** The header, links and highlights change to match the book you're in.
- **Banners at the top of each page**, a hero banner on each book and shelf, and matching covers.
- **Book contents as cards**, each page with a small thumbnail and a one-line description.
- **Nicer tables**: rounded, coloured header rows, striped rows, and pills for things like `OK`, `Warning`, `Failed`, `High`, `Fixed`.
- **Wider layout on big screens.** BookStack stops at about 840px of text; this lets pages use the space on wide and ultrawide monitors.
- Smaller touches: pill breadcrumbs, code blocks that look like little windows, a reading progress bar, a back-to-top button, and a dark login page.

## Three levels

You can stop after any of them.

### 1. Just the CSS (5 minutes, no scripts needed)

1. Edit `books.csv`: one line per book or shelf, using the slug from its URL (`/books/networking` → `books/networking`) and the colours you want.
2. Run `python3 build_head.py`. It writes `head.html`.
3. In BookStack go to **Settings › Customization › Custom HTML Head Content**, paste in all of `head.html`, and save.

This gives you the colours, layout, tables, cards and everything else except the images. Python 3.8+ only, nothing to install.

### 2. Banners, covers and thumbnails

1. `cp .env.example .env` and fill in your BookStack URL and an API token. Create the token on your BookStack profile under API Tokens; your role needs the "Access System API" permission.
2. Edit `pages.csv`: one line per page that should get a banner. `python3 publish.py --list` shows page IDs.
   Icons are [Lucide](https://lucide.dev/icons) names, or `img:logo.png` for your own image.
3. `python3 render.py` draws everything into `out/`. It needs Chrome, Chromium or Edge installed. If it can't find one, set `CHROME=/path/to/browser`.
   Running Gotenberg in Docker already? Use `python3 render.py --gotenberg http://gotenberg:3000` instead.
4. `python3 upload.py` uploads them and saves where they went in `state.json`.
5. Run `python3 build_head.py` again and paste the new `head.html` (it now knows the thumbnail and hero images).

To change one banner later: edit its line, then `python3 render.py 12 && python3 upload.py 12`. The URL stays the same,
so nothing else needs updating.

Fonts: banners use Space Grotesk and Plus Jakarta Sans. With internet access they load from Google Fonts while
rendering. To work offline, put `SpaceGrotesk-700.woff2` and `PlusJakartaSans-500.woff2` in `fonts/`.

### 3. Pages written as HTML files

This is how my own pages get their coloured headings and tables. Write the page as a plain HTML file
(see `examples/page.html`), then:

```
python3 publish.py 12 my-page.html
```

It adds the banner, coloured `h2`/`h3` headings, table header colours, padding, striped rows and status pills,
then replaces the page in BookStack. Old versions stay in the page's revision history as usual.

Keep the HTML file as the source and always publish from it. Don't fetch a page back from BookStack and run it
through again: BookStack adds its own IDs and rewrites styles, so you'd get a second banner.

`examples/dashboard.html` is the start page with a tile per book. Set it as the homepage under
**Settings › Customization › Application Homepage**.

## Good to know

- BookStack strips `border-radius`, `box-shadow` and gradients from page HTML. That's why banners are images with
  the rounded corners baked in, and why the pills get their rounded look from the head CSS (BookStack keeps `class`).
- The custom head isn't applied on BookStack's settings pages. That's BookStack being safe, so you can always fix
  a broken paste.
- Built and used on BookStack v26.09. It only uses BookStack's own class names, so a big UI change in a future
  version could need a tweak.
- To undo everything, delete the block from Custom HTML Head Content.

## Licence

MIT. Icons are [Lucide](https://lucide.dev) (ISC), downloaded when you render, not included here.
Fonts are from Google Fonts (OFL).
