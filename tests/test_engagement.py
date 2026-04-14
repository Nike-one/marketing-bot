from unittest.mock import MagicMock, patch
from marketing_bot.db import init_db, get_connection
from marketing_bot.engagement import EngagementCollector


def _seed(db):
    with get_connection(db) as conn:
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES('twitter','sip','tw-1','body','2026-04-14T09:00:00')"
        )
        conn.commit()


@patch("marketing_bot.engagement.requests")
def test_collect_twitter_metrics(mock_requests, tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    _seed(db)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "public_metrics": {
                "like_count": 10,
                "retweet_count": 2,
                "reply_count": 1,
                "impression_count": 500,
            }
        }
    }
    mock_resp.raise_for_status = MagicMock()
    mock_requests.get.return_value = mock_resp

    collector = EngagementCollector(db, twitter_bearer="bt", linkedin_token=None, reddit=None)
    collector.collect_twitter()

    with get_connection(db) as conn:
        row = conn.execute(
            "SELECT likes, shares, comments, impressions FROM engagement WHERE post_id='tw-1'"
        ).fetchone()
    assert row["likes"] == 10
    assert row["shares"] == 2
    assert row["comments"] == 1
    assert row["impressions"] == 500
