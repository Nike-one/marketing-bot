import argparse
import logging
import os
from marketing_bot.config import Config
from marketing_bot.db import init_db
from marketing_bot.scheduler import run_daily_job, run_weekly_job


def _build_publishers(cfg: Config):
    from marketing_bot.platforms.twitter import TwitterPublisher
    from marketing_bot.platforms.linkedin import LinkedInPublisher
    from marketing_bot.platforms.reddit import RedditPublisher
    return [
        TwitterPublisher(
            consumer_key=cfg.twitter_consumer_key,
            consumer_secret=cfg.twitter_consumer_secret,
            access_token=cfg.twitter_access_token,
            access_secret=cfg.twitter_access_secret,
            bearer_token=cfg.twitter_bearer_token,
        ),
        LinkedInPublisher(
            access_token=cfg.twitter_bearer_token,  # replaced by OAuthManager at runtime
            person_urn=cfg.linkedin_person_urn,
        ),
        RedditPublisher(
            client_id=cfg.reddit_client_id,
            client_secret=cfg.reddit_client_secret,
            username=cfg.reddit_username,
            password=cfg.reddit_password,
            user_agent=cfg.reddit_user_agent,
            subreddit="personalfinanceindia",
        ),
    ]


def cli() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--weekly", action="store_true")
    parser.add_argument("--platform", action="append",
                        help="Restrict to single platform (repeatable)")
    parser.add_argument("--topic", help="Force specific topic slug")
    args = parser.parse_args()

    cfg = Config.from_env()
    init_db(cfg.db_path)
    dry_run = args.dry_run or cfg.dry_run

    topic_file = os.path.join(os.path.dirname(__file__), "topic_pool.json")

    ce_kwargs = {
        "api_key": cfg.gemini_api_key,
        "db_path": cfg.db_path,
        "landing_url": cfg.landing_page_url,
    }

    if args.weekly:
        run_weekly_job(
            db_path=cfg.db_path,
            topic_file=topic_file,
            content_engine_kwargs=ce_kwargs,
            beehiiv_kwargs={"api_key": cfg.beehiiv_api_key,
                            "publication_id": cfg.beehiiv_publication_id},
            dry_run=dry_run,
        )
        return

    publishers = _build_publishers(cfg)
    if args.platform:
        publishers = [p for p in publishers if p.name in args.platform]

    run_daily_job(
        db_path=cfg.db_path,
        topic_file=topic_file,
        content_engine_kwargs=ce_kwargs,
        publishers=publishers,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    cli()
