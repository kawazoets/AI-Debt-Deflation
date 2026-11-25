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
for name, code in SERIES.items():
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}&cosd=2005-01-01"
    print(f"Downloading {code}", flush=True)
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers={"User-Agent":"AI-Debt-Deflation research (public data)", "Accept":"text/csv, */*"}), timeout=90) as response:
                raw = pd.read_csv(BytesIO(response.read()))
            s = pd.Series(pd.to_numeric(raw[code], errors="coerce").values,
                          index=pd.to_datetime(raw.iloc[:,0]), name=name)
            s = s.dropna()
            if s.empty:
                raise ValueError(f"No data: {code}")
            raw.to_csv(f"data/{code}.csv", index=False)
            # Monthly flows at annual rates are averaged, quarterly observations retained.
            frames.append(s.groupby(s.index.to_period("Q")).mean())
            break
        except Exception as exc:
            print(f"{code} attempt {attempt+1}: {exc}", flush=True)
            if attempt == 3:
                raise RuntimeError(f"Unable to retrieve {code}") from exc
            time.sleep(5*(attempt+1))
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
