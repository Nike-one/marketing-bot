from datetime import date
from marketing_bot.db import get_connection


def already_posted(db_path: str, topic: str, platform: str, day: date) -> bool:
    day_str = day.isoformat()
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM posts WHERE topic=? AND platform=? "
            "AND substr(posted_at,1,10)=? LIMIT 1",
            (topic, platform, day_str),
        ).fetchone()
    return row is not None


def record_post(db_path: str, platform: str, topic: str,
                post_id: str, content: str, posted_at: str) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO posts(platform, topic, post_id, content, posted_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (platform, topic, post_id, content, posted_at),
        )
        conn.commit()
