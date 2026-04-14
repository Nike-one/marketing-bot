import sqlite3
from marketing_bot.db import init_db, get_connection


def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    conn = sqlite3.connect(str(db_path))
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    assert "posts" in tables
    assert "engagement" in tables
    assert "oauth_tokens" in tables
    assert "gemini_usage" in tables
    conn.close()


def test_posts_table_schema(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    conn = sqlite3.connect(str(db_path))
    cols = {r[1] for r in conn.execute("PRAGMA table_info(posts)")}
    assert cols == {"id", "platform", "topic", "post_id", "content", "posted_at"}
    conn.close()


def test_get_connection_returns_connection(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    conn = get_connection(str(db_path))
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory == sqlite3.Row
    conn.close()
