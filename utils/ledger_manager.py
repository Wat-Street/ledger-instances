from sqlalchemy import select
from utils.db_config import get_db_connection, ledger
from utils.tasks import run_ledger_trade

def start_ledger(name):
    """
    Starts a ledger instance.

    Args:
        name (str): Name of the ledger to start.

    Returns:
        dict: A message indicating success or failure.
        int: HTTP status code.
    """
    with get_db_connection() as conn:
        stmt = select(
            ledger.c.name,
            ledger.c.update_time,
            ledger.c.algo_link,
            ledger.c.end_duration
        ).where(ledger.c.name == name)
        result = conn.execute(stmt).fetchone()

    if not result:
        return {"Error": f"Ledger {name} does not exist."}, 404

    run_ledger_trade(result.name, result.algo_link, result.update_time, result.end_duration)

    return {f"Ledger {name} will now start"}, 202