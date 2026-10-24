---
name: track-instagram-brand-deals
description: "Track Instagram brand deals and sponsored posts of a public creator, influencer or brand account: which brands sponsor them, paid-partnership posts, collab posts with co-authors, and how big each partner is. Use when the user wants to find who sponsors an influencer, list an account's brand partnerships, monitor competitors' influencer deals, or vet a creator before working with them. No Instagram login needed."
---

# Track Instagram brand deals

Runs the Intropix **PRO Instagram Posts & Reels Scraper** on Apify
(`intropix/instagram-posts-reels-scraper-pro`) and lists every sponsored or
collab post of an account with the brands involved.

## Rules

- Public **business, creator and brand accounts** only. If the user asks for a
  private person's account, say the scraper's terms do not allow it and stop.
- Partners and tagged accounts can be private people: do not scrape them in
  turn or build profiles of them.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not republish them as a dataset.

## 1. Build the input

```json
{"usernames": ["natgeo"], "maxPosts": 100, "enrichPartners": true}
```

| Field | Use |
|---|---|
| `usernames` | The creator or brand to check, without `@`. |
| `maxPosts` | How many of the newest posts to read. 100 is a few months for most creators. |
| `maxPostsPerAccount` | Instead of `maxPosts` for several creators: up to this many of EACH one's newest posts. |
| `sinceDate`, `untilDate` | Optional `YYYY-MM-DD` (UTC) bounds. |
| `enrichPartners` | `true` adds `{username, full_name, follower_count, is_verified, category, account_type}` for every co-author and sponsor brand. $0.005 per profile, once per run; paid Apify plans only (a free-plan run returns the posts without it). |

**Several creators:** use `maxPostsPerAccount` instead of `maxPosts`.
`maxPosts` alone is one shared total spent in input order, so the first
creator can use it all. A run holds at most 1,000 posts on a paid plan (10
on the free plan), filled account by account.

A free Apify plan delivers at most 10 posts per run and 40 results per day.

If the user only needs to know which posts are labelled or collab posts, the
standard scraper `intropix/instagram-posts-reels-scraper` returns
`is_paid_partnership` and `coauthors` at $1.90 per 1,000 posts; the sponsor
brand names (`sponsor_usernames`) and partner sizes need PRO.

## 2. Run the scraper

Use the first path that is available.

**A. Apify tools are connected** (tools named `call-actor` and
`get-dataset-items`, from the Apify connector or `https://mcp.apify.com`):
call `call-actor` with actor `intropix/instagram-posts-reels-scraper-pro` and
the input. If the run is not finished when the call returns, poll
`get-actor-run` until it is. Then read the results with `get-dataset-items`
using the run's dataset id, and set `limit` to the run's item count (the
default is 20).

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
```

If the CLI says you are not logged in, ask the user to run `apify login`
themselves (it opens a browser). Never ask the user to paste an API token into
the conversation.

**C. Neither is available:** tell the user to either connect Apify
(`https://mcp.apify.com`) or install the CLI (`npm install -g apify-cli`, then
`apify login`). An Apify account is free to create. Stop there.

## 3. Find the deals

A post is a brand deal when any of these holds:

- `is_paid_partnership` is `true` (Instagram's "Paid partnership" label);
  `sponsor_usernames` names the brand(s);
- `coauthors` has an account other than the owner (a collab post);
- the caption has `#ad`, `#sponsored`, `#partner` or a brand `@mention` with a
  discount code (flag these as "likely, not labelled").

Write `brand-deals.csv` with: `taken_at`, `permalink`, `post_type`, deal type
(labelled / collab / likely), brands, `like_count`, `comment_count`,
`view_count`, and, with enrichment, each brand's `follower_count` and
`category` from `partners`.

## 4. Report

Summarise: how many of the posts read were deals, the brands ranked by number
of posts, the newest deal per brand, and whether labelled deals perform better
or worse than the account's other posts (median likes or views). Null means
"not available", never zero.

If the run returned fewer posts than expected, read the run's `OUTPUT` record
(`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`) and explain its `reason`.

## Cost

Paid by the user's own Apify account: $0.005 per run, $0.002 per account
scanned, $0.0039 per delivered post ($3.90 per 1,000), plus $0.005 per enriched
partner profile. Failed lookups are not charged. Example: 100 posts with 8
partner brands cost about $0.45.

Scraper page: https://apify.com/intropix/instagram-posts-reels-scraper-pro
