#!/usr/bin/env python3
"""Upload what render.py drew, and remember where it went (state.json).

- Page banners and thumbnails go into that page's image gallery.
- Book and shelf covers are set as the book/shelf cover image.
- Heroes go into the gallery of the first page in that book (or in the shelf's first book);
  BookStack keeps every gallery image attached to some page.

Re-running replaces images in place (same URL) and bumps a version number so browsers fetch the new one.
Afterwards run build_head.py again and paste the new head, since it carries the thumbnail and hero URLs.

  python3 upload.py                      # everything in out/
  python3 upload.py 12 books/networking  # only these rows
"""
import os, sys
from common import API, HERE, books, load_state, pages, save_state, url_path

OUT = os.path.join(HERE, "out")


def gallery(api, png, image_id, page_id, name):
    if image_id:
        return api.call("POST", f"image-gallery/{image_id}", {"_method": "PUT", "name": name}, {"image": png})
    return api.call("POST", "image-gallery", {"type": "gallery", "uploaded_to": page_id, "name": name}, {"image": png})


def store(entry, key, d):
    if entry.get(key + "_id") != d["id"]:
        entry[key + "_v"] = 0
    entry[key + "_id"] = d["id"]
    entry[key] = url_path(d["url"])
    entry[key + "_v"] = entry.get(key + "_v", 0) + 1


def first_page(api, kind, item_id):
    if kind == "books":
        for c in api.call("GET", f"books/{item_id}").get("contents", []):
            if c.get("type") == "page":
                return c["id"]
            for p in c.get("pages", []):
                return p["id"]
        return None
    for b in api.call("GET", f"shelves/{item_id}").get("books", []):
        pid = first_page(api, "books", b["id"])
        if pid:
            return pid
    return None


def main(only):
    api = API()
    state = load_state()
    for pid, r in pages().items():
        if only and pid not in only:
            continue
        e = state["pages"].setdefault(pid, {})
        for key in ("banner", "thumb"):
            png = os.path.join(OUT, f"{key}-p{pid}.png")
            if os.path.exists(png):
                store(e, key, gallery(api, png, e.get(key + "_id"), pid, f'{r["title"]} {key}'))
        print(f"page {pid}: banner {e.get('banner_id')}, thumbnail {e.get('thumb_id')}")

    wanted = [t for t in books() if not only or t in only]
    ids = {}
    for kind in {t.split("/", 1)[0] for t in wanted}:
        ids.update({f'{kind}/{x["slug"]}': x["id"] for x in api.listing(kind)})
    for target in wanted:
        r = books()[target]
        kind = target.split("/", 1)[0]
        if target not in ids:
            print(f"{target}: not found in BookStack (check the slug in its URL), skipped")
            continue
        e = state["books"].setdefault(target, {})
        name = target.replace("/", "-")
        cover = os.path.join(OUT, f"cover-{name}.png")
        if os.path.exists(cover):
            api.call("POST", f"{kind}/{ids[target]}", {"_method": "PUT"}, {"image": cover})
        hero = os.path.join(OUT, f"hero-{name}.png")
        if os.path.exists(hero):
            page_id = e.get("hero_page") or first_page(api, kind, ids[target])
            if page_id:
                e["hero_page"] = page_id
                store(e, "hero", gallery(api, hero, e.get("hero_id"), page_id, f'{r["title"]} hero'))
            else:
                print(f"{target}: has no pages yet, so the hero has nowhere to live; add a page and re-run")
        print(f"{target}: cover set, hero {e.get('hero_id')}")
    save_state(state)
    print("Saved state.json. Now run build_head.py and paste head.html into BookStack.")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
