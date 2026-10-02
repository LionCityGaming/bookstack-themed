#!/usr/bin/env python3
"""Draw the images: page banners and card thumbnails (pages.csv), book/shelf heroes and covers (books.csv).

Each one is a small HTML page screenshotted by a headless browser, so the design lives in plain CSS
below. PNGs go to out/.

  python3 render.py                          # everything
  python3 render.py 12 books/networking      # only these rows
  python3 render.py --gotenberg http://localhost:3000   # use a Gotenberg container instead of a local browser

Browser: Chrome, Chromium or Edge, found automatically or set with CHROME=/path/to/browser.
Icons: any Lucide icon name (https://lucide.dev/icons), downloaded once into icons/. Use img:path/to/logo.png
for your own image instead.
Fonts: put SpaceGrotesk-700.woff2 and PlusJakartaSans-500.woff2 in fonts/ to embed them; otherwise
the page loads them from Google Fonts while rendering.
"""
import base64, os, re, shutil, subprocess, sys, tempfile, time, urllib.request
from common import HERE, _multipart, books, pages

LUCIDE = "https://unpkg.com/lucide-static@1.50.0/icons/{}.svg"
OUT = os.path.join(HERE, "out")
ICONS = os.path.join(HERE, "icons")
FONTS = os.path.join(HERE, "fonts")


# ---------- icons and fonts ----------

def icon(name, size, stroke, opacity=1.0):
    if name.startswith("img:"):
        path = os.path.join(HERE, name[4:])
        mime = "image/svg+xml" if path.endswith(".svg") else "image/png"
        data = base64.b64encode(open(path, "rb").read()).decode()
        look = "" if opacity == 1 else f"opacity:{opacity * 1.4};filter:grayscale(1) brightness(2);"
        px = int(size * 1.45)
        return f'<img src="data:{mime};base64,{data}" style="width:{px}px;height:{px}px;display:block;{look}">'
    path = os.path.join(ICONS, f"{name}.svg")
    if not os.path.exists(path):
        os.makedirs(ICONS, exist_ok=True)
        try:
            svg = urllib.request.urlopen(LUCIDE.format(name), timeout=30).read().decode()
        except Exception as e:
            raise SystemExit(f"Could not download Lucide icon '{name}' ({e}). Check the name at https://lucide.dev/icons")
        open(path, "w", encoding="utf8").write(svg)
    svg = open(path, encoding="utf8").read()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r'width="24"', f'width="{size}"', svg, count=1)
    svg = re.sub(r'height="24"', f'height="{size}"', svg, count=1)
    svg = svg.replace('stroke="currentColor"', f'stroke="white" stroke-opacity="{opacity}"')
    svg = svg.replace('fill="currentColor"', f'fill="white" fill-opacity="{opacity}"')
    return svg.replace('stroke-width="2"', f'stroke-width="{stroke}"')


def font_css():
    files = {"Space Grotesk": ("SpaceGrotesk-700.woff2", 700), "Plus Jakarta Sans": ("PlusJakartaSans-500.woff2", 500)}
    if all(os.path.exists(os.path.join(FONTS, f)) for f, _ in files.values()):
        out = ""
        for family, (f, weight) in files.items():
            data = base64.b64encode(open(os.path.join(FONTS, f), "rb").read()).decode()
            out += f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}\n"
        return out
    return "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=Plus+Jakarta+Sans:wght@500&display=block');\n"


# ---------- designs ----------

BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:'Plus Jakarta Sans',sans-serif;background:transparent}}
.card{{position:absolute;inset:0;border-radius:{radius}px;overflow:hidden;background:linear-gradient({angle}deg,{c1} 0%,{c2} 100%)}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.10) 1.2px,transparent 1.2px);background-size:{dot}px {dot}px}}
.mark{{position:absolute;{mark};transform:rotate(-12deg)}}
.badge{{border-radius:{br}px;background:rgba(255,255,255,.12);border:2px solid rgba(255,255,255,.22);
  display:flex;align-items:center;justify-content:center;box-shadow:0 16px 40px rgba(0,0,0,.35)}}
{extra}</style></head><body><div class="card"><div class="dots"></div>
<div class="mark">{big}</div>
{body}</div></body></html>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def banner(ic, c1, c2, title, subtitle):
    """1600x300 with title and subtitle: the top of each page, and the hero on book/shelf pages."""
    W, H = 1600, 300
    # sized so the subtitle is still readable when the banner is shown ~600px wide
    tsize = 84 if len(title) <= 18 else max(46, int(84 * 18 / len(title)))
    ssize = 42 if len(subtitle) <= 46 else max(32, int(42 * 46 / len(subtitle)))
    ssize = min(ssize, max(30, int(tsize * 0.62)))  # the title always leads
    extra = (f".row{{position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);display:flex;align-items:center;gap:44px}}\n"
             f".badge{{flex:none;width:150px;height:150px}}\n"
             f"h1{{margin:0;color:#fff;font-family:'Space Grotesk',sans-serif;font-size:{tsize}px;font-weight:700;letter-spacing:-1.5px;line-height:1}}\n"
             f"p{{margin:16px 0 0;color:rgba(255,255,255,.86);font-size:{ssize}px;font-weight:500;line-height:1.15}}\n")
    body = f'<div class="row"><div class="badge">{icon(ic, 86, 1.7)}</div><div><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div></div>'
    return W, H, BASE.format(fonts=font_css(), W=W, H=H, radius=28, angle=120, c1=c1, c2=c2, dot=22, br=36,
                             mark="right:40px;top:-60px", big=icon(ic, 420, 1.2, 0.08), extra=extra, body=body)


