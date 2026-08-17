# Python Financial Analysis

Build a stock analysis pipeline from scratch using **pure Python**.  
No pandas. No numpy. Just the standard library, `requests`, and `matplotlib`.

By the end you will have a script that downloads real market data, calculates
technical indicators, generates trading signals, and produces a chart like this:

```
Yahoo Finance API  →  CSV file  →  Feature engineering  →  Signals  →  Chart
```

---

## Project files

| File | What it contains |
|------|-----------------|
| `data_fetcher.py` | **Part 1** — fetch from Yahoo Finance via HTTP |
| `feature_engineering.py` | **Part 2** — SMA, RSI, daily return + trading signals |
| `plotter.py` | **Part 3** — matplotlib three-panel figure |
| `main.py` | Entrypoint — runs the full pipeline end to end |
| `requirements.txt` | Python dependencies |

Work through the parts in order.  Each part has a **Task** telling you exactly
what function to write and what signature it must have.

> `data_fetcher_requests.py` is provided as a **reference** — study it, but write your own code in `data_fetcher.py`.

---

---

## Part 0 — Project setup

### 0.1 Prerequisites

Make sure you have **Python 3.10 or newer** installed.  
Check with:

```bash
python --version
```

### 0.2 Create a virtual environment

A virtual environment keeps this project's libraries isolated from the rest of
your system.  Run these commands once, from inside the project folder:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt should now start with `(venv)`.  
**Every time you open a new terminal for this project, activate the venv first.**

### 0.3 Install the dependencies

The packages you will need for this project are:

```python
requests==2.34.2  # to get the data
matplotlib>=3.7.0  # to make charts later on
```


### 0.5 Project folder structure
To respect proper project structure, we would like to have the following files:
```python
project/
├── venv/
├── data/ # the folder where your data will live
├── main.py # the main script that is executed (entrypoint) 
├── data_fetcher.py # the data fetching logic lives here
├── feature_engineering.py # data processing logic is here
├── plotter.py # drawing logic will be here
└── requirements.txt
```


---

---

## Part 1 — Fetching and saving stock data

The goal of this part is to write two functions inside `data_fetcher.py`:

1. `fetch_ohlcv(ticker, period)` — ask Yahoo Finance for price data, return it as a list of dicts
2. `save_to_csv(data, filepath)` — write that list to a CSV file on disk

By the end, running `data_fetcher.py` directly should download real stock data and save it locally so the rest of the pipeline can use it without going to the internet again.

---

### 1.1 What is a REST API?

Every time your browser loads a web page, it sends an **HTTP request** to a server and receives a response. REST APIs work on the same principle — but instead of asking for a web page, you are asking for **data**.

The request is still just a URL. The response is still just text. What changes is the format: instead of HTML that a browser renders, you get **JSON** — a text format that maps directly onto Python dicts and lists.

There is no login, no SDK, no library specific to Yahoo Finance. You send a URL, you get JSON back. That is the whole protocol.

The Python library `requests` handles the mechanics of making HTTP calls. It is the only non-standard import you will need in this file.

---

### 1.2 Anatomy of a GET request

An HTTP GET request has three components you need to understand:

**The URL**

A URL is a structured address. For example:

```
https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1y&interval=1d
```

It has four parts:

