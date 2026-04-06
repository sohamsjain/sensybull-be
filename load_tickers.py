import os
import requests
from dotenv import load_dotenv

from app import create_app, db
from app.models import Ticker

# Load env variables
load_dotenv()

USER_AGENT = os.getenv("SEC_USER_AGENT")

if not USER_AGENT:
    raise ValueError("SEC_USER_AGENT is not set in environment variables")

URL = "https://www.sec.gov/files/company_tickers.json"

headers = {
    "User-Agent": USER_AGENT
}

response = requests.get(URL, headers=headers)
response.raise_for_status()
data = response.json()

app = create_app()
app.app_context().push()

tickers = []

for item in data.values():
    symbol = item.get("ticker")
    name = item.get("title")
    cik = item.get("cik_str")

    if not symbol or not name:
        continue

    tickers.append(
        Ticker(symbol=symbol, name=name, cik=cik)
    )

db.session.bulk_save_objects(tickers)
db.session.commit()

print(f"Inserted {len(tickers)} tickers")