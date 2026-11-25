import csv
from pathlib import Path
p=Path(__file__).resolve().parent/'data'; p.mkdir(exist_ok=True)
# Hypothetical annual disposable income 100,000; debt 300,000.
# Immediate annualized interest savings only; no amortization or fees.
with (p/'ch09_rate_relief.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['repricing_share_pct','loan_rate_cut_pp','annual_interest_savings','income_loss_offset_pct'])
 for share in (.05,.25,.5,1):
  for cut in (.01,.02,.03):
   savings=300000*share*cut
   w.writerow([share*100,cut*100,round(savings,2),round(savings/100000*100,4)])
# Real interest rate, exact Fisher equation
with (p/'ch09_real_rate.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['nominal_rate_pct','expected_inflation_pct','real_rate_pct'])
 for nominal,inflation in [(.04,.03),(.02,0),(0,-.02)]:
  w.writerow([nominal*100,inflation*100,round(((1+nominal)/(1+inflation)-1)*100,4)])
