"""Illustrative scenarios, not empirical forecasts.
FRB Z.1 F4.s release 2026-09-11:
https://www.federalreserve.gov/releases/z1/20260911/html/F4_s.htm
NY Fed 2026 Q3 household debt and FHFA 2026 Q3 HPI are separate datasets.
"""
import csv
from pathlib import Path
p=Path("data")
p.mkdir(exist_ok=True)
with (p/"property_mortgage_stock.csv").open("w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["period","commercial_usd_billion","multifamily_usd_billion"])
    w.writerows([["2023Q4",3774.1,2204.3],["2024Q4",3834.9,2307.3],["2025Q4",3953.4,2448.7],["2026Q2",4011.5,2493.4]])
with (p/"housing_affordability_stress.csv").open("w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["income_decline_pct","annual_income","purchase_capacity"])
    for shock in (0,5,10,20,30):
        income=100000*(1-shock/100)
        rate=.06/12
        value=income*.30/12*(1-(1+rate)**-360)/rate/.8
        w.writerow([shock,income,round(value,2)])
with (p/"cre_refinancing_stress.csv").open("w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["noi_decline_pct","cap_rate_pct","noi","value","debt","ltv_pct","dscr","refinance_gap"])
    for shock in (0,10,20,30):
        for cap in (.05,.06,.07):
            noi=500000*(1-shock/100)
            value=noi/cap
            debt=7000000
            w.writerow([shock,cap*100,noi,round(value,2),debt,round(100*debt/value,2),round(noi/400000,3),round(max(0,debt-.7*value),2)])
