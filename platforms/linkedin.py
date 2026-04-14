import json
import requests
from marketing_bot.platforms import register
from marketing_bot.platforms.base import BasePublisher, PostResult

UGC_URL = "https://api.linkedin.com/v2/ugcPosts"


@register
class LinkedInPublisher(BasePublisher):
    name = "linkedin"

    def __init__(self, access_token: str, person_urn: str):
        self.access_token = access_token
        self.person_urn = person_urn

    def post(self, content: str, topic_slug: str) -> PostResult:
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        resp = requests.post(UGC_URL, headers=headers, data=json.dumps(payload), timeout=30)
        resp.raise_for_status()
        post_id = resp.headers.get("x-restli-id") or resp.json().get("id")
        return PostResult(
            post_id=post_id,
            url=f"https://www.linkedin.com/feed/update/{post_id}",
            platform="linkedin",
        )
