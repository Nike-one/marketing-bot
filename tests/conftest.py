import pytest


@pytest.fixture
def env_setup(monkeypatch):
    env = {
        "GEMINI_API_KEY": "g-test",
        "TWITTER_CONSUMER_KEY": "tck", "TWITTER_CONSUMER_SECRET": "tcs",
        "TWITTER_ACCESS_TOKEN": "tat", "TWITTER_ACCESS_SECRET": "tas",
        "TWITTER_BEARER_TOKEN": "tbt",
        "LINKEDIN_CLIENT_ID": "lci", "LINKEDIN_CLIENT_SECRET": "lcs",
        "LINKEDIN_PERSON_URN": "urn:li:person:abc",
        "REDDIT_CLIENT_ID": "rci", "REDDIT_CLIENT_SECRET": "rcs",
        "REDDIT_USERNAME": "ru", "REDDIT_PASSWORD": "rp",
        "BEEHIIV_API_KEY": "bk", "BEEHIIV_PUBLICATION_ID": "bp",
        "LANDING_PAGE_URL": "https://example.com",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return env
