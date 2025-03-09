import yfinance as yf

def calculate_new_balance(current_balance, new_trades):
    """Calculate new balance based on trades"""
    for trade in new_trades:
        if trade["type"] == "buy":
            current_balance -= trade["price"] * trade["quantity"]
        else:  # sell
            current_balance += trade["price"] * trade["quantity"]
    return current_balance

def get_current_price(ticker):
    """Helper function to get current price using yfinance"""
    try:
        ticker_obj = yf.Ticker(ticker)
        current_price = ticker_obj.info["regularMarketPrice"]
        return float(current_price)
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        raise RuntimeError(f"Failed to get current price for {ticker}")

def calculate_total_value(holdings, balance):
    """Helper function to calculate total portfolio value"""
    if not holdings:
        return balance

    stock_value = 0
    for ticker, quantity in holdings.items():
        try:
            current_price = get_current_price(ticker)
            stock_value += quantity * current_price
        except Exception as e:
            print(f"Error calculating value for {ticker}: {e}")
            raise RuntimeError(
                f"Failed to calculate portfolio value due to error with {ticker}"
            )

    return balance + stock_value