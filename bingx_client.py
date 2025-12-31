import time
import hmac
import hashlib
import requests
import pandas as pd
from config.bingx_config import API_KEY, API_SECRET, BASE_URL

class BingX:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-BX-APIKEY": API_KEY})

    def _sign(self, params):
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            API_SECRET.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()

    def get_all_usdt_pairs(self):
        url = f"{BASE_URL}/openApi/swap/v2/quote/contracts"
        r = self.session.get(url).json()
        return [
            x["symbol"] for x in r["data"]
            if x["currency"] == "USDT"
        ]

    def get_klines(self, symbol, interval="15m", limit=200):
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
            "timestamp": int(time.time() * 1000)
        }
        params["signature"] = self._sign(params)
        url = f"{BASE_URL}/openApi/swap/v3/quote/klines"
        r = self.session.get(url, params=params).json()

        df = pd.DataFrame(r["data"], columns=[
            "time","open","high","low","close","volume"
        ])
        df[["open","high","low","close","volume"]] = df[
            ["open","high","low","close","volume"]
        ].astype(float)
        return df
