"""Calcul conditionnel, puissance supposée et facteur électrique sourcé ; aucune mesure électrique."""
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
summary=pd.read_csv(ROOT/'experiments/results/tp04/summary.csv')
rows=[]
for _,r in summary.iterrows():
    for watts in [10,25,50]:
        kwh=r.total_seconds*watts/3600000
        rows.append({'strategy':r.strategy,'workload':'TP04_10_fixtures','power_w_assumed':watts,'pue':1,
          'power_source':'hypothèse pédagogique autorisée ; pas de wattmètre','pue_status':'frontière ordinateur seul, pas de centre de données',
          'duration_seconds_measured':r.total_seconds,'estimated_conditional_kwh':kwh,'carbon_g_per_kwh':20.0,
          'estimated_direct_gco2e':kwh*20,'estimated_kwh_per_contract_success':kwh/r.passes if r.passes else None,
          'factor_source':'https://analysesetdonnees.rte-france.com/bilan-electrique-2025/emissions',
          'factor_scope':'consommation française 2025, émissions directes, moyenne annuelle historique',
          'consulted':'2026-11-23','status':'calcul conditionnel, puissance hypothétique, facteur historique sourcé ; réel ND',
          'excluded':'chargement, entraînement, fabrication, réseau, électricité amont, climatisation du lieu, durée hors requêtes'})
pd.DataFrame(rows).to_csv(ROOT/'experiments/results/tp05_green_estimates.csv',index=False)
print('12 scénarios calculés ; énergie réelle toujours ND')
