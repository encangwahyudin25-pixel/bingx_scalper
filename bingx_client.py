import requests
import pandas as pd
from config.bingx_config import BASE_URL


class BingXClient:
    """
    BingX Futures Client (USDT-M)
    SAFE version (anti IP block & schema change)
    """

    def get_futures_pairs(self):
        """
        Fetch pair via TICKER endpoint (paling stabil)
        """
        url = f"{BASE_URL}/openApi/swap/v2/quote/ticker"

        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                return []

            data = r.json()
            if "data" not in data or not isinstance(data["data"], list):
                return []

            pairs = set()
            for item in data["data"]:
                symbol = item.get("symbol")
                if symbol and symbol.endswith("-USDT"):
                    pairs.add(symbol)

            return sorted(list(pairs))

        except Exception:
            return []

    def get_klines(self, symbol, interval, limit=200):
        url = f"{BASE_URL}/openApi/swap/v2/quote/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                return None

            raw = r.json().get("data", [])
            if not raw or len(raw) < 50:
                return None

            df = pd.DataFrame(
                raw,
                columns=["time", "open", "high", "low", "close", "volume"]
            )

            df[["open", "high", "low", "close", "volume"]] = df[
                ["open", "high", "low", "close", "volume"]
            ].astype(float)

            return df

        except Exception:
            return None
