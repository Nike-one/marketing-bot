from datetime import datetime, timedelta
from typing import Optional
from marketing_bot.db import get_connection


def top_topic_last_week(db_path: str, as_of: str) -> Optional[str]:
    as_of_date = datetime.fromisoformat(as_of).date()
    start = (as_of_date - timedelta(days=7)).isoformat()
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT p.topic,
                   SUM(e.likes + e.comments*3 + e.shares*5 + e.impressions/100) as score
            FROM posts p
            JOIN engagement e ON e.post_id = p.post_id AND e.platform = p.platform
            WHERE substr(p.posted_at,1,10) >= ?
            GROUP BY p.topic
            ORDER BY score DESC
            LIMIT 1
            """,
            (start,),
        ).fetchone()
    return row["topic"] if row else None
