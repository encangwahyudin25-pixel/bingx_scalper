import requests
import pandas as pd
from config.bingx_config import BASE_URL

class BingXClient:

    def get_futures_pairs(self):
        url = f"{BASE_URL}/openApi/swap/v2/quote/contracts"
        data = requests.get(url).json()
        return [i["symbol"] for i in data["data"] if i["quoteAsset"] == "USDT"]

    def get_klines(self, symbol, interval, limit=200):
        url = f"{BASE_URL}/openApi/swap/v2/quote/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        r = requests.get(url, params=params).json()["data"]
        df = pd.DataFrame(r, columns=[
            "time","open","high","low","close","volume"
        ])
        df = df.astype(float)
        return df
