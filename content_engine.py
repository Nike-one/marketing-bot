from datetime import date, timedelta
from typing import List, Tuple
import google.generativeai as genai
from marketing_bot.db import get_connection
from marketing_bot.cost_monitor import CostMonitor

TWEET_PROMPT = """Write a 3-tweet thread about "{title}".
Hook: {hook}
Audience: young Indian professional (20–30), early career, first job or couple years in.
Tone: smart friend who knows finance. Hinglish-friendly English (casual, relatable, but not forced slang).
Use ₹ amounts. Reference Indian context (EPF, SIP, FD, ITR, HRA, NPS) where relevant.
Each tweet max 270 characters. Separate tweets with "---".
No hashtag spam — max 2 relevant hashtags in the final tweet only.
Do not include URLs or links.
"""

LINKEDIN_PROMPT = """Write a LinkedIn post about "{title}".
Hook: {hook}
Audience: young Indian professional (20–30), early career.
Tone: professional but relatable, not corporate. Hinglish-friendly English.
Length: 150–300 words. Use line breaks for readability.
Use ₹ amounts. Reference Indian context (EPF, SIP, FD, ITR, HRA, NPS) where relevant.
End with a soft CTA pointing to the landing page: {landing_url}
"""

REDDIT_PROMPT = """Write a Reddit post for r/personalfinanceindia about "{title}".
Hook: {hook}
Audience: young Indian professional (20–30), early career.
Tone: value-first, no promotion, like a helpful community member.
Format: title line, then body. Title max 300 chars.
Body: 300–600 words, long-form, actionable.
Use ₹ amounts. Reference Indian context.
Do NOT include any URLs, links, or "check out my" language. Pure value.
Output format:
TITLE: <title>
BODY:
<body>
"""


def pick_next_topic(db_path: str, topics: list, recent_days: int = 50) -> dict:
    cutoff = (date.today() - timedelta(days=recent_days)).isoformat()
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT topic, MAX(posted_at) as last "
            "FROM posts WHERE substr(posted_at,1,10) >= ? GROUP BY topic",
            (cutoff,),
        ).fetchall()
    recent = {r["topic"]: r["last"] for r in rows}
    unused = [t for t in topics if t["slug"] not in recent]
    if unused:
        return unused[0]
    return min(topics, key=lambda t: recent.get(t["slug"], ""))


class ContentEngine:
    def __init__(self, api_key: str, db_path: str, landing_url: str):
        genai.configure(api_key=api_key)
        self.db_path = db_path
        self.landing_url = landing_url
        self.cost_monitor = CostMonitor(db_path)

    def _generate(self, prompt: str) -> str:
        self.cost_monitor.check()
        model = genai.GenerativeModel(self.cost_monitor.current_model())
        result = model.generate_content(prompt)
        self.cost_monitor.increment()
        return result.text.strip()

    def generate_tweet_thread(self, topic: dict) -> List[str]:
        prompt = TWEET_PROMPT.format(title=topic["title"], hook=topic["hook"])
        text = self._generate(prompt)
        tweets = [t.strip() for t in text.split("---") if t.strip()]
        return tweets[:3]

    def generate_linkedin_post(self, topic: dict) -> str:
        prompt = LINKEDIN_PROMPT.format(
            title=topic["title"], hook=topic["hook"], landing_url=self.landing_url
        )
        return self._generate(prompt)

    def generate_reddit_post(self, topic: dict) -> Tuple[str, str]:
        prompt = REDDIT_PROMPT.format(title=topic["title"], hook=topic["hook"])
        text = self._generate(prompt)
        title = ""
        body_lines = []
        in_body = False
        for line in text.splitlines():
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()
        title = self._strip_links(title)
        body = self._strip_links(body)
        return title, body

    def generate_newsletter(self, topic: dict) -> str:
        prompt = (
            f"Write a long-form newsletter (500-800 words) about \"{topic['title']}\". "
            f"Hook: {topic['hook']}. Audience: young Indian professional (20-30). "
            f"Tone: friendly, Hinglish-friendly English. Use ₹ amounts and Indian context. "
            f"End with CTA: ebook dropping soon, join waitlist at {self.landing_url}"
        )
        return self._generate(prompt)

    @staticmethod
    def _strip_links(text: str) -> str:
        import re
        return re.sub(r"https?://\S+", "", text).strip()
