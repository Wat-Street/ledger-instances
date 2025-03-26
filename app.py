import os
import glob
from flask import Flask, jsonify, request
from sqlalchemy import select, insert, delete, update
from utils.db_config import get_db_connection, ledger
from utils.docker_utils import (
    build_docker_image,
    run_docker_container,
    stop_docker_container,
)
from utils.github_utils import recursive_repo_clone
from utils.ledger_utils import (
    calculate_new_balance,
    get_current_price,
    calculate_total_value,
)
from utils.ledger_manager import start_ledger
from datetime import datetime, timezone
import yfinance as yf

API_KEY = os.environ.get("LEDGER_API_KEY")

ORDERBOOKS_TABLE_NAME = "order_books_v2"


app = Flask(__name__)


@app.route("/create_ledger", methods=["GET"])
def create_ledger():
    """
    This endpoint creates a ledger instance. It expects the following arguments:
        - name: unique ledger name
        - tickerstotrack: tickers (e.g. (AAPL, GOOG))
        - algo_path: GitHub URL. Specific branch and filepath are supported, but optional. (e.g. 'https://github.com/Wat-Street/money-making/tree/main/projects/ledger_test_model')
        - updatetime: time interval for updates (minutes)
        - end: lifespan of instance (days)
    It creates an entry in the database for the ledger, as well as generates a Docker image, saved as a tar file in [TODO directory]
    """
    name = request.args.get("name")
    tickers_to_track = request.args.get("tickerstotrack", "").split(",")
    algo_path = request.args.get("algo_path")
    update_time = request.args.get("updatetime", type=int)
    end_duration = request.args.get("end", type=int)

    # input validation
    if not name or not algo_path or not update_time or not end_duration:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # pull algorithm into local
        temp_model_store = "temporary_model_storage"
        recursive_repo_clone(algo_path, temp_model_store)
        print(f"Successfully pulled algo {name} repo to temporary model storage")

        # paths to pull algorithm and store image
        path_to_algo = f"{temp_model_store}"
        path_to_image_store = f"docker_images/{name}.tar"

        # check if image with this name already exists. If so, delete it first.
        # Then, build it from the path_to_algo.
        if os.path.exists(path_to_image_store):
            os.remove(path_to_image_store)

        # build docker image
        image = build_docker_image(name, path_to_algo)

        # save image as .tar to path_to_image_store
        with open(path_to_image_store, "wb") as image_tar:
            for chunk in image.save():
                image_tar.write(chunk)
        print(f"Saved Docker image for '{name}' to {path_to_image_store}")

        # delete the temporary model storage folder after image build
        for file in glob.glob("{temp_model_store}/*"):
            os.remove(file)
        print(f"Successfully removed contents of temporary model storage")

        # save the ledger in the database
        with get_db_connection() as conn:
            stmt = insert(ledger).values(
                name=name,
                tickers_to_track=tickers_to_track,
                algo_link=algo_path,
                update_time=update_time,
                end_duration=end_duration,
            )
            conn.execute(stmt)
            conn.commit()

        # start ledger after creation - use internal call directly instead of endpoint
        response, status_code = start_ledger(name)

        return (
            jsonify(
                {"info": f"Ledger '{name}' has been created.", "start_status": response}
            ),
            status_code,
        )

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/view_ledger", methods=["GET"])
def view_ledger():
    """
    This endpoint allows you to view a ledger.
    Expects: name of algorithm.
    Returns: a json containing the trades, holdings, value history, and balance of the ledger.
    """
    name = request.args.get("name")

    # retrieve ledger from database
    with get_db_connection() as conn:
        stmt = select(
            ledger.c.trades, ledger.c.holding, ledger.c.value, ledger.c.balance
        ).where(ledger.c.name == name)
        result = conn.execute(stmt).fetchone()

    # return result if not empty, 404 otherwise
    if result:
        return jsonify(
            {
                "trades": result.trades,
                "holding": result.holding,
                "value": result.value,
                "balance": result.balance,
            }
        )
    return {"error": "Ledger not found"}, 404


@app.route("/delete_ledger", methods=["GET"])
def delete_ledger():
    """
    This endpoint deletes a ledger instance.
    Expects: name of algorithm.
    This function deletes the ledger instance from the database. The image persists in the docker_images folder.
    """
    name = request.args.get("name")

    with get_db_connection() as conn:
        # check if the ledger exists in the database
        stmt = select(ledger.c.name).where(ledger.c.name == name)
        result = conn.execute(stmt).fetchone()

        print(result)
        print(f"DELETE FROM {ORDERBOOKS_TABLE_NAME} WHERE name = '{name}';")

        if not result:
            return {
                "Error": f"You are trying to delete a ledger called '{name}' that does not exist."
            }, 404

        # delete the ledger from the table
        stmt = delete(ledger).where(ledger.c.name == name)
        conn.execute(stmt)
        conn.commit()

    return {"Info": f"Deleted ledger named '{name}'"}


@app.route("/update_ledger", methods=["PATCH"])
def update_ledger():
    """
    PRIVATE ENDPOINT - Requires valid API key.
    This endpoint updates a ledger instance. It expects the following arguments:
    - name: name of the algorithm
    - trades: list of trades
    - value: dict of current stock values
    - balance: current balance
    This function takes the output of a model's trade function and updates the corresponding ledger instance's record.
    """
    # validate API key
    if not validate_api_key():
        return jsonify({"error": "Unauthorized access. Valid API key required."}), 401

    data = request.json
    name = data.get("name")
    new_trades = data.get("trades")
    new_holdings = data.get("holding")
    # pass to view_ledger so that timestamp can be displayed
    timestamp = datetime.now(timezone.utc)

    # validate required fields
    if None in [name, new_trades, new_holdings]:
        return (
            jsonify(
                {
                    "error": "Missing required fields. Please provide name, trades, and holding."
                }
            ),
            400,
        )

    try:
        with get_db_connection() as conn:
            # fetch current ledger data
            stmt = select(ledger).where(ledger.c.name == name)
            result = conn.execute(stmt).fetchone()

            if not result:
                return (
                    jsonify(
                        {
                            "error": f"You are trying to update a ledger called '{name}' that does not exist."
                        }
                    ),
                    404,
                )

            # update trades
            updated_trades = result.trades + new_trades

            # calculate new balance based on trades
            new_balance = calculate_new_balance(result.balance, new_trades)

            # calculate current total value
            current_value = calculate_total_value(new_holdings, new_balance)

            # update ledger in database
            update_stmt = (
                update(ledger)
                .where(ledger.c.name == name)
                .values(
                    trades=updated_trades,
                    holding=new_holdings,
                    balance=new_balance,
                    value={str(timestamp): current_value, **result.value},
                )
            )
            conn.execute(update_stmt)
            conn.commit()

        return jsonify({"message": f"Ledger '{name}' updated successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/start_ledger", methods=["GET"])
def start_ledger_endpoint():
    """
    PRIVATE ENDPOINT - Requires valid API key.
    This endpoint starts a ledger instance.
    Expects: name of the ledger to start.
    """
    # Validate API key
    if not validate_api_key():
        return jsonify({"error": "Unauthorized access. Valid API key required."}), 401

    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing required parameter: name"}), 400

    response, status_code = start_ledger(name)
    return jsonify(response), status_code


def validate_api_key():
    """Validates the API key provided in the request headers."""
    # Get API key from header
    provided_key = request.headers.get("X-API-Key")

    # Compare with stored API key
    if not provided_key or provided_key != API_KEY:
        return False
    return True


if __name__ == "__main__":
    app.run()
