# marketing_bot/scheduler.py
import json
import logging
from datetime import date, datetime, timezone
from typing import List
from marketing_bot.content_engine import ContentEngine, pick_next_topic
from marketing_bot.moderation import append_disclaimer
from marketing_bot.idempotency import already_posted, record_post
from marketing_bot.analytics import top_topic_last_week
from marketing_bot.newsletter.beehiiv import BeehiivClient

log = logging.getLogger(__name__)


def _load_topics(topic_file: str) -> list:
    with open(topic_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_daily_job(db_path: str, topic_file: str,
                  content_engine_kwargs: dict,
                  publishers: List,
                  dry_run: bool = True) -> None:
    topics = _load_topics(topic_file)
    topic = pick_next_topic(db_path, topics)
    log.info("Picked topic: %s", topic["slug"])

    engine = ContentEngine(**content_engine_kwargs)
    tweets = engine.generate_tweet_thread(topic)
    linkedin_post = engine.generate_linkedin_post(topic)
    reddit_title, reddit_body = engine.generate_reddit_post(topic)

    content_map = {
        "twitter": [append_disclaimer(t, "twitter") for t in tweets],
        "linkedin": append_disclaimer(linkedin_post, "linkedin"),
        "reddit": (reddit_title, append_disclaimer(reddit_body, "reddit")),
    }

    today = date.today()
    for pub in publishers:
        if pub.name not in content_map:
            continue
        if already_posted(db_path, topic["slug"], pub.name, today):
            log.info("Skip %s (already posted today)", pub.name)
            continue
        content = content_map[pub.name]
        if dry_run:
            log.info("[DRY RUN] %s: %r", pub.name, content)
            continue
        try:
            result = pub.post(content, topic_slug=topic["slug"])
            record_post(
                db_path, pub.name, topic["slug"], result.post_id,
                json.dumps(content) if not isinstance(content, str) else content,
                datetime.now(timezone.utc).isoformat(),
            )
            log.info("Posted %s: %s", pub.name, result.url)
        except Exception as e:
            log.exception("Post failed on %s: %s", pub.name, e)


def run_weekly_job(db_path: str, topic_file: str,
                   content_engine_kwargs: dict,
                   beehiiv_kwargs: dict,
                   dry_run: bool = True) -> None:
    topics = _load_topics(topic_file)
    top_slug = top_topic_last_week(db_path, as_of=date.today().isoformat())
    if top_slug:
        topic = next((t for t in topics if t["slug"] == top_slug), topics[0])
    else:
        topic = topics[0]

    engine = ContentEngine(**content_engine_kwargs)
    body = engine.generate_newsletter(topic)
    body = append_disclaimer(body, "newsletter")
    html_body = body.replace("\n", "<br>")

    if dry_run:
        log.info("[DRY RUN] newsletter: %s", topic["slug"])
        return

    beehiiv = BeehiivClient(**beehiiv_kwargs)
    post_id = beehiiv.send_newsletter(
        title=f"{topic['title']}",
        body_html=html_body,
    )
    log.info("Newsletter sent: %s", post_id)
