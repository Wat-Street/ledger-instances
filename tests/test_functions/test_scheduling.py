import pytest
from app import run_ledger_trade,  execute_trade_cycle

def test_run_ledger_trade(sample_ledger):
    result = run_ledger_trade(**sample_ledger)
    assert result["success"] is True
    assert "Trading cycle initiated" in result["message"]

def test_expired_ledger_cycle(expired_ledger):
    result = execute_trade_cycle(**expired_ledger)
    assert result is None  