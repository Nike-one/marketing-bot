import pytest
from freezegun import freeze_time
from marketing_bot.db import init_db
from marketing_bot.cost_monitor import CostMonitor, PRIMARY_MODEL, FALLBACK_MODEL, DAILY_LIMIT


@freeze_time("2026-04-14")
def test_fresh_day_uses_primary(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    cm = CostMonitor(db)
    assert cm.current_model() == PRIMARY_MODEL


@freeze_time("2026-04-14")
def test_increment_below_limit_stays_primary(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    cm = CostMonitor(db)
    for _ in range(100):
        cm.increment()
    assert cm.current_model() == PRIMARY_MODEL


@freeze_time("2026-04-14")
def test_over_buffer_switches_to_fallback(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    cm = CostMonitor(db)
    for _ in range(DAILY_LIMIT - 50):
        cm.increment()
    assert cm.current_model() == FALLBACK_MODEL


@freeze_time("2026-04-14")
def test_over_hard_limit_raises(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    cm = CostMonitor(db)
    for _ in range(DAILY_LIMIT):
        cm.increment()
    with pytest.raises(RuntimeError, match="quota"):
        cm.check()
