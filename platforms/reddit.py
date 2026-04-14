from typing import Tuple
import praw
from marketing_bot.platforms import register
from marketing_bot.platforms.base import BasePublisher, PostResult


@register
class RedditPublisher(BasePublisher):
    name = "reddit"

    def __init__(self, client_id, client_secret, username, password,
                 user_agent, subreddit: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent,
        )
        self.subreddit_name = subreddit

    def post(self, content: Tuple[str, str], topic_slug: str) -> PostResult:
        title, body = content
        subreddit = self.reddit.subreddit(self.subreddit_name)
        submission = subreddit.submit(title=title, selftext=body)
        return PostResult(
            post_id=submission.id,
            url=f"https://reddit.com{submission.permalink}",
            platform="reddit",
        )
