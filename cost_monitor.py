from datetime import date
from marketing_bot.db import get_connection

PRIMARY_MODEL = "gemini-1.5-flash"
FALLBACK_MODEL = "gemini-1.5-flash-8b"
DAILY_LIMIT = 1400  # buffer below 1500
FALLBACK_THRESHOLD = DAILY_LIMIT - 100


class CostMonitor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _today(self) -> str:
        return date.today().isoformat()

    def _count(self) -> int:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT request_count FROM gemini_usage WHERE day=?",
                (self._today(),),
            ).fetchone()
        return row["request_count"] if row else 0

    def increment(self) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                "INSERT INTO gemini_usage(day, request_count) VALUES(?, 1) "
                "ON CONFLICT(day) DO UPDATE SET request_count=request_count+1",
                (self._today(),),
            )
            conn.commit()

    def current_model(self) -> str:
        return FALLBACK_MODEL if self._count() >= FALLBACK_THRESHOLD else PRIMARY_MODEL

    def check(self) -> None:
        if self._count() >= DAILY_LIMIT:
            raise RuntimeError(f"Gemini daily quota exhausted ({DAILY_LIMIT})")
