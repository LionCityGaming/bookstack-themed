#!/usr/bin/env python3
"""Write head.html: the CSS and JavaScript to paste into BookStack under
Settings › Customization › Custom HTML Head Content.

It reads books.csv (each book's colours), pages.csv and state.json (thumbnail and hero image URLs,
once upload.py has run), and the optional login text in .env. Re-run it and paste again whenever
those change. Nothing is sent anywhere; it only writes the file.

  python3 build_head.py
"""
import json, os
from common import HERE, books, load_state, pages, settings, versioned

cfg = settings()
state = load_state()

# "books/<slug>" or "shelves/<slug>" -> [accent, deep, bright]
colours = {t: [r["from"], r["to"], r["bright"] or r["from"]] for t, r in books().items()}
# page id -> card thumbnail + the banner subtitle as the card's description
thumbs = {pid: {"t": versioned(e, "thumb"), "d": pages().get(pid, {}).get("subtitle", "")}
          for pid, e in state["pages"].items() if e.get("thumb")}
heroes = {t: versioned(e, "hero") for t, e in state["books"].items() if e.get("hero")}
login = {"title": cfg.get("LOGIN_TITLE", ""), "sub": cfg.get("LOGIN_SUBTITLE", ""), "foot": cfg.get("LOGIN_FOOTER", "")}
fonts = cfg.get("FONTS_CSS") or ("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600"
                                 "&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap")

