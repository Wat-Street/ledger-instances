"""
Usage example:
    # Create a ledger:
    python3 tests/test_integration/create_view_script.py --mode create \
                                                         --name myledger \
                                                         --tickers TSLA,MSFT \
                                                         --algo https://github.com/Wat-Street/money-making/tree/main/projects/orderbook_test_model \
                                                         --update 10 \
                                                         --end 2 \
                                                         --port 5001

    # View a ledger:
    python3 tests/test_integration/create_view_script.py --mode view \
                                                         --name myledger \
                                                         --port 5001
"""
import argparse
import sys
from urllib.parse import urljoin
import requests
import json

DEFAULT_PORT = 5000


def ensure_json_serializable(obj):
    """Helper function to ensure an object is JSON serializable."""
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [ensure_json_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    return obj


def create_ledger(base_url: str,
                  name: str,
                  tickers: str,
                  algo_path: str,
                  update_time: int,
                  end_duration: int):
    """Calls /create_ledger and returns (status_code, response_json)."""
    endpoint = urljoin(base_url, "/create_ledger")
    params = {
        "name": name,
        "tickerstotrack": tickers,
        "algo_path": algo_path,
        "updatetime": update_time,
        "end": end_duration,
    }
    resp = requests.get(endpoint, params=params, timeout=30)
    return resp.status_code, ensure_json_serializable(resp.json())


def view_ledger(base_url: str, name: str):
    """Calls /view_ledger and returns (status_code, response_json)."""
    endpoint = urljoin(base_url, "/view_ledger")
    resp = requests.get(endpoint, params={"name": name}, timeout=30)
    return resp.status_code, ensure_json_serializable(resp.json())


def parse_args():
    parser = argparse.ArgumentParser(description="Test ledger endpoints")
    parser.add_argument("--mode", choices=["create", "view"], required=True,
                        help="Operation mode: create a new ledger or view an existing one")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port number for the Flask server (default: {DEFAULT_PORT})")
    parser.add_argument("--name", required=True,
                        help="Ledger name (primary key)")
    
    # Arguments only needed for create mode
    create_group = parser.add_argument_group("Create mode arguments")
    create_group.add_argument("--tickers", default="AAPL,GOOG",
                        help="Comma-separated tickers (create mode only)")
    create_group.add_argument("--algo", default=(
        "https://github.com/Wat-Street/money-making/tree/main/projects/orderbook_test_model"),
                        help="GitHub URL of the trading algorithm (create mode only)")
    create_group.add_argument("--update", type=int, default=5,
                        help="Update interval in minutes (create mode only)")
    create_group.add_argument("--end", type=int, default=1,
                        help="Lifetime of instance in days (create mode only)")
    
    return parser.parse_args()


def main():
    args = parse_args()
    base_url = f"http://127.0.0.1:{args.port}"

    if args.mode == "create":
        print(f"[+] Creating ledger '{args.name}' …")
        status, data = create_ledger(
            base_url, args.name, args.tickers, args.algo, args.update, args.end)
        print(f"    HTTP {status}")
        print(f"    Response: {data}")
    else:  # view mode
        print(f"[+] Viewing ledger '{args.name}' …")
        status, data = view_ledger(base_url, args.name)
        print(f"    HTTP {status}")
        print(f"    Response: {data}")


if __name__ == "__main__":
    main()
