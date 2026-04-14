from unittest.mock import MagicMock, patch
from marketing_bot.content_engine import ContentEngine, pick_next_topic


def test_pick_next_topic_skips_recent(tmp_path):
    from marketing_bot.db import init_db, get_connection
    db = str(tmp_path / "t.db")
    init_db(db)
    topics = [
        {"slug": "a", "title": "A", "hook": "h", "category": "c"},
        {"slug": "b", "title": "B", "hook": "h", "category": "c"},
    ]
    with get_connection(db) as conn:
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','a','x','y','2026-04-14T09:00:00')"
        )
        conn.commit()
    chosen = pick_next_topic(db, topics, recent_days=50)
    assert chosen["slug"] == "b"


def test_pick_next_topic_oldest_when_all_recent(tmp_path):
    from marketing_bot.db import init_db, get_connection
    db = str(tmp_path / "t.db")
    init_db(db)
    topics = [
        {"slug": "a", "title": "A", "hook": "h", "category": "c"},
        {"slug": "b", "title": "B", "hook": "h", "category": "c"},
    ]
    with get_connection(db) as conn:
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','a','x','y','2026-04-13T09:00:00')"
        )
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','b','x','y','2026-04-14T09:00:00')"
        )
        conn.commit()
    chosen = pick_next_topic(db, topics, recent_days=50)
    assert chosen["slug"] == "a"


@patch("marketing_bot.content_engine.genai")
def test_generate_tweet_thread(mock_genai, tmp_path):
    from marketing_bot.db import init_db
    db = str(tmp_path / "t.db")
    init_db(db)

    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = (
        "Tweet 1 about SIP\n---\nTweet 2 continues\n---\nTweet 3 closes"
    )
    mock_genai.GenerativeModel.return_value = mock_model

    topic = {"slug": "sip", "title": "SIP basics", "hook": "h", "category": "investing"}
    engine = ContentEngine(api_key="k", db_path=db, landing_url="https://x.com")
    tweets = engine.generate_tweet_thread(topic)
    assert len(tweets) == 3
    assert "SIP" in tweets[0]


@patch("marketing_bot.content_engine.genai")
def test_generate_linkedin_post(mock_genai, tmp_path):
    from marketing_bot.db import init_db
    db = str(tmp_path / "t.db")
    init_db(db)

    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Professional LinkedIn post body."
    mock_genai.GenerativeModel.return_value = mock_model

    topic = {"slug": "sip", "title": "SIP basics", "hook": "h", "category": "investing"}
    engine = ContentEngine(api_key="k", db_path=db, landing_url="https://x.com")
    post = engine.generate_linkedin_post(topic)
    assert "Professional" in post


@patch("marketing_bot.content_engine.genai")
def test_reddit_post_strips_landing_link(mock_genai, tmp_path):
    from marketing_bot.db import init_db
    db = str(tmp_path / "t.db")
    init_db(db)

    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = (
        "TITLE: SIP basics for beginners\nBODY:\nReddit body with https://x.com somewhere"
    )
    mock_genai.GenerativeModel.return_value = mock_model

    topic = {"slug": "sip", "title": "SIP basics", "hook": "h", "category": "investing"}
    engine = ContentEngine(api_key="k", db_path=db, landing_url="https://x.com")
    title, body = engine.generate_reddit_post(topic)
    assert "https://x.com" not in body
    assert "https://x.com" not in title
