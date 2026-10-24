#!/usr/bin/env python3
"""Download the media of Intropix Instagram scraper results to local folders.

Usage: python3 save_media.py ITEMS_JSON OUT_DIR [--covers]

ITEMS_JSON is the dataset the actor returned (a JSON array, as printed by
`apify datasets get-items <id> --format json`). Works for posts, reels and
stories. Files land in OUT_DIR/<username>/ as <date>_<id>[_<slide>].<ext>,
and every item is appended once to OUT_DIR/<username>/items.jsonl, so running
it again on overlapping results downloads and records only what is new.

Standard library only. Instagram media links expire, so run this right after
the scrape.
"""

import json
import pathlib
import shutil
import sys
import urllib.request

EXT = {"video": "mp4", "image": "jpg"}


def media_entries(item):
    """(suffix, url, media_type) for each file of one item."""
    if item.get("media"):  # posts and reels: one entry per slide
        slides = item["media"]
        for m in slides:
            suffix = f"_{(m.get('slide_index') or 0) + 1}" if len(slides) > 1 else ""
            if m.get("media_url"):
                yield suffix, m["media_url"], m.get("media_type") or "image"
    elif item.get("media_url"):  # stories: one file per item
        yield "", item["media_url"], item.get("media_type") or "image"


def cover_entries(item):
    slides = item.get("media") or []
    for m in slides:
        if m.get("media_type") == "video" and m.get("cover_url"):
            slide = f"_{(m.get('slide_index') or 0) + 1}" if len(slides) > 1 else ""
            yield f"{slide}_cover", m["cover_url"], "image"


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    tmp = path.with_suffix(path.suffix + ".part")
    try:
        with urllib.request.urlopen(req, timeout=60) as r, tmp.open("wb") as f:
            shutil.copyfileobj(r, f)  # stream: a reel can be tens of MB
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    tmp.replace(path)


def load_seen(index):
    """Ids already in items.jsonl; a damaged line is skipped, not fatal."""
    seen = set()
    if index.exists():
        text = index.read_text(encoding="utf-8")
        if text and not text.endswith("\n"):  # cut short: end the line so the
            with index.open("a", encoding="utf-8") as f:  # next record stays whole
                f.write("\n")
        for line in text.splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue  # e.g. a half-written last line from an interrupted run
            if isinstance(rec, dict):
                seen.add(str(rec.get("post_pk") or rec.get("story_pk")))
    return seen


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    covers = "--covers" in sys.argv
    items = json.loads(pathlib.Path(args[0]).read_text(encoding="utf-8"))
    out = pathlib.Path(args[1])
    saved = skipped = failed = new_items = 0
    seen_by_index = {}  # items.jsonl path -> ids recorded, read once per run
    for item in items:
        item_id = item.get("post_pk") or item.get("story_pk")
        user = item.get("username")
        if not item_id or not user:
            continue  # not a result item
        folder = out / user
        folder.mkdir(parents=True, exist_ok=True)
        date = (item.get("taken_at") or "")[:10] or "undated"
        files = list(media_entries(item)) + (list(cover_entries(item)) if covers else [])
        for suffix, url, kind in files:
            path = folder / f"{date}_{item_id}{suffix}.{EXT.get(kind, 'jpg')}"
            if path.exists():
                skipped += 1
                continue
            try:
                download(url, path)
                saved += 1
            except Exception as e:  # keep going: one expired link must not stop the rest
                failed += 1
                print(f"failed {path.name}: {e}", file=sys.stderr)
        index = folder / "items.jsonl"
        if index not in seen_by_index:
            seen_by_index[index] = load_seen(index)
        seen = seen_by_index[index]
        if str(item_id) not in seen:
            with index.open("a", encoding="utf-8") as f:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
            seen.add(str(item_id))
            new_items += 1
    print(f"saved {saved} file(s), {skipped} already present, {failed} failed; "
          f"{new_items} new item(s) recorded under {out}")
    sys.exit(1 if failed and not saved else 0)


if __name__ == "__main__":
    main()
