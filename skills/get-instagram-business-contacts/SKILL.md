---
name: get-instagram-business-contacts
description: "Get the public business contact details of Instagram business and creator accounts: email, phone, address, city, website, bio links, category, followers and account type, for a list of handles. Use when the user wants Instagram business emails, contact info for a list of brands, or to turn Instagram handles into a lead list or CRM spreadsheet. Returns only what the profile shows publicly; no Instagram login needed."
---

# Get Instagram business contacts

Runs the Intropix **PRO Instagram Posts & Reels Scraper** on Apify
(`intropix/instagram-posts-reels-scraper-pro`) once for the whole list,
reading one post per account to get its public profile, and builds a contact
sheet.

## Rules

- Business, creator and brand accounts only. Drop every account whose
  `owner_account_type` is `personal`, and do not use their details.
- Contact details come back only where the profile shows them publicly; a null
  means the account does not show it. Never guess an address.
- The data is for business-to-business contact. Unsolicited marketing mail can
  need the recipient's consent in some countries (EU, UK); remind the user once.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not resell or republish them.

## 1. Build the input

One run for the whole list, one post per account:

```json
{"usernames": ["redbull", "heineken"], "maxPostsPerAccount": 1, "includeViews": false}
```

Use `maxPostsPerAccount`, not `maxPosts`: `maxPosts` is one shared total, so
`maxPosts: 1` would return only the first handle. A run holds at most 1,000
accounts on a paid plan; split a longer list into several runs.

A free Apify plan delivers at most 10 results per run and 40 per day, so on
the free plan run at most 10 handles at a time; a longer list needs a paid
plan.

## 2. Run the scraper

Use the first path that is available.

**A. Apify tools are connected** (tools named `call-actor` and
`get-dataset-items`, from the Apify connector or `https://mcp.apify.com`):
call `call-actor` with actor `intropix/instagram-posts-reels-scraper-pro` and
the input. If the run is not finished when the call returns, poll
`get-actor-run` until it is. Then read the result with `get-dataset-items`
using the run's dataset id, and set `limit` to the run's item count (the
default is 20).

**B. A shell with the Apify CLI** (`apify --version` prints 1.5 or later):
write the input to `input.json`, then run

```bash
apify actors call intropix/instagram-posts-reels-scraper-pro --input-file input.json --json 2>/dev/null
```

Take `storage.defaultDatasetId` and `storage.defaultKeyValueStoreId` from the
printed JSON (do not add `--silent`: together with `--json` it prints nothing).
Then read the result:

```bash
apify datasets get-items <defaultDatasetId> --format json
```

If the CLI says you are not logged in, ask the user to run `apify login`
themselves (it opens a browser). Never ask the user to paste an API token into
the conversation.

**C. Neither is available:** tell the user to either connect Apify
(`https://mcp.apify.com`) or install the CLI (`npm install -g apify-cli`, then
`apify login`). An Apify account is free to create. Stop there.

## 3. Build the contact sheet

One row per account from its item, written to `instagram-contacts.csv`:
`username`, `full_name`, `owner_account_type`, `owner_category`,
`follower_count`, `is_verified`, `owner_public_email`, `owner_public_phone`,
`owner_address`, `owner_city`, `owner_website`, `owner_bio_links` (joined with
spaces), profile link `https://www.instagram.com/<username>/`.

An account with no posts returns no item: note it as "no posts, no profile
data". For a missing account, read the run's `OUTPUT` record
(`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`): `not_found` means the handle
does not exist.

## 4. Report

Say how many accounts were checked, how many show an email, a phone and a
website, which were dropped as personal, and where the CSV is.

## Cost

Paid by the user's own Apify account: $0.005 once per run, plus $0.002 scan
and $0.0039 for the one post per account, about $0.006 per account. 100
accounts in one run cost about $0.60. Failed lookups are not charged.

Scraper page: https://apify.com/intropix/instagram-posts-reels-scraper-pro
