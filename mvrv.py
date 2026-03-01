import requests
import pandas as pd

url = (
    "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    "?assets=btc"
    "&metrics=CapMVRVCur"
    "&frequency=1d"
    "&start_time=2011-01-01"
)

response = requests.get(url)

if response.status_code != 200:
    raise Exception(f"API request failed: {response.status_code} - {response.text}")

data = response.json()

if "data" not in data:
    raise Exception(f"Unexpected API response: {data}")

df = pd.DataFrame(data["data"])

df["CapMVRVCur"] = pd.to_numeric(df["CapMVRVCur"], errors="coerce")
df = df.dropna()

# Optional: compute Z-score of MVRV ratio
window = 730
rolling_mean = df["CapMVRVCur"].rolling(window).mean()
rolling_std = df["CapMVRVCur"].rolling(window).std()

df["mvrv_z_score"] = (df["CapMVRVCur"] - rolling_mean) / rolling_std

output = df[["time", "mvrv_z_score"]].rename(columns={"time": "date"})
output = output.dropna()

output.to_json("mvrv.json", orient="records")

print("MVRV updated successfully.")
