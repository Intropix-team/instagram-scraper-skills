---
name: save-instagram-stories
description: "Save or download the current Instagram stories of a public business, creator or brand account, as image and video files plus JSON with links, mentions, hashtags, music and the paid-partnership flag. Use when the user wants to download Instagram stories, archive a brand's or competitor's stories before they disappear after 24 hours, check whether an influencer posted a sponsored story, or back up stories every day. Reads age-restricted (18+) brand accounts too. No Instagram login needed; works on the free Apify plan."
---

# Save Instagram stories

Runs the Intropix **Instagram Stories Scraper** on Apify
(`intropix/instagram-stories-scraper`) and saves every active story: the image
or video file plus one JSON record per story.

## Rules

- Public **business, creator and brand accounts** only. If the user asks for a
  private person's account, say the scraper's terms do not allow it and stop.
  Private accounts are never readable.
- Keep the results only as long as the user's purpose needs them (the terms
  suggest at most 30 days), and do not republish them as a dataset.

Stories disappear 24 hours after posting, so a run returns only what is live
right now. To keep an archive, run this once a day into the same folder; the
save step skips stories already saved.

## 1. Build the input

```json
{"usernames": ["natgeo"], "maxResults": 10}
```

| Field | Use |
|---|---|
| `usernames` | Account handles without `@`. |
| `maxResults` | Most story items to deliver in the run. Default 10. |

**One run per account** when the user names several: `maxResults` is shared by
the whole run, so the first account can use it all.

A free Apify plan delivers at most 10 stories per run and 40 results per day.
On a paid plan, 30 is a safe ceiling for one busy account.

## 2. Run the scraper

Use the first path that is available.

**A. Apify tools are connected** (tools named `call-actor` and
`get-dataset-items`, from the Apify connector or `https://mcp.apify.com`):
call `call-actor` with actor `intropix/instagram-stories-scraper` and the
input. If the run is not finished when the call returns, poll `get-actor-run`
until it is. Then read the results with `get-dataset-items` using the run's
dataset id, and set `limit` to the run's item count (the default is 20).
With a shell, write the returned items, as one JSON array, to `items.json`
for step 3.

**B. A shell with the Apify CLI** (`apify --version` prints 1.5 or later):
write the input to `input.json`, then run

```bash
apify actors call intropix/instagram-stories-scraper --input-file input.json --json 2>/dev/null
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

Media links point at Instagram's CDN and **expire**, so download right after
the run. With a shell and Python 3:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/save_media.py items.json instagram-stories
```

(`${CLAUDE_SKILL_DIR}` is this skill's folder; use its real path if the variable
is not set.) This writes `instagram-stories/<username>/<date>_<story id>.jpg|mp4`
and appends each story once to `instagram-stories/<username>/items.jsonl`.

Without Python, download each `media_url` with `curl -L -o`. Without a shell,
list the stories with their media links and say the links expire.

## 4. Report

Say how many stories were saved and where, and list them with `taken_at`,
`media_type`, `link_urls`, `mentions` and `is_paid_partnership`. Point out
sponsored stories and link stickers, since that is usually why people archive
stories.

**No stories:** an empty result is normal when the account posted nothing in
the last 24 hours. Read the run's `OUTPUT` record to be sure
(`apify key-value-stores get-value <defaultKeyValueStoreId> OUTPUT`, or
`get-key-value-store-record` with key `OUTPUT`): `not_found` means a wrong
handle, `user_daily_exhausted` means the free plan's daily limit is reached,
`temporarily_unavailable` or `upstream_outage` mean retry later.

## Cost

Paid by the user's own Apify account: $0.005 per run, $0.002 per account
scanned, $0.0025 per delivered story ($2.50 per 1,000). Failed lookups are not
charged.

Scraper page: https://apify.com/intropix/instagram-stories-scraper
