from utils.tasks import run_ledger_trade, execute_trade_cycle

def test_run_ledger_trade(mock_execute_trade_cycle, sample_inputs):
    """Tests initiating a trading cycle."""
    result = run_ledger_trade(
        sample_inputs["name"],
        sample_inputs["image_path"],
        sample_inputs["update_time"],
        sample_inputs["end_duration"]
    )

    assert result["success"] is True
    assert result["message"] == f"Trading cycle initiated for '{sample_inputs['name']}'"
    assert result["update_interval_minutes"] == sample_inputs["update_time"]
    assert result["end_duration_days"] == sample_inputs["end_duration"]

    mock_execute_trade_cycle.assert_called_once_with(
        sample_inputs["name"],
        sample_inputs["image_path"],
        sample_inputs["update_time"],
        sample_inputs["end_duration"],
        result["start_time"]
    )

def test_execute_trade_cycle(mock_schedule, mock_docker, sample_inputs):
    """Tests executing a trade cycle and scheduling the next one."""
    execute_trade_cycle(
        sample_inputs["name"],
        sample_inputs["image_path"],
        sample_inputs["update_time"],
        sample_inputs["end_duration"],
        sample_inputs["start_time"]
    )

    mock_docker.assert_called_once_with(image_name=sample_inputs["image_path"], command=None)
    mock_schedule.assert_called_once()