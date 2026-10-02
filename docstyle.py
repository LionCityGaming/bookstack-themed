"""Page styling, added at publish time so your page sources stay plain HTML.

apply(html, page_id) adds the page's banner at the top, a solid band on each h2 and a left bar on
each h3 in the page's colour, coloured table header rows, cell padding, striped rows and status
pills. Everything is inline styles, because BookStack keeps those; the few things it strips from page
HTML (border-radius, box-shadow, gradients) are handled by the custom head CSS instead, which
targets the hl-badge class (BookStack keeps class attributes).

Always run it on your source file, never on HTML fetched back from BookStack: BookStack adds ids
and rewrites styles, so a second pass would add a second banner and re-stripe the tables.
"""
import re
from common import load_state, pages, versioned

STRIPE = "rgba(127,127,127,.08)"
# a table cell that starts with one of these words becomes a coloured pill
BADGES = {"Critical": "#7f1d1d", "High": "#dc2626", "Medium": "#d97706", "Low": "#2563eb", "Info": "#64748b",
          "Fixed": "#16a34a", "Done": "#16a34a", "OK": "#16a34a", "Partly fixed": "#ca8a04",
          "In progress": "#7c3aed", "Open": "#d97706", "Warning": "#d97706", "Failed": "#dc2626",
          "Accepted": "#64748b", "No issue": "#0d9488"}
BADGE_STYLE = "display:inline-block;padding:1px 10px;background:{};color:#fff;font-weight:700;font-size:.85em;"
# the word must be the whole cell, or be followed by ':', '.', ' (' or ' by'
BADGE_RE = re.compile(r"<td>(" + "|".join(sorted(BADGES, key=len, reverse=True)) + r")(?=</td>|[:.]| \(| by )")


def _stripe(tbody):
    n = 0

    def row(m):
        nonlocal n
        n += 1
        return f'<tr style="background:{STRIPE};">' if n % 2 == 0 else m.group(0)
    return re.sub(r"<tr>", row, tbody)


def apply(html, page_id):
    page_id = str(page_id)
    row = pages().get(page_id)
    if not row:
        return html  # not in pages.csv: publish unstyled
    c, deep = row["from"], row["to"]
    banner = load_state()["pages"].get(page_id, {})
    if banner.get("banner"):
        img = f'<p><img src="{versioned(banner, "banner")}" alt="{row["title"]} banner" style="width:100%;height:auto;"></p>'
        banner_re = re.compile(r'<p><img src="[^"]*/banner-[^"]*"[^>]*></p>')
        html = banner_re.sub(img, html, count=1) if banner_re.search(html) else img + "\n\n" + html
    html = re.sub(r"<h2((?: id=\"[^\"]*\")?)>",
                  rf'<h2 style="border-left:6px solid {c};background:{deep};color:#fff;padding:8px 14px;"\1>', html)
    html = re.sub(r"<h3((?: id=\"[^\"]*\")?)>", rf'<h3 style="border-left:4px solid {c};padding-left:10px;"\1>', html)
    html = html.replace("<thead><tr>", f'<thead><tr style="background:{c};color:#fff;">')
    html = re.sub(r"<tr>(\s*<th)", rf'<tr style="background:{c};color:#fff;">\1', html)
    html = BADGE_RE.sub(lambda m: f'<td><span class="hl-badge" style="{BADGE_STYLE.format(BADGES[m.group(1)])}">'
                                  f"{m.group(1)}</span>", html)
    html = html.replace("<th>", '<th style="padding:8px 10px;">')
    html = html.replace("<td>", '<td style="padding:6px 10px;">')
    html = re.sub(r"<tbody>.*?</tbody>", lambda m: _stripe(m.group(0)), html, flags=re.S)
    return html


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        raise SystemExit("Preview the styled HTML: python3 docstyle.py <page_id> <file.html>")
    print(apply(open(sys.argv[2], encoding="utf8").read(), sys.argv[1]))
