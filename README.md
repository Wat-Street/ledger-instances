# Ledger Instances

## Overview
Ledger instances allow the ML team to forward-test their algorithms. An API and database are hosted on the PC that allows members to create instances of Ledgers and tie specific algorithms to trade on them.

## API Features
1. **`create_ledger`**
    To create a ledger.

    Expected arguments:
    - `name`: **unique** name of algorithm
    - `tickerstotrack`: two tickers (e.g. (AAPL, GOOG))
    - `algo_path`: path to algorithm from the `projects` directory (ex. algo_path=harv-extension)
    - `updatetime`: time interval for updates (minutes)
    - `end`: lifespan of instance (days)

    Example command: `https://watstreet/create_ledger?name=krishalgo&tickerstotrack=AAPL,GOOG&algo_path=https://github.com/Wat-Street/money-making/tree/main/projects/ledger_test_model&updatetime=1&end=100`

2. **`view_ledger`**
    To retrieve details of a specific ledger.

    Expected arguments:
    - `name`: name of ledger.

    Example command: `https://watstreet/view_ledger?name=krishalgo`

3. **`delete_ledger`**
    To delete a ledger.

    Expected arguments:
    - `name`: name of ledger.
  
    Example command: `https://watstreet/delete_ledger?name=krishalgo`

4. **`update_ledger`** (Protected Endpoint)
   To update a ledger's trades and holdings. Requires API key in X-API-Key header.

    Expected arguments (JSON body):

    - `name`: name of ledger
    - `trades`: list of new trades
    - `holding`: updated holdings dictionary

    Example command:

    ```bash
    curl -X PATCH https://watstreet/update_ledger \
         -H "Content-Type: application/json" \
         -H "X-API-Key: your-api-key" \
         -d '{
           "name": "krishalgo",
           "trades": [{"type": "buy", "ticker": "AAPL", "price": 176, "quantity": 8}],
           "holding": {"AAPL": 8, "GOOG": 0}
         }'
    ```

5. **`start_ledger`** (Protected Endpoint)
   To start a ledger instance. Requires API key in X-API-Key header.

    Expected arguments:

    - `name`: name of ledger to start

    Example command:

    ```bash
    curl -X GET https://watstreet/start_ledger?name=krishalgo \
         -H "X-API-Key: your-api-key"
    ```

## Interaction with Models
The two standard commands are:
- `trade()`: runs the algorithm and, based on current ownership of stocks and balance, will return a trade
- `update_book_status(book_status)`: gives the trading algorithm the info it needs to make trades (portfolio and balance)

Thus, models' interfaces should look like so:
```
class Model:
    def update_book_status(self, book_status):
        """Gives the trading algorithm the info it needs to make trades (portfolio and balance, retrieved from the view_book endpoint)"""
        pass

    def trade(self):
        """Runs the algorithm and, based on current ownership of stocks and balance, will return a trade. The result of this trade is updated into the Ledger."""
        pass
```

Some considerations:
- It is the responsibility of the algorithm to not violate the ledger (ie. sell more than you own or buy more than the money you have)
- In case the algorithm violates the ledger, return an exception. The algorithm must be able to deal with these standard exceptions. 

## Architecture Diagrams
### User Endpoints
![Ledger Software Architecture](https://github.com/user-attachments/assets/2a9cac2a-7bd0-446c-8cdb-fec982467540)

### Model Interaction
![Ledger Software Architecture Interaction (1)](https://github.com/user-attachments/assets/34e724dd-d48e-419f-b9f0-fefa9386c170)

## Data Formats (TODO:)
**KEEP THIS UPDATED AT ALL TIMES.** 
#### Basic Model Output
```
{
  "trades": [
    {"type": "buy", "ticker": "AAPL", "price": 176, "quantity": 8},
    {"type": "sell", "ticker": "AAPL", "price": 157, "quantity": 7},
    {"type": "buy", "ticker": "GOOG", "price": 112, "quantity": 9}
  ],
}
```


#### View Book
```
{
  "trades": [
    {"type": "buy", "ticker": "AAPL", "price": 176, "quantity": 8},
    {"type": "sell", "ticker": "AAPL", "price": 157, "quantity": 7},
    {"type": "buy", "ticker": "GOOG", "price": 112, "quantity": 9}
  ],
  "holding": {
    "GOOG": 9,
    "AAPL": 1,
  },
  "value": [
        "1999-01-08 04:05:06": 100000,
        "1999-01-08 04:10:06": 100800,
        "1999-01-08 04:15:06": 109000,
  ],
  "balance": 96,485
}
```

## Design Components (wip)
1. API Backend (Flask)
2. Database (PostgreSQL, in Rebbi's local env)
Database name: `postgres` for now
Tables: (wip)
- `order_books_v2`
- `trades`
3. Scheduler (Celery?) (wip)






