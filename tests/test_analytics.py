from marketing_bot.db import init_db, get_connection
from marketing_bot.analytics import top_topic_last_week


def _seed(db):
    with get_connection(db) as conn:
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','sip','tw-1','b','2026-04-10T09:00:00')"
        )
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','epf','tw-2','b','2026-04-11T09:00:00')"
        )
        conn.execute(
            "INSERT INTO engagement(post_id, platform, likes, comments, shares, impressions, collected_at) "
            "VALUES('tw-1','twitter',100,5,10,5000,'2026-04-14T23:00:00')"
        )
        conn.execute(
            "INSERT INTO engagement(post_id, platform, likes, comments, shares, impressions, collected_at) "
            "VALUES('tw-2','twitter',5,0,0,100,'2026-04-14T23:00:00')"
        )
        conn.commit()


def test_top_topic_picks_highest_engagement(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    _seed(db)
    topic = top_topic_last_week(db, as_of="2026-04-14")
    assert topic == "sip"


def test_top_topic_none_when_empty(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    assert top_topic_last_week(db, as_of="2026-04-14") is None