CSS = """
/* ---------- Fonts ---------- */
body {
  --font-body: 'Plus Jakarta Sans', system-ui, sans-serif;
  --font-heading: 'Space Grotesk', system-ui, sans-serif;
  --font-code: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 1rem;
}
h1, h2, h3, h4, .logo-text { font-family: var(--font-heading); letter-spacing: -.01em; }
main h1 { font-weight: 700; }
html { scroll-behavior: smooth; }
::selection { background: color-mix(in srgb, var(--hl-accent, #2563eb) 35%, transparent); }

/* ---------- Header: follows the current book's colour ---------- */
header#header { background: linear-gradient(100deg, #0f172a 0%, var(--hl-deep, #1e3a8a) 55%, var(--hl-accent, #0f766e) 100%) !important;
  box-shadow: 0 4px 24px rgba(0,0,0,.28); border-bottom: 1px solid rgba(255,255,255,.08); transition: background .3s ease; }
header#header .logo-text { font-weight: 700; letter-spacing: .02em; }
header#header .search-box input { border-radius: 999px; background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.2); color: #fff; }
header#header .search-box input::placeholder { color: rgba(255,255,255,.7); }

/* ---------- Background: soft glows on the root element, fixed, so they cover every scroll position ---------- */
html:not(.dark-mode) { background:
  radial-gradient(1200px 600px at 5% -10%, color-mix(in srgb, var(--hl-accent, #2563eb) 10%, transparent), transparent 60%),
  radial-gradient(1000px 500px at 105% 5%, rgba(13,148,136,.09), transparent 60%), #f3f5fa;
  background-attachment: fixed; min-height: 100%; }
html.dark-mode { background:
  radial-gradient(1200px 600px at 5% -10%, color-mix(in srgb, var(--hl-accent, #2563eb) 18%, transparent), transparent 60%),
  radial-gradient(1000px 500px at 105% 5%, rgba(13,148,136,.13), transparent 60%), #0b1020;
  background-attachment: fixed; min-height: 100%; }
html body { background: transparent !important; }

/* ---------- Cards, grids, lists ---------- */
.card { border-radius: 16px !important; border: 1px solid rgba(127,127,127,.12);
  box-shadow: 0 8px 30px rgba(15,23,42,.08) !important; }
html.dark-mode .card { background: #151b2e !important; box-shadow: 0 10px 34px rgba(0,0,0,.45) !important; }
.grid-card { border-radius: 16px !important; overflow: hidden; border: 1px solid rgba(127,127,127,.14);
  transition: transform .18s ease, box-shadow .18s ease; }
html.dark-mode .grid-card { background: #151b2e; }
.grid-card:hover { transform: translateY(-4px); box-shadow: 0 16px 36px rgba(0,0,0,.28) !important; }
.grid-card .featured-image-container { transition: transform .45s ease; }
.grid-card:hover .featured-image-container { transform: scale(1.05); }
.grid-card h2 { font-family: var(--font-heading); font-weight: 600; }
.entity-list-item { border-radius: 10px; transition: background .15s ease, transform .15s ease; }
.entity-list > .entity-list-item:hover { transform: translateX(3px); }
.entity-list-item-image { border-radius: 10px; }
.button { border-radius: 999px !important; }
.tag-item { border-radius: 10px !important; overflow: hidden; }  /* not a full pill: long two-line tags turn into circles */

/* ---------- Sign-in pages (login, two-factor, password reset) ---------- */
.hl-auth .card.content-wrap { background-image: radial-gradient(420px 220px at 50% -40px, rgba(29,78,216,.22), transparent 70%) !important; }
.hl-auth input[type="text"], .hl-auth input[type="password"], .hl-auth input[type="email"] { border-radius: 10px;
  padding: 10px 14px; font-size: 1rem; letter-spacing: .04em; }
.hl-auth .button:not(.outline) { background: linear-gradient(100deg, #1e3a8a, #1d4ed8 50%, #0f766e) !important; border: 0 !important;
  color: #fff !important; padding: 8px 22px !important; box-shadow: 0 8px 20px rgba(29,78,216,.35); }
.hl-login .container.very-small { max-width: 460px; }
.hl-login .card.content-wrap { position: relative; overflow: hidden; padding: 40px 36px 30px !important; }
.hl-login.hl-intro .card.content-wrap { text-align: center; }
.hl-login.hl-intro h1.list-heading { display: none; }
.hl-login-logo { display: block; width: 112px; height: 112px; margin: 0 auto 18px; border-radius: 50%; object-fit: cover;
  box-shadow: 0 0 0 6px rgba(255,255,255,.08), 0 12px 36px rgba(29,78,216,.45); animation: hlPulse 4s ease-in-out infinite; }
@keyframes hlPulse { 50% { box-shadow: 0 0 0 10px rgba(255,255,255,.04), 0 12px 48px rgba(15,118,110,.55); } }
.hl-login-title { font-family: var(--font-heading); font-size: 2rem; font-weight: 700; margin: 0; line-height: 1.15;
  background: linear-gradient(90deg, #60a5fa, #2dd4bf); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hl-login-sub { opacity: .75; margin: 8px 0 6px; }
.hl-login-foot { margin: 18px 0 0; font-size: .8rem; opacity: .6; }
.hl-login [id$="-login"].button { width: 100%; justify-content: center; padding: 12px 20px !important; font-size: 1rem; font-weight: 600; }
.hl-login [id$="-login"].button svg { fill: #fff !important; }

/* ---------- Breadcrumbs as pills ---------- */
.breadcrumbs .icon-list-item, .breadcrumbs .dropdown-search-toggle-breadcrumb { padding: 4px 12px !important;
  border-radius: 999px; background: rgba(127,127,127,.10); border: 1px solid rgba(127,127,127,.16);
  transition: background .15s ease; }
.breadcrumbs .icon-list-item:hover { background: color-mix(in srgb, var(--hl-accent, #2563eb) 18%, transparent); }

/* ---------- Sidebar navigation ---------- */
.book-tree .entity-list-item.selected { background: color-mix(in srgb, var(--hl-accent, #2563eb) 20%, transparent) !important;
  border-radius: 999px; font-weight: 600; }
.book-tree .entity-list-item.selected .entity-list-item-name { color: var(--color-primary); }
.sidebar-page-nav .current-heading, .sidebar-page-nav .current-heading a { color: var(--color-primary) !important; font-weight: 700; }
.sidebar-page-nav .current-heading .sidebar-page-nav-bullet { background: var(--color-primary) !important;
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary) 25%, transparent); }
.sidebar-page-nav a { transition: color .15s ease; }

/* ---------- Page content: tables ---------- */
.page-content table { border-collapse: separate !important; border-spacing: 0; border: 1px solid rgba(127,127,127,.22) !important;
  border-radius: 12px; }
.page-content table:not([style*="nowrap"]) { overflow: hidden; }
.page-content table td, .page-content table th { border: 0 !important; border-bottom: 1px solid rgba(127,127,127,.14) !important; }
.page-content table tr:last-child td { border-bottom: 0 !important; }
.page-content table tbody tr { transition: background .12s ease; }
.page-content table tbody tr:hover { background: color-mix(in srgb, var(--hl-accent, #2563eb) 12%, transparent) !important; }
.page-content .hl-badge { border-radius: 999px; letter-spacing: .02em; box-shadow: 0 2px 8px rgba(0,0,0,.18); white-space: nowrap; }
.page-content a.hl-badge:hover { filter: brightness(1.2); }

/* ---------- Page content: callouts ---------- */
.page-content .callout { border-radius: 12px; border-left-width: 4px; }
.page-content .callout.info { background: linear-gradient(90deg, rgba(2,136,209,.18), rgba(2,136,209,.04)); }
.page-content .callout.success { background: linear-gradient(90deg, rgba(22,163,74,.18), rgba(22,163,74,.04)); }
.page-content .callout.warning { background: linear-gradient(90deg, rgba(217,119,6,.20), rgba(217,119,6,.04)); }
.page-content .callout.danger { background: linear-gradient(90deg, rgba(220,38,38,.20), rgba(220,38,38,.04)); }

/* ---------- Page content: code blocks as little windows ---------- */
.page-content .cm-editor { position: relative; border-radius: 12px; overflow: hidden; padding-top: 32px;
  border: 1px solid rgba(127,127,127,.22); box-shadow: 0 8px 22px rgba(0,0,0,.18); }
.page-content .cm-editor::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 32px;
  background: rgba(127,127,127,.14); border-bottom: 1px solid rgba(127,127,127,.18); z-index: 4; }
.page-content .cm-editor::before { content: ""; position: absolute; top: 11px; left: 14px; width: 10px; height: 10px;
  border-radius: 50%; background: #ff5f57; box-shadow: 16px 0 #febc2e, 32px 0 #28c840; z-index: 5; }
.page-content .cm-copy-button { border-radius: 999px !important; z-index: 6; }
.page-content pre { border-radius: 12px; border: 1px solid rgba(127,127,127,.18); }
.page-content code { border-radius: 6px; }

/* ---------- Pages with a banner: the banner replaces the page title ---------- */
.page-content:has(img[src*="/banner-"]) #bkmrk-page-title { display: none; }
.page-content p:has(> img[src*="/banner-"]) { margin-top: 0; }
.page-content img[src*="/banner-"] { display: block; }

/* ---------- Book and shelf pages: the hero banner replaces the plain title ---------- */
.hl-hero { display: block; width: 100%; height: auto; margin: -6px 0 22px; filter: drop-shadow(0 10px 22px rgba(0,0,0,.3)); }
.hl-title-hidden { display: none !important; }
.book-content > .text-muted:first-child { border-left: 4px solid var(--hl-accent, currentColor); padding: 10px 16px;
  background: rgba(127,127,127,.08); border-radius: 8px; margin-bottom: 20px; }

/* ---------- Book contents: pages as cards with a thumbnail ---------- */
.book-contents a.entity-list-item.hl-card { display: grid; grid-template-columns: 200px 1fr; gap: 18px;
  align-items: center; padding: 10px; margin: 12px 0; border: 0; border-radius: 12px;
  background: rgba(127,127,127,.07); transition: transform .15s ease, box-shadow .15s ease; }
.book-contents a.entity-list-item.hl-card:hover { transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(0,0,0,.28); background: rgba(127,127,127,.12); }
.book-contents a.entity-list-item.hl-card > .icon { display: none; }
.book-contents a.entity-list-item.hl-card .entity-list-item-name { margin-bottom: 2px; }
.book-contents a.entity-list-item.hl-card .entity-item-snippet p { margin: 0; -webkit-line-clamp: unset; display: block; overflow: visible; }
.hl-thumb { width: 200px; height: 77px; object-fit: cover; border-radius: 10px; }
@media (max-width: 600px) {
  .book-contents a.entity-list-item.hl-card { grid-template-columns: 1fr; }
  .hl-thumb { width: 100%; height: 64px; }
}

/* ---------- Layout width: scale with the screen, laptop to ultrawide ---------- */
/* BookStack caps the middle column at 940px and page text at 840px. Above 1400px the side panels keep
   260-360px and the centre takes the rest, up to 1800px. */
@media screen and (min-width: 1401px) {
  .tri-layout-sides-content, .tri-layout-container {
    grid-template-columns: minmax(260px, 360px) minmax(0, 1fr) minmax(260px, 360px);
  }
  .tri-layout-middle-contents { max-width: 1800px; }
  .page-content, .title-input.page-title input[type=text] { max-width: 100%; }
}
.content-wrap.card { min-height: 0; }

/* ---------- Dashboard page: tiles and columns (see examples/dashboard.html) ---------- */
.page-content .hl-tilegrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(max(560px, 45%), 1fr)); gap: 8px 20px; margin-bottom: 8px; }
.page-content .hl-tile img { display: block; transition: transform .18s ease, filter .18s ease; filter: drop-shadow(0 8px 16px rgba(0,0,0,.28)); }
.page-content .hl-tile a:hover img { transform: translateY(-3px); filter: drop-shadow(0 14px 24px rgba(0,0,0,.38)) brightness(1.08); }
.page-content .hl-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(max(480px, 45%), 1fr)); gap: 0 28px; align-items: start; }
.page-content .hl-col > h2:first-child { margin-top: 1em; }
@media (max-width: 600px) {
  .page-content .hl-tilegrid, .page-content .hl-cols { grid-template-columns: 1fr; }
}

/* ---------- Reading progress bar and back-to-top button ---------- */
#hl-progress { position: fixed; top: 0; left: 0; height: 3px; width: 0; z-index: 10000; pointer-events: none;
  background: linear-gradient(90deg, var(--hl-bright, #60a5fa), var(--hl-accent, #0f766e));
  box-shadow: 0 0 10px var(--hl-bright, #60a5fa); transition: width .08s linear; }
#hl-top { position: fixed; right: 24px; bottom: 24px; width: 46px; height: 46px; border-radius: 50%; z-index: 9999;
  border: 1px solid rgba(255,255,255,.25); color: #fff; font-size: 20px; cursor: pointer;
  background: linear-gradient(135deg, var(--hl-accent, #1d4ed8), var(--hl-deep, #0f172a));
  box-shadow: 0 8px 22px rgba(0,0,0,.35); opacity: 0; transform: translateY(12px); pointer-events: none;
  transition: opacity .2s ease, transform .2s ease; }
#hl-top.show { opacity: 1; transform: none; pointer-events: auto; }
#hl-top:hover { filter: brightness(1.15); }

/* ---------- Motion ---------- */
@keyframes hlIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
main.content-wrap, .tri-layout-left-contents, .tri-layout-right-contents { animation: hlIn .35s ease both; }
.grid-card { animation: hlIn .4s ease both; }
.grid-card:nth-child(2) { animation-delay: .04s; } .grid-card:nth-child(3) { animation-delay: .08s; }
.grid-card:nth-child(4) { animation-delay: .12s; } .grid-card:nth-child(n+5) { animation-delay: .16s; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
@media print { #hl-progress, #hl-top { display: none !important; } }
"""

