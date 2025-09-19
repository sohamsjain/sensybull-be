from app import create_app, db
from app.models import Ticker
import pandas as pd


df = pd.read_csv('us_common_stocks.csv')
df.dropna(inplace=True)

app = create_app()
app.app_context().push()

for index, row in df.iterrows():
    try:
        symbol = row['symbol']
        name = row['name']
        if not symbol or not name:
            print(f"Skipping row {index}: symbol or name is missing")
            print(index, row)
            continue
        ticker = Ticker(symbol=symbol, name=name)
        db.session.add(ticker)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
