# Ebook Marketing Bot

Automated marketing for personal finance ebook targeting young Indian professionals (20–30).

## Setup
1. `cd marketing_bot`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in keys
4. Run `python main.py --auth twitter` (repeat for linkedin, reddit)
5. Test: `pytest` (from inside `marketing_bot/`)
6. Run: `python main.py --dry-run` (keep DRY_RUN=true for first 2 weeks)
