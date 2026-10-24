---
name: save-instagram-posts
description: "Save or download Instagram posts (photos, carousels and reels) from a public business, creator or brand account, or from post links, as files plus JSON with captions, likes, comments, view counts and dates. Use when the user wants to download Instagram posts, back up an account's feed, export Instagram posts to JSON or CSV, save a post from its link, or get posts between two dates. No Instagram login needed; works on the free Apify plan."
---

# Save Instagram posts

Runs the Intropix **Instagram Posts & Reels Scraper** on Apify
(`intropix/instagram-posts-reels-scraper`) and saves what it returns: the
media files plus one JSON record per post.

## Rules

- Public **business, creator and brand accounts** only. If the user asks for a
  private person's account, say the scraper's terms do not allow it and stop.
  Private accounts are never readable.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not republish them as a dataset.

## 1. Build the input

| Field | Use |
|---|---|
| `usernames` | Account handles without `@`, e.g. `["nike"]`. |
| `postUrls` | Instead of or besides usernames: links like `https://www.instagram.com/p/<code>/` or `/reel/<code>/`. Every valid link is delivered. |
| `maxPosts` | How many of the newest posts to read. Default 10. One shared total for the whole run. |
| `maxPostsPerAccount` | Instead of `maxPosts`: up to this many of EACH account's newest posts. |
| `sinceDate`, `untilDate` | Optional `YYYY-MM-DD` (UTC) bounds. |
| `mediaType` | `any` (default), `image` or `video`. |

**Several accounts:** use `maxPostsPerAccount`, e.g.
`{"usernames": ["nike", "adidas"], "maxPostsPerAccount": 10}`. `maxPosts`
alone is one shared total spent in input order, so the first account can use
it all. A run holds at most 1,000 posts on a paid plan (10 on the free
plan), filled account by account.

Ask how many posts if the user did not say; otherwise use 10. A free Apify plan
delivers at most 10 posts per run and 40 results per day.

## 2. Run the scraper

Use the first path that is available.

**A. Apify tools are connected** (tools named `call-actor` and
`get-dataset-items`, from the Apify connector or `https://mcp.apify.com`):
call `call-actor` with actor `intropix/instagram-posts-reels-scraper` and the
input. If the run is not finished when the call returns, poll `get-actor-run`
until it is. Then read the results with `get-dataset-items` using the run's
dataset id, and set `limit` to the run's item count (the default is 20).
With a shell, write the returned items, as one JSON array, to `items.json`
for step 3.

**B. A shell with the Apify CLI** (`apify --version` prints 1.5 or later):
write the input to `input.json`, then run

```bash
apify actors call intropix/instagram-posts-reels-scraper --input-file input.json --json 2>/dev/null
```

Take `storage.defaultDatasetId` and `storage.defaultKeyValueStoreId` from the
printed JSON (do not add `--silent`: together with `--json` it prints nothing).
Then save the results:

```bash
apify datasets get-items <defaultDatasetId> --format json > items.json
```

If the CLI says you are not logged in, ask the user to run `apify login`
themselves (it opens a browser). Never ask the user to paste an API token into
the conversation.

**C. Neither is available:** tell the user to either connect Apify
(`https://mcp.apify.com`) or install the CLI (`npm install -g apify-cli`, then
`apify login`). An Apify account is free to create. Stop there.

## 3. Save the files

Media links point at Instagram's CDN and **expire within days**, so download
right after the run. With a shell and Python 3:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/save_media.py items.json instagram
```

(`${CLAUDE_SKILL_DIR}` is this skill's folder; use its real path if the variable
is not set.) This writes `instagram/<username>/<date>_<post id>[_<slide>].jpg|mp4`
and appends each post once to `instagram/<username>/items.jsonl`, so repeated
runs only add what is new. Add `--covers` to also save video cover images.

Without Python, download each `media[].media_url` with `curl -L -o`. Without a
shell, show the user the post links (`permalink`) and the media links, and say
they expire.

If the user wants a spreadsheet, write a CSV with `username`, `taken_at`,
`post_type`, `permalink`, `caption`, `like_count`, `comment_count`,
`view_count`.

## 4. Report

Say how many posts were saved, where, the date range they cover, and the cost
(see below). A `view_count` of null means "not available", never zero; likes
can be null where the owner hid them.

**Fewer posts than expected or none:** read the run's `OUTPUT` record
(`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`). Its `reason` and
`failed_target_reasons` explain it: `not_found` (wrong handle),
`user_daily_exhausted` (free plan daily limit reached), `temporarily_unavailable`
or `upstream_outage` (retry later). With `mediaType` set, `maxPosts` counts posts
read, not posts delivered, so fewer come back.

## Cost

Paid by the user's own Apify account: $0.005 per run, $0.002 per account
scanned, $0.0019 per delivered post ($1.90 per 1,000). Failed lookups are not
charged. Example: the newest 100 posts of one account cost about $0.20.

For more fields (music, shares, location, tagged accounts, sponsor brand,
business contacts) the PRO edition `intropix/instagram-posts-reels-scraper-pro`
takes the same input at $3.90 per 1,000 posts.

Scraper page: https://apify.com/intropix/instagram-posts-reels-scraper
