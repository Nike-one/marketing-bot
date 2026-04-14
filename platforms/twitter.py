from typing import List
import tweepy
from marketing_bot.platforms import register
from marketing_bot.platforms.base import BasePublisher, PostResult


@register
class TwitterPublisher(BasePublisher):
    name = "twitter"

    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_secret, bearer_token):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )

    def post(self, content: List[str], topic_slug: str) -> PostResult:
        first_id = None
        reply_to = None
        for tweet in content:
            resp = self.client.create_tweet(text=tweet, in_reply_to_tweet_id=reply_to)
            tid = resp.data["id"]
            if first_id is None:
                first_id = tid
            reply_to = tid
        return PostResult(
            post_id=str(first_id),
            url=f"https://twitter.com/i/web/status/{first_id}",
            platform="twitter",
        )
