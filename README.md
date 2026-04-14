# Ebook Marketing Bot

An automated marketing tool that promotes a personal finance ebook across **Twitter/X, LinkedIn, Reddit**, and **Beehiiv** newsletter — targeting young Indian professionals (ages 20–30).

It uses **Google Gemini AI** to generate platform-specific content, posts on a daily/weekly schedule, tracks engagement, and avoids duplicate posts automatically.

---

## Features

- AI-generated content tailored for each platform (Twitter, LinkedIn, Reddit)
- Beehiiv newsletter integration
- Daily and weekly posting schedules
- Duplicate post prevention
- Dry-run mode for safe testing before going live
- Cost monitoring to track AI API usage
- Engagement analytics and tracking
- Content moderation built-in

---

## Requirements

- Python 3.10+
- API credentials for: Twitter/X, LinkedIn, Reddit, Beehiiv, Google Gemini

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example file and fill in your API keys:

```bash
cp .env.example .env
```

Open `.env` and add your credentials:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (for AI content generation) |
| `TWITTER_CONSUMER_KEY` | Twitter/X app consumer key |
| `TWITTER_CONSUMER_SECRET` | Twitter/X app consumer secret |
| `TWITTER_ACCESS_TOKEN` | Twitter/X access token |
| `TWITTER_ACCESS_SECRET` | Twitter/X access secret |
| `TWITTER_BEARER_TOKEN` | Twitter/X bearer token |
| `LINKEDIN_CLIENT_ID` | LinkedIn app client ID |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn app client secret |
| `LINKEDIN_REDIRECT_URI` | OAuth callback URL (default: `http://localhost:8080/callback`) |
| `LINKEDIN_PERSON_URN` | Your LinkedIn person URN (e.g. `urn:li:person:xxxx`) |
| `REDDIT_CLIENT_ID` | Reddit app client ID |
| `REDDIT_CLIENT_SECRET` | Reddit app client secret |
| `REDDIT_USERNAME` | Reddit account username |
| `REDDIT_PASSWORD` | Reddit account password |
| `REDDIT_USER_AGENT` | App identifier string (e.g. `ebook-bot/0.1`) |
| `BEEHIIV_API_KEY` | Beehiiv API key |
| `BEEHIIV_PUBLICATION_ID` | Your Beehiiv publication ID |
| `DRY_RUN` | Set to `true` to preview posts without publishing (recommended for first use) |
| `LANDING_PAGE_URL` | URL of your ebook landing page |

### 3. Authenticate platforms

Run OAuth authentication for each platform:

```bash
python main.py --auth twitter
python main.py --auth linkedin
python main.py --auth reddit
```

### 4. Test your setup

```bash
pytest
```

---

## Usage

### Dry run (safe preview — no actual posts)

```bash
python main.py --dry-run
```

> **Recommended:** Keep `DRY_RUN=true` in your `.env` for the first 2 weeks to review generated content before going live.

### Run daily job (posts to all platforms)

```bash
python main.py
```

### Run weekly job

```bash
python main.py --weekly
```

### Post to a specific platform only

```bash
python main.py --platform twitter
python main.py --platform reddit
```

### Force a specific topic

```bash
python main.py --topic "budgeting-basics"
```

---

## Project Structure

```
marketing_bot/
├── main.py               # CLI entry point
├── config.py             # Environment config loader
├── scheduler.py          # Daily/weekly job runner
├── content_engine.py     # AI content generation (Gemini)
├── moderation.py         # Content moderation
├── engagement.py         # Engagement tracking
├── analytics.py          # Analytics helpers
├── cost_monitor.py       # AI cost tracking
├── idempotency.py        # Duplicate post prevention
├── db.py                 # Database setup
├── oauth_manager.py      # OAuth token management
├── topic_pool.json       # List of content topics
├── platforms/
│   ├── twitter.py        # Twitter/X publisher
│   ├── linkedin.py       # LinkedIn publisher
│   ├── reddit.py         # Reddit publisher
│   └── base.py           # Shared publisher interface
├── newsletter/
│   └── beehiiv.py        # Beehiiv newsletter client
├── landing/
│   ├── index.html        # Ebook landing page
│   └── style.css
└── tests/                # Test suite
```

---

## License

MIT
