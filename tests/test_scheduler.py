# tests/test_scheduler.py
from unittest.mock import MagicMock, patch
from datetime import date
import json
from marketing_bot.db import init_db, get_connection
from marketing_bot.scheduler import run_daily_job, run_weekly_job


@patch("marketing_bot.scheduler.ContentEngine")
def test_daily_job_posts_to_all_platforms(MockEngine, tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)

    topic_file = tmp_path / "topics.json"
    topic_file.write_text(json.dumps([
        {"slug": "sip", "title": "SIP", "hook": "h", "category": "c"}
    ]))

    engine = MagicMock()
    engine.generate_tweet_thread.return_value = ["t1", "t2", "t3"]
    engine.generate_linkedin_post.return_value = "linkedin body"
    engine.generate_reddit_post.return_value = ("title", "body")
    MockEngine.return_value = engine

    twitter = MagicMock()
    twitter.name = "twitter"
    twitter.post.return_value = MagicMock(post_id="tw-1", url="u", platform="twitter")
    linkedin = MagicMock()
    linkedin.name = "linkedin"
    linkedin.post.return_value = MagicMock(post_id="li-1", url="u", platform="linkedin")
    reddit = MagicMock()
    reddit.name = "reddit"
    reddit.post.return_value = MagicMock(post_id="rd-1", url="u", platform="reddit")

    run_daily_job(
        db_path=db,
        topic_file=str(topic_file),
        content_engine_kwargs={"api_key": "k", "db_path": db, "landing_url": "u"},
        publishers=[twitter, linkedin, reddit],
        dry_run=False,
    )

    with get_connection(db) as conn:
        rows = conn.execute("SELECT platform FROM posts").fetchall()
    platforms = {r["platform"] for r in rows}
    assert platforms == {"twitter", "linkedin", "reddit"}


@patch("marketing_bot.scheduler.ContentEngine")
def test_daily_job_dry_run_no_posts(MockEngine, tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)

    topic_file = tmp_path / "topics.json"
    topic_file.write_text(json.dumps([
        {"slug": "sip", "title": "SIP", "hook": "h", "category": "c"}
    ]))

    engine = MagicMock()
    engine.generate_tweet_thread.return_value = ["t1", "t2", "t3"]
    engine.generate_linkedin_post.return_value = "li"
    engine.generate_reddit_post.return_value = ("t", "b")
    MockEngine.return_value = engine

    twitter = MagicMock()
    twitter.name = "twitter"

    run_daily_job(
        db_path=db, topic_file=str(topic_file),
        content_engine_kwargs={"api_key": "k", "db_path": db, "landing_url": "u"},
        publishers=[twitter], dry_run=True,
    )

    twitter.post.assert_not_called()
    with get_connection(db) as conn:
        rows = conn.execute("SELECT * FROM posts").fetchall()
    assert len(rows) == 0


@patch("marketing_bot.scheduler.ContentEngine")
def test_daily_job_skips_already_posted(MockEngine, tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)

    topic_file = tmp_path / "topics.json"
    topic_file.write_text(json.dumps([
        {"slug": "sip", "title": "SIP", "hook": "h", "category": "c"}
    ]))

    today = date.today().isoformat()
    with get_connection(db) as conn:
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','sip','old','b',?)",
            (f"{today}T09:00:00",),
        )
        conn.commit()

    engine = MagicMock()
    engine.generate_tweet_thread.return_value = ["t1"]
    engine.generate_linkedin_post.return_value = "li"
    engine.generate_reddit_post.return_value = ("t", "b")
    MockEngine.return_value = engine

    twitter = MagicMock()
    twitter.name = "twitter"

    run_daily_job(
        db_path=db, topic_file=str(topic_file),
        content_engine_kwargs={"api_key": "k", "db_path": db, "landing_url": "u"},
        publishers=[twitter], dry_run=False,
    )
    twitter.post.assert_not_called()


@patch("marketing_bot.scheduler.BeehiivClient")
@patch("marketing_bot.scheduler.ContentEngine")
@patch("marketing_bot.scheduler.top_topic_last_week")
def test_weekly_job_sends_newsletter(mock_top, MockEngine, MockBeehiiv, tmp_path):
    import json
    from marketing_bot.db import init_db
    db = str(tmp_path / "t.db")
    init_db(db)
    topic_file = tmp_path / "topics.json"
    topic_file.write_text(json.dumps([
        {"slug": "sip", "title": "SIP", "hook": "h", "category": "c"}
    ]))

    mock_top.return_value = "sip"

    engine = MagicMock()
    engine.generate_newsletter.return_value = "Newsletter body"
    MockEngine.return_value = engine

    beehiiv = MagicMock()
    beehiiv.send_newsletter.return_value = "post-42"
    MockBeehiiv.return_value = beehiiv

    run_weekly_job(
        db_path=db, topic_file=str(topic_file),
        content_engine_kwargs={"api_key": "k", "db_path": db, "landing_url": "u"},
        beehiiv_kwargs={"api_key": "k", "publication_id": "p"},
        dry_run=False,
    )
    beehiiv.send_newsletter.assert_called_once()
    kwargs = beehiiv.send_newsletter.call_args.kwargs
    assert "Newsletter body" in kwargs["body_html"]
    assert "Disclaimer" in kwargs["body_html"]
