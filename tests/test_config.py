import os
import pytest
from marketing_bot.config import Config, ConfigError


def test_config_loads_required_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "tc")
    monkeypatch.setenv("TWITTER_CONSUMER_SECRET", "ts")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "tat")
    monkeypatch.setenv("TWITTER_ACCESS_SECRET", "tas")
    monkeypatch.setenv("TWITTER_BEARER_TOKEN", "tbt")
    monkeypatch.setenv("LINKEDIN_CLIENT_ID", "lci")
    monkeypatch.setenv("LINKEDIN_CLIENT_SECRET", "lcs")
    monkeypatch.setenv("LINKEDIN_PERSON_URN", "urn:li:person:abc")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "rci")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "rcs")
    monkeypatch.setenv("REDDIT_USERNAME", "ru")
    monkeypatch.setenv("REDDIT_PASSWORD", "rp")
    monkeypatch.setenv("BEEHIIV_API_KEY", "bk")
    monkeypatch.setenv("BEEHIIV_PUBLICATION_ID", "bp")
    monkeypatch.setenv("LANDING_PAGE_URL", "https://example.com")

    cfg = Config.from_env()
    assert cfg.gemini_api_key == "g-test"
    assert cfg.dry_run is True  # default
    assert cfg.landing_page_url == "https://example.com"


def test_config_missing_key_raises(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ConfigError, match="GEMINI_API_KEY"):
        Config.from_env()


def test_dry_run_false_when_explicit(monkeypatch):
    for k in ["GEMINI_API_KEY","TWITTER_CONSUMER_KEY","TWITTER_CONSUMER_SECRET",
              "TWITTER_ACCESS_TOKEN","TWITTER_ACCESS_SECRET","TWITTER_BEARER_TOKEN",
              "LINKEDIN_CLIENT_ID","LINKEDIN_CLIENT_SECRET","LINKEDIN_PERSON_URN",
              "REDDIT_CLIENT_ID","REDDIT_CLIENT_SECRET","REDDIT_USERNAME",
              "REDDIT_PASSWORD","BEEHIIV_API_KEY","BEEHIIV_PUBLICATION_ID",
              "LANDING_PAGE_URL"]:
        monkeypatch.setenv(k, "x")
    monkeypatch.setenv("DRY_RUN", "false")
    cfg = Config.from_env()
    assert cfg.dry_run is False
