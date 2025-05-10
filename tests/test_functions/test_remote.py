import requests
import os
from dotenv import load_dotenv
load_dotenv()

# debug
API_KEY = os.environ.get("LEDGER_API_KEY")
if not API_KEY:
    raise ValueError("API key not found in .env")

headers = {
    "X-API-Key": API_KEY
}

create_params = {
    "name": "testledger_view",
    "tickerstotrack": "AAPL,GOOG",
    "algo_path": "https://github.com/Wat-Street/example-model",
    "updatetime": 5,
    "end": 1
}

# create the ledger
r_create = requests.get("http://localhost:5000/create_ledger", params=create_params, headers=headers)
print("CREATE STATUS:", r_create.status_code)
print("CREATE BODY:", r_create.text)

# view the ledger
view_params = {
    "name": "testledger_view"
}
r_view = requests.get("http://localhost:5000/view_ledger", params=view_params, headers=headers)
print("VIEW STATUS:", r_view.status_code)
print("VIEW BODY:", r_view.text)