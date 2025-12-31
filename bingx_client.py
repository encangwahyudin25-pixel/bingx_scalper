import requests
import pandas as pd
from config.bingx_config import BASE_URL


class BingXClient:

    def get_futures_pairs(self):
        """
        Fetch ALL USDT-M Futures pairs safely
        """
        url = f"{BASE_URL}/openApi/swap/v2/quote/contracts"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        data = resp.json()

        pairs = []

        for item in data.get("data", []):
            symbol = item.get("symbol", "")
            status = item.get("status", "")

            # ✅ FILTER AMAN & STABIL
            if symbol.endswith("-USDT") and status == "TRADING":
                pairs.append(symbol)

        return pairs

    def get_klines(self, symbol, interval, limit=200):
        url = f"{BASE_URL}/openApi/swap/v2/quote/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json().get("data", [])

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
