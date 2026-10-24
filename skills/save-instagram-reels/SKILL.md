---
name: save-instagram-reels
description: "Save or download Instagram reels and videos from a public business, creator or brand account, as MP4 files plus JSON with view counts, likes, comments, captions and dates. Use when the user wants to download Instagram reels, back up a brand's reels, get reel view counts, or collect the latest videos of an account, including reels shown only on the reels tab. No Instagram login needed; works on the free Apify plan."
---

# Save Instagram reels

Runs the Intropix **Instagram Posts & Reels Scraper** on Apify
(`intropix/instagram-posts-reels-scraper`) with the video filter on, and saves
the MP4 files plus one JSON record per reel, view counts included.

## Rules

- Public **business, creator and brand accounts** only. If the user asks for a
  private person's account, say the scraper's terms do not allow it and stop.
  Private accounts are never readable.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not republish them as a dataset.

## 1. Build the input

```json
{"usernames": ["nike"], "mediaType": "video", "maxPosts": 20}
```

| Field | Use |
|---|---|
| `usernames` | Account handles without `@`. |
| `postUrls` | Instead: reel links like `https://www.instagram.com/reel/<code>/`. Every valid link is delivered. |
| `mediaType` | Always `video` for this skill. Photos are skipped and not charged. |
| `maxPosts` | How many of the newest posts are **read**, not how many reels come back. Every reel among them is delivered and billed. Set it to about 1.5 times the number of reels wanted (most brands post mainly reels) and save everything delivered, since it is paid for. |
| `maxPostsPerAccount` | Instead of `maxPosts`, for several accounts: how many of EACH account's newest posts are read. Same 1.5 times rule. |
| `sinceDate`, `untilDate` | Optional `YYYY-MM-DD` (UTC) bounds. |
| `includeOffGridReels` | `true` to also get reels shown only on the reels tab, not on the profile grid. Off by default. |

View counts come by default (`includeViews` is on).

**Several accounts:** use `maxPostsPerAccount` instead of `maxPosts`.
`maxPosts` alone is one shared total spent in input order, so the first
account can use it all. A run holds at most 1,000 posts on a paid plan (10
on the free plan), filled account by account.

Ask how many reels if the user did not say; otherwise aim for 10. A free Apify
plan delivers at most 10 posts per run and 40 results per day.

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
python3 ${CLAUDE_SKILL_DIR}/scripts/save_media.py items.json instagram --covers
```

(`${CLAUDE_SKILL_DIR}` is this skill's folder; use its real path if the variable
is not set.) This writes `instagram/<username>/<date>_<post id>.mp4`, the cover
image beside it, and appends each reel once to
`instagram/<username>/items.jsonl`, so repeated runs only add what is new.

Without Python, download each `media[].media_url` with `curl -L -o`. Without a
shell, show the user the reel links (`permalink`) and the video links, and say
they expire.

## 4. Report

Say how many reels were saved, where, and list them newest first with date,
`view_count`, `like_count` and `comment_count`. A `view_count` of null means
"not available", never zero. `is_off_grid: true` marks a reel that was not on
the profile grid.

**Fewer reels than expected or none:** with `mediaType: video`, `maxPosts`
counts posts read, so an account that posts mostly photos returns few reels;
raise `maxPosts` or add `sinceDate`. For other cases read the run's `OUTPUT`
record (`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`): `not_found` (wrong handle),
`user_daily_exhausted` (free plan daily limit reached),
`temporarily_unavailable` or `upstream_outage` (retry later).

## Cost

Paid by the user's own Apify account: $0.005 per run, $0.002 per account
scanned, $0.0019 per delivered reel ($1.90 per 1,000). Skipped photos and
failed lookups are not charged.

For the reel's music, shares and location, the PRO edition
`intropix/instagram-posts-reels-scraper-pro` takes the same input at $3.90 per
1,000 posts.

Scraper page: https://apify.com/intropix/instagram-posts-reels-scraper
