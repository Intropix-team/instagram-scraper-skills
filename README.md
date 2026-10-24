# Instagram scraper skills

Agent skills that save Instagram stories, reels and posts, download a
competitor's Instagram, track brand deals and collect business contacts. They
run the [Intropix](https://apify.com/intropix) Instagram scrapers on Apify:
no Instagram login, no cookies, public business, creator and brand accounts
only, and a free Apify plan is enough to try them (10 results per run, 40 per
day).

| Skill | Ask for example | Scraper |
|---|---|---|
| `instagram-scraper` | "Scrape nike's last 20 posts to a CSV" (any job below, in one skill) | All three |
| `save-instagram-stories` | "Save today's stories from @natgeo" | [Instagram Stories Scraper](https://apify.com/intropix/instagram-stories-scraper) |
| `save-instagram-reels` | "Download the last 10 reels from nike with view counts" | [Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper) |
| `save-instagram-posts` | "Back up redbull's posts from September" | [Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper) |
| `download-competitor-instagram` | "Audit adidas's Instagram for the last 50 posts" | [PRO Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper-pro) |
| `track-instagram-brand-deals` | "Which brands sponsor this creator?" | [PRO Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper-pro) |
| `get-instagram-business-contacts` | "Get the public emails of these 20 brands" | [PRO Instagram Posts & Reels Scraper](https://apify.com/intropix/instagram-posts-reels-scraper-pro) |

## Install

As a plugin, in agents with plugin marketplaces:

```bash
/plugin marketplace add Intropix-team/instagram-scraper-skills
/plugin install intropix@intropix
```

Any agent that reads skills (Cursor, Codex, Gemini CLI and others):

```bash
npx skills add Intropix-team/instagram-scraper-skills
```

## What you need

An [Apify](https://apify.com) account (free to create), connected in one of two
ways:

- **Apify MCP server.** The plugin declares Apify's hosted server
  `https://mcp.apify.com/?tools=call-actor`; you sign in to Apify in the
  browser the first time it is used. Other agents can add the same URL as an
  MCP server.
- **Apify CLI.** `npm install -g apify-cli`, then `apify login`. The skills run
  `apify actors call` and `apify datasets get-items`.

The skills never ask for your API token in the conversation.

## What it sends, where, and what it costs

- The Instagram handles or post links you ask about, and the scraper input
  built from them, go to Apify (`mcp.apify.com` or `api.apify.com`, through the
  MCP server or the CLI), which runs the Intropix scraper in your own Apify
  account.
- The `instagram-scraper`, `save-*` and `download-competitor-instagram`
  skills then download the media files from Instagram's CDN
  (`*.cdninstagram.com`) to a local folder, using the bundled
  `scripts/save_media.py` (Python 3, standard library only).
- Nothing is sent anywhere else, and the skills keep no data of their own.
- Runs are billed to your Apify account at the scrapers' public prices: $1.90
  per 1,000 posts, $2.50 per 1,000 stories, $3.90 per 1,000 PRO posts, plus
  $0.005 per run and $0.002 per scanned account. Failed lookups are not charged.

## Terms

Use these skills only for public business, creator and brand accounts and for
legitimate business purposes (competitive monitoring, brand protection,
partnership and market research, B2B outreach). Do not target personal
accounts, build profiles of individuals, or keep results longer than your
purpose needs. The full Terms of Use and the privacy notice are on each
scraper's page; see also [PRIVACY.md](PRIVACY.md).

Intropix is independent and not affiliated with, endorsed by, or connected to
Instagram or Meta.

Contact: team.intropix@gmail.com

## License

MIT
