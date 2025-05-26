import time
from datetime import datetime, timedelta

from utils.db_config import get_db_connection, ledger
from utils.docker_utils import (
    pull_image_from_registry,
    run_docker_container,
    stop_docker_container,
)
from huey import RedisHuey
from sqlalchemy import select, update

huey = RedisHuey("ledger-tasks", host="localhost", port=6379)


@huey.task()
def execute_trade_cycle(
    name, registry_image_path, update_time, end_duration, start_time
):
    """
    Execute a single trade and schedule the next one if not past the end time.
    This task recursively schedules itself
    """
    end_time = start_time + timedelta(days=end_duration)

    # Check if the current time is past the end time
    if datetime.now() > end_time:
        print(f"Ledger '{name}' has reached its end time. Stopping cycle.")
        return

    # Check if ledger still exists in db
    with get_db_connection() as conn:
        stmt = select(ledger.c.name).where(ledger.c.name == name)
        result = conn.execute(stmt).fetchone()

        if not result:
            print(f"Ledger '{name}' no longer exists. Stopping cycle.")
            return

    try:
        print(f"Executing trade for ledger '{name}'")

        # Pull the latest image from registry
        pull_image_from_registry(registry_image_path)

        # Run the container and get output
        output = run_docker_container(
            image_name=registry_image_path, command=None, remove_after=True
        )

        # Process the model output
        if isinstance(output, bytes):
            logs = output.decode("utf-8")
        else:
            logs = str(output)

        print(f"Trade execution completed for '{name}'. Logs: {logs}")

        # TODO: Parse the model output and update the ledger
        # This should call the update_ledger endpoint with the model's trade results
        # We might want to add a function to parse the model output and extract trades/holdings

    except Exception as e:
        print(f"Error executing trade for ledger '{name}': {e}")

    next_run = datetime.now() + timedelta(minutes=update_time)
    print(f"Scheduling next trade for '{name}' at {next_run}")

    execute_trade_cycle.schedule(
        args=(name, registry_image_path, update_time, end_duration, start_time),
        eta=next_run,
    )


@huey.task()
def run_ledger_trade(name, registry_image_path, update_time, end_duration):
    """
    Start the trading cycle for a ledger.
    This is the entry point task that initiates the recursive cycle.
    """
    start_time = datetime.now()
    print(f"Initiating trading cycle for ledger '{name}' at {start_time}")

    execute_trade_cycle(
        name, registry_image_path, update_time, end_duration, start_time
    )

    return {
        "success": True,
        "message": f"Trading cycle initiated for '{name}'",
        "start_time": start_time.isoformat(),
        "update_interval_minutes": update_time,
        "end_duration_days": end_duration,
        "estimated_end_time": (start_time + timedelta(days=end_duration)).isoformat(),
    }
