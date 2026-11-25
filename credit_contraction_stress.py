"""Chapter 7: illustrative credit contraction, not an empirical forecast.
Sources:
https://www.federalreserve.gov/data/sloos/sloos-202610-table-1.htm
https://www.federalreserve.gov/publications/2026-june-supervision-and-regulation-report-report-banking-system-conditions.htm
https://www.federalreserve.gov/newsevents/pressreleases/bcreg20260624a.htm
"""
import csv
from pathlib import Path
p=Path("data")
p.mkdir(exist_ok=True)
def save(name, header, rows):
    with (p/name).open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
save("sloos_2026q3_cre.csv",["category","respondents","tightened","unchanged","eased","demand_stronger","demand_unchanged","demand_weaker"],[
    ["construction_land",58,11,45,2,4,35,19],
    ["nonresidential",57,7,48,2,8,35,14],
    ["multifamily",57,8,46,3,5,34,18]])
save("bank_capital_stress.csv",["cet1_loss_usd_billion","initial_rwa_usd_billion","initial_cet1_usd_billion","target_cet1_pct","max_rwa_usd_billion","rwa_reduction_usd_billion"],[
    [loss,100,12,12,round((12-loss)/.12,4),round(100-(12-loss)/.12,4)] for loss in (0,1,2,3,4)])
save("down_payment_credit_stress.csv",["down_payment_pct","available_cash_usd","purchase_ceiling_usd","loan_ceiling_usd"],[
    [ratio*100,100000,round(100000/ratio,2),round(100000/ratio-100000,2)] for ratio in (.2,.25,.3,.35,.4)])
save("fed_2026_stress_test.csv",["measure","value","unit"],[
    ["banks_tested",32,"count"],["cre_price_decline",39,"percent"],["house_price_decline",30,"percent"],
    ["peak_unemployment",10,"percent"],["total_losses_lower_bound",708,"usd_billion"],
    ["aggregate_cet1_decline",1.6,"percentage_points"],["credit_card_losses_approx",200,"usd_billion"],
    ["ci_losses_approx",160,"usd_billion"],["cre_losses_approx",75,"usd_billion"]])
