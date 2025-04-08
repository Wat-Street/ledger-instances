# test_scheduling.py
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from utils.tasks import run_ledger_trade, execute_trade_cycle

# test 1: call execute_trade_cycle with correct arguments
@patch("utils.tasks.execute_trade_cycle")
def test_run_ledger_trade_starts_cycle(mock_execute):
    result = run_ledger_trade.call_local("ledger1", "/img1", 15, 2)

    # assert that result was called with exepected args
    mock_execute.assert_called_once()
    args = mock_execute.call_args[0]
    assert args[0] == "ledger1"
    assert args[1] == "/img1"
    assert args[2] == 15
    assert args[3] == 2
    assert isinstance(args[4], datetime)

    assert result["success"] is True


# test 2: calls docker and schedules the next run
@patch("utils.tasks.execute_trade_cycle.schedule", create=True)
@patch("utils.tasks.run_docker_container")
@patch("utils.tasks.get_db_connection")
@patch("utils.tasks.datetime")
def test_execute_trade_cycle_schedules_next(mock_datetime, mock_db, mock_docker, mock_schedule):
    # simulated current time
    now = datetime(2025, 4, 5, 12, 0)
    # override the curent datetime for testing
    mock_datetime.now.return_value = now
    # forward all arguments to the real datetime constructor to preserve normal behavior when mocking
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    # mock db connection and response
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = ("ledger1",)
    mock_db.return_value.__enter__.return_value = mock_conn
    mock_docker.return_value = b"docker logs"

    # simulate ledger that started trading 5 mins ago
    start_time = now - timedelta(minutes=5)
    execute_trade_cycle.call_local("ledger1", "/img", 10, 1, start_time)

    mock_docker.assert_called_once_with(image_name="/img", command=None)
    mock_schedule.assert_called_once()


# test 3: execute_trade_cycle exits if we're past the end time
@patch("utils.tasks.datetime")
def test_execute_trade_cycle_past_end_time(mock_datetime):
    now = datetime(2025, 4, 5, 12, 0)
    mock_datetime.now.return_value = now
    # forward all arguments to the real datetime constructor to preserve normal behavior when mocking
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*a, **k)

    start_time = datetime(2000, 1, 1)
    result = execute_trade_cycle.call_local("ledger1", "image", 10, 1, start_time)
    assert result is None