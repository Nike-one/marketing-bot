import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


REQUIRED = [
    "GEMINI_API_KEY",
    "TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET",
    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET", "TWITTER_BEARER_TOKEN",
    "LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_PERSON_URN",
    "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
    "REDDIT_USERNAME", "REDDIT_PASSWORD",
    "BEEHIIV_API_KEY", "BEEHIIV_PUBLICATION_ID",
    "LANDING_PAGE_URL",
]


@dataclass
class Config:
    gemini_api_key: str
    twitter_consumer_key: str
    twitter_consumer_secret: str
    twitter_access_token: str
    twitter_access_secret: str
    twitter_bearer_token: str
    linkedin_client_id: str
    linkedin_client_secret: str
    linkedin_person_urn: str
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    reddit_username: str
    reddit_password: str
    beehiiv_api_key: str
    beehiiv_publication_id: str
    landing_page_url: str
    db_path: str
    log_path: str
    dry_run: bool

    @classmethod
    def from_env(cls) -> "Config":
        missing = [k for k in REQUIRED if not os.getenv(k)]
        if missing:
            raise ConfigError(f"Missing required env vars: {', '.join(missing)}")
        return cls(
            gemini_api_key=os.environ["GEMINI_API_KEY"],
            twitter_consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
            twitter_consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
            twitter_access_token=os.environ["TWITTER_ACCESS_TOKEN"],
            twitter_access_secret=os.environ["TWITTER_ACCESS_SECRET"],
            twitter_bearer_token=os.environ["TWITTER_BEARER_TOKEN"],
            linkedin_client_id=os.environ["LINKEDIN_CLIENT_ID"],
            linkedin_client_secret=os.environ["LINKEDIN_CLIENT_SECRET"],
            linkedin_person_urn=os.environ["LINKEDIN_PERSON_URN"],
            reddit_client_id=os.environ["REDDIT_CLIENT_ID"],
            reddit_client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ebook-marketing-bot/0.1"),
            reddit_username=os.environ["REDDIT_USERNAME"],
            reddit_password=os.environ["REDDIT_PASSWORD"],
            beehiiv_api_key=os.environ["BEEHIIV_API_KEY"],
            beehiiv_publication_id=os.environ["BEEHIIV_PUBLICATION_ID"],
            landing_page_url=os.environ["LANDING_PAGE_URL"],
            db_path=os.getenv("DB_PATH", "logs/posts.db"),
            log_path=os.getenv("LOG_PATH", "logs/errors.log"),
            dry_run=os.getenv("DRY_RUN", "true").lower() == "true",
        )