- `https://` — the protocol (always HTTPS for API calls)
- `query1.finance.yahoo.com` — the host (Yahoo's server)
- `/v8/finance/chart/AAPL` — the path, where `AAPL` is the ticker symbol you want
- `?range=1y&interval=1d` — the **query string**: parameters you send to the server

Query parameters come after the `?` and are separated by `&`. Each one is a `key=value` pair. Think of them as arguments you pass to a function, but in the URL itself.

For this project you need two:

| Parameter | What it controls | Values you can use |
|-----------|-----------------|-------------------|
| `range` | How far back in time to fetch | `1d` `5d` `1mo` `3mo` `6mo` `1y` `2y` `5y` |
| `interval` | The size of each candle | Always `1d` (one row per trading day) |

**Try it now** — paste this URL directly into your browser and look at what comes back:

```
https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=3mo&interval=1d
```

That wall of text is exactly what your Python script will receive.

**Headers**

Every HTTP request also carries **headers** — a set of key-value metadata pairs sent alongside the URL. One header matters here: `User-Agent`. It tells the server what kind of client is making the request. By default the `requests` library identifies itself as `python-requests/2.x.x`. Yahoo Finance sees this and rejects the request with a 401 or 429 error.

The fix: set `User-Agent` to a string that looks like a real browser. In `requests`, headers are passed as a plain Python dict using the `headers` argument:

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

response = requests.get(url, params=params, headers=HEADERS)
```

Define `HEADERS` once at the top of your file as a module-level constant, then pass it to every request you make.

**Status codes**

The server's response starts with a numeric status code. `200` means success. `4xx` means your request was bad (wrong ticker, missing header). `5xx` means the server failed. The `requests` library gives you access to this code and can raise an exception automatically if the status is not 2xx.

---

### 1.3 The response — understanding JSON

The server returns a JSON string. Once parsed, it becomes a nested Python structure of dicts and lists.

**What JSON looks like**

JSON is text. It uses the same syntax as Python dict and list literals: curly braces for objects (dicts), square brackets for arrays (lists), strings in double quotes, numbers unquoted. Python's `requests` library can parse it into real Python objects in one call.

**The full response structure (simplified)**

The Yahoo Finance response contains many fields. Below is the skeleton with irrelevant keys removed, and only three days of data shown to keep it readable. The `...` markers mean the pattern continues for every trading day.

```json
{
  "chart": {
    "result": [
      {
        "meta": {
          "symbol": "AAPL",
          "currency": "USD",
          "exchangeName": "NMS",
          "regularMarketPrice": 226.08
        },
        "timestamp": [
          1672531200,
          1672617600,
          1672704000
        ],
        "indicators": {
          "quote": [
            {
              "open":   [130.28, 130.46, 131.25],
              "high":   [130.90, 133.41, 133.51],
              "low":    [124.17, 129.89, 130.46],
              "close":  [125.07, 129.62, 130.15],
              "volume": [112117500, 89100800, 70790800]
            }
          ],
          "adjclose": [
            {
              "adjclose": [124.85, 129.38, 129.91]
            }
          ]
        }
      }
    ],
    "error": null
  }
}
```

**What to take from this structure**

- `chart → result` is a list. For a single ticker there is always exactly one element. You always take index `[0]`.
- `result[0] → timestamp` is a flat list of integers — one per trading day.
- `result[0] → indicators → quote` is also a list with one element. You take index `[0]` to get the dict that holds the OHLCV lists.
- `adjclose` is the split/dividend-adjusted close price. You will not need it for now.
- `meta` contains useful metadata (currency, exchange, latest price) but you will not need it for this step.
- `error` is `null` when the request succeeds. A non-null value here means the ticker was not found or the request was malformed.

**The parallel lists**

All five lists inside `quote` — `open`, `high`, `low`, `close`, `volume` — have the same length as `timestamp`. Index `i` across all of them always refers to the same trading day:

```
timestamp[0] = 1672531200   →   2023-01-01   →   open[0]=130.28, close[0]=125.07, volume[0]=112117500
timestamp[1] = 1672617600   →   2023-01-02   →   open[1]=130.46, close[1]=129.62, volume[1]=89100800
timestamp[2] = 1672704000   →   2023-01-03   →   open[2]=131.25, close[2]=130.15, volume[2]=70790800
```

Your job is to loop over these indices and pack each one into a dict.

---

### 1.4 Timestamps

The numbers in the `timestamp` list look like `1672531200`. These are not dates — they are **Unix epoch seconds**: the number of seconds elapsed since midnight on 1 January 1970 UTC. This is a universal standard shared across all operating systems and programming languages.

Python's standard library `datetime` module knows how to convert these numbers into human-readable dates. You will need `datetime.fromtimestamp()` to get a datetime object, and then `.strftime()` to format it as a string. Look up both in the Python documentation.

Store both: the raw integer (for future sorting and arithmetic) and the formatted string (for readability and CSV column headers).

---

### 1.5 What is a pure function?

A **pure function** is a function that:

- Given the same inputs, always returns the same output
- Has no side effects — it does not write files, print to the terminal, modify global variables, or do anything other than compute a return value

`fetch_ohlcv` should be a pure function. Its only job is to talk to the API and return data. It should not know or care whether that data will be saved to a file, printed, or thrown away. Keeping responsibilities separate makes each piece of code easier to read, test, and reuse.

The saving logic belongs in a separate function.

---

### 1.6 Saving to CSV

CSV stands for **Comma-Separated Values**. It is a plain text file format where each row is a line of text and each value on that line is separated by a comma. The first row is typically a header row with column names.

This format is simple, universally supported, and can be opened in Excel or any spreadsheet tool. More importantly for this project, it lets you fetch data once and reuse it without hitting the API again.

Python's standard library includes a `csv` module. The `csv.DictWriter` class is designed for exactly this task: it takes a list of dicts and writes them to a file, using the dict keys as column names. You will need to:

- Open a file for writing (using the built-in `open()`)
- Create a `DictWriter` pointing at that file, with the column names you want
- Call `writeheader()` to write the column names as the first row
- Call `writerows()` to write all the data rows

Check the Python documentation for `csv.DictWriter` — it is straightforward.

<details>
<summary>Example — writing a simple timeseries to CSV</summary>

Imagine you have this data in memory — a few days of imaginary temperature readings:

```python
readings = [
    {"date": "2024-01-01", "city": "Brussels", "temp_c": 3.2},
    {"date": "2024-01-02", "city": "Brussels", "temp_c": 1.8},
    {"date": "2024-01-03", "city": "Brussels", "temp_c": 5.0},
]
```

Writing it to `weather.csv`:

```python
import csv

with open("weather.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "city", "temp_c"])
    writer.writeheader()
    writer.writerows(readings)
```

The resulting file would look like this:

```
date,city,temp_c
2024-01-01,Brussels,3.2
2024-01-02,Brussels,1.8
2024-01-03,Brussels,5.0
```

A few things to note:
- `fieldnames` defines the column order and which keys to write. Any key in a dict that is not listed here will be silently ignored.
- `newline=""` is required when opening a file for `csv` on Windows — without it you get blank lines between rows.
- `encoding="utf-8"` ensures special characters are handled correctly.
- `writeheader()` must be called before `writerows()`, or your CSV will have no column names.

</details>

---

### 1.7 What to build

Write two functions in `data_fetcher.py`:

```python
def fetch_ohlcv(ticker: str, period: str = "1y") -> list:
    ...

def save_to_csv(data: list, filepath: str) -> None:
    ...
```

**`fetch_ohlcv`** takes a ticker symbol and a period string, calls the Yahoo Finance API, and returns a list of dicts. Each dict represents one trading day and must contain these keys:

| Key | Type | What it holds |
|-----|------|---------------|
| `"ticker"` | `str` | The ticker symbol in uppercase |
| `"timestamp"` | `int` | The raw Unix epoch integer from the API |
| `"date"` | `str` | A human-readable date in `"YYYY-MM-DD"` format |
| `"open"` | `float` | Opening price |
| `"high"` | `float` | Highest price of the day |
| `"low"` | `float` | Lowest price of the day |
| `"close"` | `float` | Closing price |
| `"volume"` | `int` | Number of shares traded |

**`save_to_csv`** takes the list returned by `fetch_ohlcv` and a file path string, and writes the data to that path as a CSV file. It returns nothing. The first row of the file must be the column headers.

At the bottom of the file, under `if __name__ == "__main__":`, call both functions in sequence to fetch 3 months of Apple data and save it to `data/aapl.csv`. Then print the first and last row so you can verify the output.
