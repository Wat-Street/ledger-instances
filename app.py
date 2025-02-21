import os, glob
from flask import Flask, jsonify, request
from sqlalchemy import select, insert, delete
from utils.db_config import get_db_connection, ledger
from utils.docker_utils import build_docker_image, run_docker_container, stop_docker_container
from utils.github_utils import recursive_repo_clone

ORDERBOOKS_TABLE_NAME = 'order_books_v2'


app = Flask(__name__)


@app.route('/create_ledger', methods=['GET'])
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
    name = request.args.get('name')
    tickers_to_track = request.args.get('tickerstotrack', '').split(',')
    algo_path = request.args.get('algo_path')
    update_time = request.args.get('updatetime', type=int)
    end_duration = request.args.get('end', type=int)

    # input validation
    if not name or not algo_path or not update_time or not end_duration:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # pull algorithm into local
        temp_model_store = "temporary_model_storage"
        recursive_repo_clone(algo_path, temp_model_store)
        print(f'Successfully pulled algo {name} repo to temporary model storage')

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
        with open(path_to_image_store, 'wb') as image_tar:
            for chunk in image.save():
                image_tar.write(chunk)
        print(f"Saved Docker image for '{name}' to {path_to_image_store}")

        # delete the temporary model storage folder after image build
        for file in glob.glob('{temp_model_store}/*'):
            os.remove(file)
        print(f'Successfully removed contents of temporary model storage')

        # save the ledger in the database
        with get_db_connection() as conn:
            stmt = insert(ledger).values(
                name=name,
                tickers_to_track=tickers_to_track,
                algo_link=algo_path,
                update_time=update_time,
                end_duration=end_duration
            )
            conn.execute(stmt)
            conn.commit()

        return jsonify({'info': f"Ledger '{name}' has been created."}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/view_ledger", methods=["GET"])
def view_ledger():
    """
    This endpoint allows you to view a ledger.
    Expects: name of algorithm.
    Returns: a json containing the trades, worth, and balance of the ledger.
    """
    name = request.args.get('name')

    # retrieve ledger from database
    with get_db_connection() as conn:
        stmt = select(ledger.c.trades, ledger.c.worth,
                        ledger.c.balance).where(ledger.c.name == name)
        result = conn.execute(stmt).fetchone()

    # return result if not empty, 404 otherwise
    if result:
        return jsonify({
            "trades": result.trades,
            "worth": result.worth,
            "balance": result.balance,
        })
    return {"error": "Ledger not found"}, 404


@app.route("/delete_ledger", methods=['GET'])
def delete_ledger():
    """
    This endpoint deletes a ledger instance.
    Expects: name of algorithm.
    This function deletes the ledger instance from the database. The image persists in the docker_images folder.
    """
    name = request.args.get('name')

    with get_db_connection() as conn:
        # check if the ledger exists in the database
        stmt = select(ledger.c.name).where(ledger.c.name == name)
        result = conn.execute(stmt).fetchone()

        print(result)
        print(f"DELETE FROM {ORDERBOOKS_TABLE_NAME} WHERE name = '{name}';")

        if not result:
            return {"Error": f"You are trying to delete a ledger called '{name}' that does not exist."}, 404

        # delete the ledger from the table
        stmt = delete(ledger).where(ledger.c.name == name)
        conn.execute(stmt)
        conn.commit()

    return {'Info': f"Deleted ledger named '{name}'"}


if __name__ == "__main__":
    app.run()
