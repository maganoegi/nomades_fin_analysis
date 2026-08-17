
import requests


def fetch_ohlcv(ticker: str, period: str = "1y") -> list:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    response = requests.get(url, params=params, headers=HEADERS)

    print("fetching data...")

def save_to_csv(data: list, filepath: str) -> None:
    print("saving your data to CSV")