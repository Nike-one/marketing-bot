from datetime import datetime, timedelta, timezone
from typing import Optional
import requests
from marketing_bot.db import get_connection


class EngagementCollector:
    def __init__(self, db_path: str, twitter_bearer: Optional[str],
                 linkedin_token: Optional[str], reddit):
        self.db_path = db_path
        self.twitter_bearer = twitter_bearer
        self.linkedin_token = linkedin_token
        self.reddit = reddit

    def _recent_posts(self, platform: str):
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        with get_connection(self.db_path) as conn:
            return conn.execute(
                "SELECT post_id FROM posts WHERE platform=? AND posted_at >= ?",
                (platform, cutoff),
            ).fetchall()

    def _record(self, post_id: str, platform: str, likes: int,
                comments: int, shares: int, impressions: int) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO engagement"
                "(post_id, platform, likes, comments, shares, impressions, collected_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (post_id, platform, likes, comments, shares, impressions,
                 datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def collect_twitter(self) -> None:
        for row in self._recent_posts("twitter"):
            pid = row["post_id"]
            resp = requests.get(
                f"https://api.twitter.com/2/tweets/{pid}",
                headers={"Authorization": f"Bearer {self.twitter_bearer}"},
                params={"tweet.fields": "public_metrics"},
                timeout=30,
            )
            resp.raise_for_status()
            m = resp.json()["data"]["public_metrics"]
            self._record(pid, "twitter",
                         likes=m.get("like_count", 0),
                         comments=m.get("reply_count", 0),
                         shares=m.get("retweet_count", 0),
                         impressions=m.get("impression_count", 0))

    def collect_linkedin(self) -> None:
        if not self.linkedin_token:
            return
        for row in self._recent_posts("linkedin"):
            pid = row["post_id"]
            try:
                resp = requests.get(
                    f"https://api.linkedin.com/v2/socialActions/{pid}",
                    headers={"Authorization": f"Bearer {self.linkedin_token}"},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                self._record(pid, "linkedin",
                             likes=data.get("likesSummary", {}).get("totalLikes", 0),
                             comments=data.get("commentsSummary", {}).get("totalComments", 0),
                             shares=0, impressions=0)
            except Exception:
                continue

    def collect_reddit(self) -> None:
        if not self.reddit:
            return
        for row in self._recent_posts("reddit"):
            pid = row["post_id"]
            try:
                sub = self.reddit.submission(id=pid)
                self._record(pid, "reddit",
                             likes=int(sub.score),
                             comments=int(sub.num_comments),
                             shares=0, impressions=0)
            except Exception:
                continue

    def collect_all(self) -> None:
        self.collect_twitter()
        self.collect_linkedin()
        self.collect_reddit()