JS = """
(() => {
  const COLOURS = %s, THUMBS = %s, HEROES = %s, LOGIN = %s;
  const root = document.documentElement;
  // Book/shelf colour: set before the page paints so the header and links already match
  const m = location.pathname.match(/^\\/(books|shelves)\\/([^/]+)/);
  const c = m && COLOURS[m[1] + "/" + m[2]];
  if (c) {
    const rgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)).join(",");
    const set = (k, v) => root.style.setProperty(k, v);
    set("--hl-accent", c[0]); set("--hl-deep", c[1]); set("--hl-bright", c[2]);
    const apply = () => {
      const p = root.classList.contains("dark-mode") ? c[2] : c[0];
      set("--color-primary", p); set("--color-link", p); set("--color-primary-light", `rgba(${rgb(p)},0.15)`);
    };
    apply();
    new MutationObserver(apply).observe(root, { attributes: true, attributeFilter: ["class"] });
  }
  // Sign-in pages come before anyone's dark-mode preference is known, so they are always dark
  if (/^\\/(login|mfa|register|password)(\\/|$)/.test(location.pathname)) root.classList.add("hl-auth", "dark-mode");
  const onLogin = location.pathname === "/login";
  if (onLogin) root.classList.add("hl-login");
  if (onLogin && LOGIN.title) root.classList.add("hl-intro");

  document.addEventListener("DOMContentLoaded", () => {
    if (onLogin && LOGIN.title) {
      const card = document.querySelector(".container.very-small .card.content-wrap");
      if (card) {
        const intro = document.createElement("div");
        const logo = document.querySelector("#header img");
        if (logo) {
          const img = document.createElement("img");
          img.src = logo.src; img.alt = ""; img.className = "hl-login-logo";
          intro.append(img);
        }
        const t = document.createElement("p"); t.className = "hl-login-title"; t.textContent = LOGIN.title;
        intro.append(t);
        if (LOGIN.sub) { const s = document.createElement("p"); s.className = "hl-login-sub"; s.textContent = LOGIN.sub; intro.append(s); }
        card.prepend(intro);
        if (LOGIN.foot) { const f = document.createElement("p"); f.className = "hl-login-foot"; f.textContent = LOGIN.foot; card.append(f); }
      }
    }
    // Book contents: each page with a thumbnail becomes a card
    document.querySelectorAll(".book-contents a.entity-list-item.page[data-entity-id]").forEach(a => {
      const t = THUMBS[a.dataset.entityId];
      if (!t) return;
      const img = document.createElement("img");
      img.src = t.t; img.alt = ""; img.className = "hl-thumb"; img.loading = "lazy";
      a.classList.add("hl-card");
      a.prepend(img);
      const snip = a.querySelector(".entity-item-snippet p");
      if (snip && t.d) snip.textContent = t.d;
    });
    // Book/shelf front page: the hero banner replaces the plain title
    const hm = location.pathname.match(/^\\/(books|shelves)\\/([^/]+)\\/?$/);
    const hero = hm && HEROES[hm[1] + "/" + hm[2]];
    const main = document.querySelector("main.content-wrap");
    const h1 = main && main.querySelector(":scope > h1");
    if (hero && h1) {
      const img = document.createElement("img");
      img.src = hero; img.alt = h1.textContent.trim(); img.className = "hl-hero";
      h1.before(img);
      h1.classList.add("hl-title-hidden");
    }
    // Reading progress bar (pages only) and back-to-top button
    const bar = document.createElement("div"); bar.id = "hl-progress";
    const top = document.createElement("button"); top.id = "hl-top"; top.type = "button";
    top.setAttribute("aria-label", "Back to top"); top.textContent = "\\u2191";
    top.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    const onPage = !!document.querySelector(".page-content");
    if (onPage) document.body.append(bar);
    document.body.append(top);
    const onScroll = () => {
      const el = document.scrollingElement || root;
      const max = el.scrollHeight - el.clientHeight;
      if (onPage) bar.style.width = (max > 0 ? (el.scrollTop / max) * 100 : 0) + "%%";
      top.classList.toggle("show", el.scrollTop > 600);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  });
})();
""" % (json.dumps(colours), json.dumps(thumbs), json.dumps(heroes), json.dumps(login))

head = (f'<!-- bookstack-themed -->\n<link rel="stylesheet" href="{fonts}">\n'
        f"<style>{CSS}</style>\n<script>{JS}</script>\n<!-- /bookstack-themed -->\n")
out = os.path.join(HERE, "head.html")
open(out, "w", encoding="utf8").write(head)
print(f"Wrote head.html ({len(head):,} characters): {len(colours)} book/shelf colours, {len(thumbs)} page thumbnails, "
      f"{len(heroes)} heroes.")
print("Paste all of it into Settings › Customization › Custom HTML Head Content, replacing any earlier copy, then Save.")
