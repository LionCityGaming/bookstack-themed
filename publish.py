#!/usr/bin/env python3
"""Publish pages you write as HTML files: style them (docstyle.py) and replace the page in BookStack.

  python3 publish.py --list                                 # page IDs, books and names
  python3 publish.py <page_id> <file.html> [<page_id> <file.html> ...]

The page must exist already: create it once in BookStack, then find its ID with --list.
Its old content stays in BookStack's revision history, as with any edit.
"""
import sys
import docstyle
from common import API

args = sys.argv[1:]
if args == ["--list"]:
    api = API()
    book_names = {b["id"]: b["name"] for b in api.listing("books")}
    for p in sorted(api.listing("pages"), key=lambda p: (book_names.get(p["book_id"], ""), p["name"])):
        print(f'{p["id"]:>6}  {book_names.get(p["book_id"], "?")} › {p["name"]}')
    sys.exit()
if not args or len(args) % 2:
    raise SystemExit(__doc__)
api = API()
for page_id, src in zip(args[0::2], args[1::2]):
    html = docstyle.apply(open(src, encoding="utf8").read(), page_id)
    d = api.call("PUT", f"pages/{page_id}", {"html": html})
    print(f"{page_id}: {d['name']} updated")
