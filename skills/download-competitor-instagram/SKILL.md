---
name: download-competitor-instagram
description: "Download a competitor's Instagram (posts, reels, captions, engagement, music, locations, collaborations and sponsor brands) and audit it: what they post, how often, what performs, which brands and creators they work with. Use when the user wants to analyze, audit, benchmark or monitor a competitor's Instagram account, compare several brands' Instagram engagement, or export a brand's Instagram to a spreadsheet. Public business, creator and brand accounts; no Instagram login needed."
---

# Download a competitor's Instagram

Runs the Intropix **PRO Instagram Posts & Reels Scraper** on Apify
(`intropix/instagram-posts-reels-scraper-pro`), saves the posts, and writes a
short audit of the account.

## Rules

- Public **business, creator and brand accounts** only. If the user asks for a
  private person's account, say the scraper's terms do not allow it and stop.
- Tagged accounts, mentions and partners in the results can be private people:
  do not scrape them in turn or build profiles of them.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not republish them as a dataset.

## 1. Build the input

```json
{"usernames": ["nike"], "maxPosts": 50, "includeOffGridReels": true}
```

| Field | Use |
|---|---|
| `usernames` | The competitor's handle, without `@`, or several to compare. |
| `maxPosts` | How many of the newest posts to read. 50 covers a few weeks for most brands. |
| `maxPostsPerAccount` | Instead of `maxPosts` when comparing several accounts: up to this many of EACH account's newest posts. |
| `sinceDate`, `untilDate` | Optional `YYYY-MM-DD` (UTC) bounds, e.g. last quarter. |
| `includeOffGridReels` | `true` also counts reels shown only on the reels tab. |
| `enrichPartners` | `true` adds follower counts and categories for every co-author and sponsor brand ($0.005 per profile, paid Apify plans only). |

**Several competitors:** one run with `maxPostsPerAccount` (e.g. 50) gives
each account the same depth; split the results by `username` and compare.
`maxPosts` alone is one shared total spent in input order, so the first
account can use it all. A run holds at most 1,000 posts on a paid plan (10
on the free plan), filled account by account.

A free Apify plan delivers at most 10 posts per run and 40 results per day,
enough for a first look; a real audit needs a paid plan.

If the user needs only dates, captions, likes, comments and views, the standard
scraper `intropix/instagram-posts-reels-scraper` takes the same input at about
half the price.

## 2. Run the scraper

Use the first path that is available.

**A. Apify tools are connected** (tools named `call-actor` and
`get-dataset-items`, from the Apify connector or `https://mcp.apify.com`):
call `call-actor` with actor `intropix/instagram-posts-reels-scraper-pro` and
the input. If the run is not finished when the call returns, poll
`get-actor-run` until it is. Then read the results with `get-dataset-items`
using the run's dataset id, and set `limit` to the run's item count (the
default is 20). With a shell, write the returned items, as one JSON array, to
`items.json` for step 3.

**B. A shell with the Apify CLI** (`apify --version` prints 1.5 or later):
write the input to `input.json`, then run

```bash
apify actors call intropix/instagram-posts-reels-scraper-pro --input-file input.json --json 2>/dev/null
```

Take `storage.defaultDatasetId` and `storage.defaultKeyValueStoreId` from the
printed JSON (do not add `--silent`: together with `--json` it prints nothing).
Then save the results:

```bash
apify datasets get-items <defaultDatasetId> --format json > items.json
apify datasets get-items <defaultDatasetId> --format csv > posts.csv
```

If the CLI says you are not logged in, ask the user to run `apify login`
themselves (it opens a browser). Never ask the user to paste an API token into
the conversation.

**C. Neither is available:** tell the user to either connect Apify
(`https://mcp.apify.com`) or install the CLI (`npm install -g apify-cli`, then
`apify login`). An Apify account is free to create. Stop there.

## 3. Save the media (if asked)

Media links expire within days. If the user wants the images and videos too,
with a shell and Python 3:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/save_media.py items.json instagram
```

(`${CLAUDE_SKILL_DIR}` is this skill's folder; use its real path if the variable
is not set.) Files land in `instagram/<username>/`, each post recorded once in
`items.jsonl`.

## 4. Write the audit

From the items, report in plain language:

- **Volume and rhythm:** posts per week, the most common weekday and hour (UTC,
  from `taken_at`), share of reels vs photos vs carousels (`post_type`).
- **What performs:** median and top `engagement_rate`, top 5 posts by
  engagement and by `view_count` with their `permalink`. Leave out posts with
  `counts_hidden: true` from rankings and say how many were left out.
- **Content:** most used `hashtags`, recurring caption themes, licensed tracks
  vs original audio (`audio_title`, `is_original_audio`), tagged places
  (`location_name`, `location_city`).
- **Collaborations:** `coauthors`, `sponsor_usernames` and posts with
  `is_paid_partnership`; with `enrichPartners`, the partners' follower counts
  from `partners`.
- **The account:** followers, `owner_category`, `owner_website`, post count.

Null means "not available", never zero. For several competitors, put the key
numbers side by side in one table.

If the run returned fewer posts than expected, read the run's `OUTPUT` record
(`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`) and explain its `reason`.

## Cost

Paid by the user's own Apify account: $0.005 per run, $0.002 per account
scanned, $0.0039 per delivered post ($3.90 per 1,000), plus $0.005 per enriched
partner profile when `enrichPartners` is on. Failed lookups are not charged.
Example: 50 posts of one competitor cost about $0.20.

Scraper page: https://apify.com/intropix/instagram-posts-reels-scraper-pro
