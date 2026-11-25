import csv
from pathlib import Path
# Illustrative normalized economy; not calibrated to national accounts.
# Household income 100, necessities 60, debt service 20.
# Firm revenue 100; 30% exposed to discretionary spending.
# Variable costs 50% of revenue, fixed costs 35, debt service 10.
# No savings drawdown, transfers, price response or substitution.
rows=[]
for s in range(0,26,5):
    income=100-s
    discretionary=max(0,income-60-20)
    household_shortfall=max(0,60+20-income)
    spending_drop=1-discretionary/20
    revenue=100*(1-.30*spending_drop)
    cash=revenue*.5-35
    rows.append([s,income,discretionary,household_shortfall,round(revenue,4),round(cash,4),round(cash/10,4),round(max(0,10-cash),4)])
header=['income_decline_pct','household_income','discretionary_spending','household_funding_gap','firm_revenue','firm_cash_before_debt','firm_debt_coverage','firm_funding_gap']
p=Path(__file__).resolve().parent/'data';p.mkdir(exist_ok=True)
with (p/'ch08_integrated_stress.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(header);w.writerows(rows)
print(header);print(*rows,sep='\n')
with (p/'ch08_exposure_sensitivity.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['discretionary_revenue_share_pct','income_decline_at_firm_coverage_one_pct'])
    for e in (.10,.20,.30,.40,.50):w.writerow([round(e*100),round(2/e,4)])
