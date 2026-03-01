import requests
import pandas as pd

url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"

params = {
    "assets": "btc",
    "metrics": "CapMrktCurUSD,CapRealUSD",
    "frequency": "1d",
    "start_time": "2011-01-01",   # REQUIRED
    "page_size": 10000
}

response = requests.get(url, params=params)

if response.status_code != 200:
    raise Exception(f"API request failed: {response.status_code} - {response.text}")

data = response.json()

print("DEBUG RESPONSE:", data)  # Temporary debug line

if "data" not in data:
    raise Exception(f"Unexpected API response: {data}")

df = pd.DataFrame(data["data"])

df["CapMrktCurUSD"] = pd.to_numeric(df["CapMrktCurUSD"], errors="coerce")
df["CapRealUSD"] = pd.to_numeric(df["CapRealUSD"], errors="coerce")

df = df.dropna()

# Rolling Z-score
window = 730
spread = df["CapMrktCurUSD"] - df["CapRealUSD"]
rolling_std = df["CapMrktCurUSD"].rolling(window).std()

df["mvrv_z_score"] = spread / rolling_std

output = df[["time", "mvrv_z_score"]].rename(columns={"time": "date"})
output = output.dropna()

output.to_json("mvrv.json", orient="records")

print("MVRV updated successfully.")
