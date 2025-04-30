import pytest
from unittest.mock import patch, MagicMock
from utils.ledger_utils import calculate_new_balance, get_current_price, calculate_total_value

def test_standard_case_calculate_new_balance():
    """Test calculate_new_balance for the expected use case"""
    balance = 10000
    trades = [
        {"type": "buy", "ticker": "AAPL", "price": 176, "quantity": 8},
        {"type": "sell", "ticker": "AAPL", "price": 157, "quantity": 7},
        {"type": "buy", "ticker": "GOOG", "price": 112, "quantity": 9}
    ]

    expected_balance = 8683
    assert calculate_new_balance(balance, trades) == expected_balance

def test_negative_balance_calculate_new_balance():
    """Test calculate_new_balance for negative balance case"""
    balance = 10000
    trades = [
        {"type": "buy", "ticker": "AAPL", "price": 176, "quantity": 16},
        {"type": "sell", "ticker": "AAPL", "price": 157, "quantity": 14},
        {"type": "buy", "ticker": "GOOG", "price": 143, "quantity": 24},
        {"type": "buy", "ticker": "NVDA", "price": 109, "quantity": 55}
    ]
    
    expected_balance = -45
    assert calculate_new_balance(balance, trades) == expected_balance

@patch('utils.ledger_utils.yf.Ticker')
def test_get_current_price(mock_ticker):
    """Test get_current_price by mocking yfinance"""
    mock_ticker_instance = MagicMock()
    mock_ticker.return_value = mock_ticker_instance

    mock_info_data = {"regularMarketPrice": 180.50}
    mock_ticker_instance.info = mock_info_data

    ticker_symbol = "MSFT"
    expected_price = 180.50

    current_price = get_current_price(ticker_symbol)

    mock_ticker.assert_called_once_with(ticker_symbol)
    assert current_price == expected_price

@patch('utils.ledger_utils.yf.Ticker')
def test_get_current_price_error_handling(mock_ticker):
    """Test get_current_price error handling when yfinance fails"""
    mock_ticker.side_effect = Exception("Simulated yfinance error")

    ticker_symbol = "ERROR_TICKER"

    with pytest.raises(RuntimeError):
        get_current_price(ticker_symbol)

    mock_ticker.assert_called_once_with(ticker_symbol)


def test_null_holdings_calculate_total_value():
    """Test calculate_total_value with no holdings"""
    balance = 10000
    holdings = {}

    expected_value = 10000
    assert calculate_total_value(holdings, balance) == expected_value

@patch('utils.ledger_utils.get_current_price')
def test_calculate_total_value_mocking_helper(mock_get_current_price):
    """Test calculate_total_value by mocking the get_current_price helper function for multiple tickers"""
    balance = 10000
    holdings = {
        "AAPL": 4,
        "MSFT": 3,
        "NVDA": 4,
        "AMD": 8
    }

    # Use side_effect to return different prices based on the ticker symbol
    def side_effect_for_get_price(ticker_symbol):
        if ticker_symbol == "AAPL":
            return 170.0
        elif ticker_symbol == "MSFT":
            return 260.0
        elif ticker_symbol == "NVDA":
            return 900.0
        elif ticker_symbol == "AMD":
            return 150.0
        else:
            raise ValueError(f"Unexpected error")

    mock_get_current_price.side_effect = side_effect_for_get_price

    expected_total_value = 16260
    
    total_value = calculate_total_value(holdings, balance)

    assert mock_get_current_price.call_count == len(holdings)
    mock_get_current_price.assert_any_call("AAPL")
    mock_get_current_price.assert_any_call("MSFT")
    mock_get_current_price.assert_any_call("NVDA")
    mock_get_current_price.assert_any_call("AMD")

    # Check if the calculated total value is correct
    assert total_value == expected_total_value

@patch('utils.ledger_utils.get_current_price')
def test_calculate_total_value_error_handling(mock_get_current_price):
    """Test calculate_total_value error handling when get_current_price fails."""
    balance = 10000
    holdings = {
        "AAPL": 4,
        "ERROR_TICKER": 3,
    }

    # Configure mock_get_current_price to raise an error for a specific ticker using side effect
    def side_effect_with_error(ticker_symbol):
        if ticker_symbol == "AAPL":
            return 170.0
        elif ticker_symbol == "ERROR_TICKER":
             raise RuntimeError(f"Expected error")
        else:
            return 100.0

    mock_get_current_price.side_effect = side_effect_with_error

    with pytest.raises(RuntimeError):
        calculate_total_value(holdings, balance)

    mock_get_current_price.assert_any_call("AAPL")
    mock_get_current_price.assert_any_call("ERROR_TICKER")