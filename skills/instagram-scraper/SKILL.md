---
name: instagram-scraper
description: "Scrape Instagram without logging in: stories, posts, reels and carousels of public business, creator and brand accounts, or single posts from their links, with captions, likes, comments, view counts, dates, music, locations, collab co-authors, sponsor brands and the account's public business contacts, plus the image and video files. Use whenever the user wants Instagram data or downloads of any kind: scrape an Instagram profile, download stories or reels, export posts to JSON or CSV, monitor or audit a competitor, find brand deals, or build a lead list. Three Intropix scrapers on Apify; works on the free Apify plan."
---

# Instagram scraper

Runs the Intropix Instagram scrapers on Apify and saves what they return. One
skill for any Instagram job; it picks the right scraper, runs it, and saves
the files.

## Rules

- Public **business, creator and brand accounts** only. If the user asks for a
  private person's account, say the scrapers' terms do not allow it and stop.
  Private accounts are never readable.
- Tagged accounts, mentions and partners in the results can be private people:
  do not scrape them in turn or build profiles of them.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not republish them as a dataset.

## 1. Pick the scraper

| The user wants | Scraper | Price |
|---|---|---|
| Stories that are live now (they vanish after 24 hours) | `intropix/instagram-stories-scraper` | $2.50 per 1,000 stories |
| Posts, reels, carousels with captions, likes, comments, views, dates | `intropix/instagram-posts-reels-scraper` | $1.90 per 1,000 posts |
| Also music, shares, location, sponsor brand names, partner sizes, the account's public email, phone, address and website | `intropix/instagram-posts-reels-scraper-pro` | $3.90 per 1,000 posts |

Use the cheapest scraper that has the fields the user needs. Every run also
costs $0.005, plus $0.002 per account scanned; failed lookups are not charged.

If one of these skills is installed and fits the job better, use it instead:
`save-instagram-stories`, `save-instagram-reels`, `save-instagram-posts`,
`download-competitor-instagram`, `track-instagram-brand-deals`,
`get-instagram-business-contacts`.

## 2. Build the input

**Stories:**

```json
{"usernames": ["natgeo"], "maxResults": 10}
```

`maxResults` is the most story items to deliver (default 10).

**Posts and reels (standard and PRO take the same input):**

```json
{"usernames": ["nike"], "maxPosts": 10}
```

| Field | Use |
|---|---|
| `usernames` | Account handles without `@`. |
| `postUrls` | Instead of or besides usernames: links like `https://www.instagram.com/p/<code>/` or `/reel/<code>/`. Every valid link is delivered. |
| `maxPosts` | How many of the newest posts to read. Default 10. One shared total for the whole run. |
| `maxPostsPerAccount` | Instead of `maxPosts`: up to this many of EACH account's newest posts. Use it whenever there are several accounts. |
| `sinceDate`, `untilDate` | Optional `YYYY-MM-DD` (UTC) bounds. |
| `mediaType` | `any` (default), `image` or `video`. With a filter, `maxPosts` counts posts read, not posts delivered, and every match among them is delivered and billed: for N reels set `maxPosts` to about 1.5 times N (2 for one reel), and save everything delivered. |
| `includeOffGridReels` | `true` also returns reels shown only on the reels tab. |
| `enrichPartners` | PRO only: `true` adds follower count, category and verification for each co-author and sponsor brand ($0.005 per profile, paid Apify plans only). |

For the public contact details of accounts, run PRO with
`maxPostsPerAccount: 1`; the `owner_*` fields of each post carry them.

**Several accounts:** for posts, use `maxPostsPerAccount`; `maxPosts` alone
is one shared total spent in input order, so the first account can use it
all. A run holds at most 1,000 posts on a paid plan (10 on the free plan),
filled account by account. The stories scraper has no per-account limit: for
stories, start one run per account.

Ask how many items if the user did not say; otherwise use 10. A free Apify
plan delivers at most 10 results per run and 40 per day.

## 3. Run the scraper

Use the first path that is available.

**A. Apify tools are connected** (tools named `call-actor` and
`get-dataset-items`, from the Apify connector or `https://mcp.apify.com`):
call `call-actor` with the scraper id and the input. If the run is not
finished when the call returns, poll `get-actor-run` until it is. Then read
the results with `get-dataset-items` using the run's dataset id, and set
`limit` to the run's item count (the default is 20). With a shell, write the
returned items, as one JSON array, to `items.json` for step 4.

**B. A shell with the Apify CLI** (`apify --version` prints 1.5 or later):
write the input to `input.json`, then run

```bash
apify actors call <scraper id> --input-file input.json --json 2>/dev/null
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

## 4. Save the files

Skip this step when the user wants data only. Media links point at
Instagram's CDN and **expire within days**, so download right after the run.
With a shell and Python 3:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/save_media.py items.json instagram --covers
```

(`${CLAUDE_SKILL_DIR}` is this skill's folder; use its real path if the variable
is not set.) This writes `instagram/<username>/<date>_<id>[_<slide>].jpg|mp4`,
reel covers beside the videos, and appends each item once to
`instagram/<username>/items.jsonl`, so repeated runs only add what is new.

Without Python, download each `media_url` (stories) or `media[].media_url`
(posts) with `curl -L -o`. Without a shell, show the links and say they expire.

For a spreadsheet, write a CSV from `items.json` with the columns the user
asked for.

## 5. Report

Say what was saved and where, then answer the user's question from the data.
Null means "not available", never zero.

**Fewer results than expected or none:** stories return nothing when the
account posted none in the last 24 hours. Otherwise read the run's `OUTPUT`
record (`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`): `not_found` (wrong handle),
`user_daily_exhausted` (free plan daily limit reached),
`temporarily_unavailable` or `upstream_outage` (retry later).

Scraper pages:

- https://apify.com/intropix/instagram-stories-scraper
- https://apify.com/intropix/instagram-posts-reels-scraper
- https://apify.com/intropix/instagram-posts-reels-scraper-pro
