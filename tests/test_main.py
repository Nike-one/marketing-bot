from unittest.mock import patch
import sys
from marketing_bot import main


@patch("marketing_bot.main.run_daily_job")
def test_cli_dry_run(mock_run, monkeypatch, env_setup):
    monkeypatch.setattr(sys, "argv", ["main.py", "--dry-run"])
    main.cli()
    mock_run.assert_called_once()
    assert mock_run.call_args.kwargs["dry_run"] is True


@patch("marketing_bot.main.run_weekly_job")
def test_cli_weekly(mock_run, monkeypatch, env_setup):
    monkeypatch.setattr(sys, "argv", ["main.py", "--weekly", "--dry-run"])
    main.cli()
    mock_run.assert_called_once()
