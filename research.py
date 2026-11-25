import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from io import BytesIO
import time

SERIES = {
    "productivity": "OPHNFB",
    "real_hourly_compensation": "COMPRNFB",
    "labor_share_index": "PRS85006173",
    "hours_worked": "HOANBS",
    "employee_compensation_billion_saar": "COE",
    "disposable_income_billion_saar": "DPI",
    "real_disposable_income_billion_saar": "DSPIC96",
    "household_debt_billion": "CMDEBT",
    "debt_service_pct": "TDSP",
    "saving_rate_pct": "PSAVERT",
    "corporate_profits_billion_saar": "CP"
}
Path("data").mkdir(exist_ok=True)
Path("charts").mkdir(exist_ok=True)
frames = []
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import re
from urllib.parse import urlencode
import json
import os

def load_series(item):
    name, code = item
    urls = [
        f"https://fred.stlouisfed.org/data/{code}.txt",
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}&cosd=2005-01-01",
    ]
    key = os.getenv("FRED_API_KEY")
    if key:
        urls.insert(0, "https://api.stlouisfed.org/fred/series/observations?" + urlencode(dict(series_id=code, api_key=key, file_type="json", observation_start="2005-01-01")))
    for url in urls:
        try:
            with urlopen(Request(url, headers={"User-Agent":"Economic research data client", "Accept":"*/*"}), timeout=25) as response:
                payload = response.read()
            if url.startswith("https://api."):
                raw = pd.DataFrame(json.loads(payload)["observations"])[["date","value"]].rename(columns={"date":"DATE","value":code})
            elif url.endswith(".txt"):
                matches = re.findall(r"(?m)^\s*(\d{4}-\d{2}-\d{2})\s+(-?\d+(?:\.\d+)?|\.)\s*$", payload.decode("utf-8"))
                raw = pd.DataFrame(matches, columns=["DATE",code])
            else:
                raw = pd.read_csv(BytesIO(payload))
            dates = pd.to_datetime(raw.iloc[:,0], errors="coerce")
            values = pd.to_numeric(raw[code], errors="coerce")
            good = dates.notna() & values.notna() & (dates >= pd.Timestamp("2005-01-01"))
            raw = pd.DataFrame({"DATE":dates[good],code:values[good]}).drop_duplicates("DATE").sort_values("DATE")
            if len(raw)<50:
                raise ValueError("Insufficient valid observations")
            s = pd.Series(raw[code].values,index=pd.DatetimeIndex(raw.DATE),name=name)
            raw.to_csv(f"data/{code}.csv",index=False)
            print(f"{code}: retrieved {len(raw)} observations through {raw.DATE.max().date()}",flush=True)
            q = s.groupby(s.index.to_period("Q"))
            result = q.mean()
            if len(s)>1 and s.index.to_series().diff().median().days<45:
                result = result.where(q.count()==3)
            return result
        except Exception as exc:
            print(f"{code}: {url.split('?')[0]} failed ({type(exc).__name__})",flush=True)
    raise RuntimeError(f"No verified data retrieved for {code}")

with ThreadPoolExecutor(max_workers=4) as pool:
    frames = list(pool.map(load_series, SERIES.items()))
df = pd.concat(frames, axis=1).sort_index()
df["household_debt_to_income_pct"] = 100*df.household_debt_billion/df.disposable_income_billion_saar
df["household_debt_to_compensation_pct"] = 100*df.household_debt_billion/df.employee_compensation_billion_saar
df["estimated_annual_debt_service_billion"] = df.debt_service_pct/100*df.disposable_income_billion_saar
df["productivity_yoy_pct"] = df.productivity.pct_change(4, fill_method=None)*100
df["real_hourly_compensation_yoy_pct"] = df.real_hourly_compensation.pct_change(4, fill_method=None)*100
df["productivity_pay_gap_pp"] = df.productivity_yoy_pct-df.real_hourly_compensation_yoy_pct
df.to_csv("data/us_quarterly.csv", index_label="quarter")
cols = ["productivity","real_hourly_compensation","labor_share_index","hours_worked"]
base = df.loc["2022Q4",cols]
indexed = df[cols].div(base)*100
indexed.to_csv("data/labor_index_2022Q4.csv", index_label="quarter")
for name, values in {"labor_index":indexed, "debt_income":df[["household_debt_to_income_pct","household_debt_to_compensation_pct"]], "debt_service":df[["debt_service_pct"]]}.items():
    ax = values.set_axis(values.index.to_timestamp()).plot(figsize=(10,5))
    ax.axvline(pd.Timestamp("2022-11-30"), color="gray", linestyle="--")
    ax.set_title(name)
    ax.figure.tight_layout()
    ax.figure.savefig(f"charts/{name}.png", dpi=160)
    plt.close(ax.figure)
print(df.tail().to_string())
