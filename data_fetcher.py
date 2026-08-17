
import requests
import json


def fetch_ohlcv(ticker: str, period: str = "1y") -> list:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    URL = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1y&interval=1d"
    response = requests.get(URL, params=[], headers=HEADERS)
    response_as_dict = response.json()
    print(response_as_dict)


def save_to_csv(data: list, filepath: str) -> None:
    print("saving your data to CSV")