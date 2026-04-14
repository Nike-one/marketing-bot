from datetime import date
from marketing_bot.db import init_db, get_connection
from marketing_bot.idempotency import already_posted, record_post


def test_not_posted_returns_false(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    assert already_posted(db, "sip-basics", "twitter", date(2026, 4, 14)) is False


def test_record_then_check_returns_true(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    record_post(db, "twitter", "sip-basics", "tw-123", "hello", "2026-04-14T09:00:00")
    assert already_posted(db, "sip-basics", "twitter", date(2026, 4, 14)) is True


def test_different_day_returns_false(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    record_post(db, "twitter", "sip-basics", "tw-123", "hello", "2026-04-14T09:00:00")
    assert already_posted(db, "sip-basics", "twitter", date(2026, 4, 15)) is False


def test_different_platform_returns_false(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    record_post(db, "twitter", "sip-basics", "tw-123", "hello", "2026-04-14T09:00:00")
    assert already_posted(db, "sip-basics", "linkedin", date(2026, 4, 14)) is False
