"""Illustrative cash-flow model, not a forecast.
Observed aggregate inputs: Fed Z.1 S11.t, September 11 2026.
https://www.federalreserve.gov/releases/z1/current/html/S11_t.htm
Debt stock: https://www.federalreserve.gov/releases/z1/dataviz/z1/nonfinancial_debt/table/
Gross saving is not accounting operating cash flow.
"""
import csv
from pathlib import Path
p=Path("data")
with (p/"business_fed_20260911.csv").open() as f:
    rows=list(csv.DictReader(f))
with (p/"business_internal_funds_stress.csv").open("w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["period","internal_funds_shock_pct","internal_funds_billion","capital_expenditure_billion","funding_gap_billion"])
    for row in rows:
        saving=float(row["adjusted_gross_saving_billion"])
        capex=float(row["capital_expenditure_billion"])
        for shock in (0,5,10,15,20):
            funds=saving*(1-shock/100)
            w.writerow([row["period"],shock,round(funds,2),capex,round(funds-capex,2)])
# Hypothetical firm: revenue 100, variable costs 50%, fixed cash costs 35,
# annual interest plus principal 10. Excludes taxes and working capital.
with (p/"business_illustrative_dscr.csv").open("w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["revenue_decline_pct","revenue","cash_surplus_before_debt_service","debt_service","illustrative_coverage"])
    for shock in (0,5,10,15,20,25,30):
        revenue=100-shock
        surplus=revenue*.5-35
        w.writerow([shock,revenue,surplus,10,surplus/10])
