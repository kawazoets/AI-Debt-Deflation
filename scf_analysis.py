"""Descriptive point estimates only; no causal AI inference or survey standard errors.
Source: https://www.federalreserve.gov/econres/scfindex.htm
Published comparison: https://www.federalreserve.gov/publications/files/scf26.pdf Table 5.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from urllib.request import urlopen, Request
from io import BytesIO
from zipfile import ZipFile
Path("data").mkdir(exist_ok=True)
rows=[]
for year in (2022,2025):
    url=f"https://www.federalreserve.gov/econres/files/scfp{year}excel.zip"
    local=Path(f"data/scfp{year}excel.zip")
    if local.exists():
        z=ZipFile(local)
    else:
        req=Request(url, headers={"User-Agent":"AI-Debt-Deflation research (public data)", "Accept":"application/zip, */*"})
        with urlopen(req,timeout=120) as response:
            z=ZipFile(BytesIO(response.read()))
    with z.open(next(n for n in z.namelist() if n.lower().endswith(".csv"))) as f:
        d=pd.read_csv(f,low_memory=False)
    d.columns=d.columns.str.lower()
    d=d[["age","income","debt","wgt","pirtotal"]].dropna()
    d=d[d.wgt>0].copy()
    d["age_group"]=pd.cut(d.age,[0,35,45,55,65,75,np.inf],right=False)
    ordered=d.sort_values("income")
    ranks=(ordered.wgt.cumsum()-ordered.wgt/2)/ordered.wgt.sum()
    d["income_group"]=pd.cut(ranks,[0,.2,.4,.6,.8,1],include_lowest=True,labels=["Q1","Q2","Q3","Q4","Q5"])
    for dimension in ("age_group","income_group"):
        for group,g in d.groupby(dimension,observed=True):
            b=g[g.debt>0]
            w=g.wgt
            bw=b.wgt
            total_debt=(d.debt*d.wgt).sum()
            inc=(g.income*w).sum()
            for shock in (0,.05,.10,.15,.20):
                rows.append(dict(year=year,dimension=dimension,group=str(group),income_shock_pct=shock*100,
                    debt_share_pct=100*(g.debt*w).sum()/total_debt,
                    debt_income_pct=100*(g.debt*w).sum()/(inc*(1-shock)) if inc>0 else np.nan,
                    debtor_share_pct=100*bw.sum()/w.sum(),
                    stressed_debtor_share_pct=100*bw[b.pirtotal/(1-shock)>.4].sum()/bw.sum() if bw.sum()>0 else np.nan))
pd.DataFrame(rows).to_csv("data/scf_group_stress.csv",index=False)
