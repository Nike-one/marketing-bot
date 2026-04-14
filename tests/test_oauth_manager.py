from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest
from marketing_bot.db import init_db
from marketing_bot.oauth_manager import OAuthManager, TokenRefreshError


def _now():
    return datetime.now(timezone.utc)


def test_save_and_load_token(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    mgr = OAuthManager(db)
    expires = (_now() + timedelta(hours=1)).isoformat()
    mgr.save("twitter", "access-1", "refresh-1", expires)
    tok = mgr.load("twitter")
    assert tok["access_token"] == "access-1"
    assert tok["refresh_token"] == "refresh-1"


def test_get_valid_token_returns_existing(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    mgr = OAuthManager(db)
    expires = (_now() + timedelta(hours=1)).isoformat()
    mgr.save("twitter", "access-1", "refresh-1", expires)
    assert mgr.get_valid_token("twitter", lambda r: None) == "access-1"


def test_get_valid_token_refreshes_when_expiring(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    mgr = OAuthManager(db)
    expires = (_now() + timedelta(minutes=2)).isoformat()  # within 5-min window
    mgr.save("twitter", "old-access", "refresh-1", expires)

    def refresh(refresh_token):
        assert refresh_token == "refresh-1"
        return {
            "access_token": "new-access",
            "refresh_token": "refresh-2",
            "expires_at": (_now() + timedelta(hours=1)).isoformat(),
        }

    token = mgr.get_valid_token("twitter", refresh)
    assert token == "new-access"
    assert mgr.load("twitter")["refresh_token"] == "refresh-2"


def test_refresh_failure_raises(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    mgr = OAuthManager(db)
    expires = (_now() + timedelta(minutes=1)).isoformat()
    mgr.save("twitter", "old", "refresh-x", expires)

    def bad_refresh(_):
        raise RuntimeError("boom")

    with pytest.raises(TokenRefreshError):
        mgr.get_valid_token("twitter", bad_refresh)
