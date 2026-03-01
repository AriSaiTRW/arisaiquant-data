import requests
import pandas as pd

# -------------------------
# Fetch Data from CoinMetrics
# -------------------------

url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"

params = {
    "assets": "btc",
    "metrics": "CapMrktCurUSD,CapRealUSD",
    "frequency": "1d"
}

response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame(data["data"])

# Convert to numeric
df["CapMrktCurUSD"] = pd.to_numeric(df["CapMrktCurUSD"])
df["CapRealUSD"] = pd.to_numeric(df["CapRealUSD"])

# -------------------------
# Calculate MVRV Z-Score
# -------------------------

window = 730  # 2-year rolling window

spread = df["CapMrktCurUSD"] - df["CapRealUSD"]
rolling_std = df["CapMrktCurUSD"].rolling(window).std()

df["mvrv_z_score"] = spread / rolling_std

# Clean output
output = df[["time", "mvrv_z_score"]].rename(columns={"time": "date"})
output = output.dropna()

output.to_json("mvrv.json", orient="records")

print("MVRV updated successfully.")