def thumb(ic, c1, c2):
    """520x200, icon only: the card image next to each page in a book's contents."""
    W, H = 520, 200
    extra = ".badge{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:118px;height:118px}\n"
    return W, H, BASE.format(fonts="", W=W, H=H, radius=22, angle=120, c1=c1, c2=c2, dot=18, br=30,
                             mark="right:-40px;top:-50px", big=icon(ic, 300, 1.2, 0.08), extra=extra,
                             body=f'<div class="badge">{icon(ic, 66, 1.8)}</div>')


def cover(ic, c1, c2):
    """880x500, icon only, square corners: the book/shelf cover BookStack shows in its grid view."""
    W, H = 880, 500
    extra = ".badge{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:230px;height:230px}\n"
    return W, H, BASE.format(fonts="", W=W, H=H, radius=0, angle=135, c1=c1, c2=c2, dot=22, br=52,
                             mark="right:-70px;bottom:-90px", big=icon(ic, 420, 1.2, 0.08), extra=extra,
                             body=f'<div class="badge">{icon(ic, 132, 1.6)}</div>')


# ---------- screenshotting ----------

def find_browser():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome"):
        if shutil.which(name):
            return shutil.which(name)
    for path in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 "/Applications/Chromium.app/Contents/MacOS/Chromium",
                 "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                 r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                 r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(path):
            return path
    raise SystemExit("No Chrome, Chromium or Edge found. Set CHROME=/path/to/browser, or use --gotenberg URL.")


def shot_browser(browser, W, H, page, png):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "page.html")
        open(src, "w", encoding="utf8").write(page)
        if os.path.exists(png):
            os.remove(png)
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        f"--user-data-dir={os.path.join(tmp, 'profile')}", "--force-device-scale-factor=1",
                        "--default-background-color=00000000", "--virtual-time-budget=3000",
                        f"--window-size={W},{H}", f"--screenshot={png}", "file:///" + src.replace("\\", "/").lstrip("/")],
                       check=True, capture_output=True, timeout=120)
        for _ in range(60):  # on Windows the launcher can exit before the file is written
            if os.path.exists(png) and os.path.getsize(png) > 0:
                return
            time.sleep(0.5)
        raise SystemExit(f"The browser did not write {png}")


def shot_gotenberg(url, W, H, page, png):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "index.html")
        open(src, "w", encoding="utf8").write(page)
        body, ctype = _multipart({"width": W, "height": H, "clip": "true", "format": "png",
                                  "omitBackground": "true", "waitDelay": "1s"}, {"files": src})
        req = urllib.request.Request(url.rstrip("/") + "/forms/chromium/screenshot/html", body,
                                     headers={"Content-Type": ctype}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            open(png, "wb").write(r.read())


def main(argv):
    gotenberg = None
    if "--gotenberg" in argv:
        i = argv.index("--gotenberg")
        gotenberg = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    only = set(argv)
    jobs = []
    for pid, r in pages().items():
        if not only or pid in only:
            jobs.append((f"banner-p{pid}", banner(r["icon"], r["from"], r["to"], r["title"], r["subtitle"])))
            jobs.append((f"thumb-p{pid}", thumb(r["icon"], r["from"], r["to"])))
    for target, r in books().items():
        if not only or target in only:
            name = target.replace("/", "-")
            jobs.append((f"hero-{name}", banner(r["icon"], r["from"], r["to"], r["title"], r["subtitle"])))
            jobs.append((f"cover-{name}", cover(r["icon"], r["from"], r["to"])))
    if not jobs:
        raise SystemExit("Nothing to render: check pages.csv / books.csv (and the IDs you passed)")
    os.makedirs(OUT, exist_ok=True)
    browser = None if gotenberg else find_browser()
    for name, (W, H, page) in jobs:
        png = os.path.join(OUT, f"{name}.png")
        if gotenberg:
            shot_gotenberg(gotenberg, W, H, page, png)
        else:
            shot_browser(browser, W, H, page, png)
        print(f"{name}.png  {W}x{H}  {os.path.getsize(png) // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
