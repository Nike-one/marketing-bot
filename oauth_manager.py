from datetime import datetime, timedelta, timezone
from typing import Callable, Optional
from marketing_bot.db import get_connection


class TokenRefreshError(Exception):
    pass


REFRESH_WINDOW = timedelta(minutes=5)


class OAuthManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def save(self, platform: str, access_token: str,
             refresh_token: Optional[str], expires_at: Optional[str]) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                "INSERT INTO oauth_tokens(platform, access_token, refresh_token, expires_at) "
                "VALUES(?,?,?,?) ON CONFLICT(platform) DO UPDATE SET "
                "access_token=excluded.access_token, "
                "refresh_token=excluded.refresh_token, "
                "expires_at=excluded.expires_at",
                (platform, access_token, refresh_token, expires_at),
            )
            conn.commit()

    def load(self, platform: str) -> Optional[dict]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT access_token, refresh_token, expires_at "
                "FROM oauth_tokens WHERE platform=?",
                (platform,),
            ).fetchone()
        return dict(row) if row else None

    def get_valid_token(self, platform: str,
                        refresh_fn: Callable[[str], dict]) -> str:
        tok = self.load(platform)
        if tok is None:
            raise TokenRefreshError(f"no token stored for {platform}")
        if tok["expires_at"]:
            expires = datetime.fromisoformat(tok["expires_at"])
            if expires - datetime.now(timezone.utc) <= REFRESH_WINDOW:
                try:
                    new = refresh_fn(tok["refresh_token"])
                except Exception as e:
                    raise TokenRefreshError(f"{platform} refresh failed: {e}") from e
                self.save(platform, new["access_token"],
                          new.get("refresh_token", tok["refresh_token"]),
                          new.get("expires_at"))
                return new["access_token"]
        return tok["access_token"]
