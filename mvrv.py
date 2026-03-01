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

json_response = response.json()

if "data" not in json_response:
    raise Exception(f"Unexpected API response: {json_response}")

df = pd.DataFrame(json_response["data"])

df["CapMVRVCur"] = pd.to_numeric(df["CapMVRVCur"], errors="coerce")
df = df.dropna()

# Rolling Z-score
window = 730
rolling_mean = df["CapMVRVCur"].rolling(window).mean()
rolling_std = df["CapMVRVCur"].rolling(window).std()

df["mvrv_z_score"] = (df["CapMVRVCur"] - rolling_mean) / rolling_std

output = df[["time", "mvrv_z_score"]].rename(columns={"time": "date"})
output = output.dropna()

output.to_json("mvrv.json", orient="records")

print("MVRV updated successfully.")
