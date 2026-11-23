"""Détailler le scénario fictif autorisé, sans l'assimiler aux mesures de TP04."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def save(path,rows):
    with (ROOT/path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    # Coûts d'exploitation techniques ; revue dossier et coûts métier restent séparés.
    posts=[('calcul_materiel_electricite',1200,800,600,'Allocation hypothétique ordinateur/électricité ; aucune API payante'),('maintenance_correctifs',4000,3200,2800,'Forfait hypothétique de maintenance logicielle'),('supervision_technique',2500,2000,1800,'Exploitation technique uniquement, hors relecture métier'),('stockage_sauvegardes',800,600,400,'Forfait hypothétique de stockage et sauvegardes'),('licences',0,0,0,'Aucune licence payante retenue dans ce scénario'),('reserve_incidents_techniques',1500,1400,1400,'Réserve hypothétique pour incidents techniques, pas temps de revue des alertes')]
    detail=[dict(poste=k,unite='EUR/an',pessimiste=p,central=c,optimiste=o,methode=m,statut='hypothèse pédagogique, aucune facture') for k,p,c,o,m in posts]
    assert [sum(r[k] for r in detail) for k in ['pessimiste','central','optimiste']]==[10000,8000,7000]
    save('docs/29_ventilation_couts.csv',detail)
    initial=[dict(poste=k,unite='EUR',montant=v,statut='hypothèse pédagogique') for k,v in [('cadrage_architecture',2000),('audit_preparation_donnees',2000),('experimentation_diffusion',4000),('integration_multi_llm',3000),('interface_api',2500),('qualification_documentation',1500)]]
    assert sum(r['montant'] for r in initial)==15000
    save('docs/29_investissement_initial.csv',initial)
    steps=[('1','Réception de la transaction associée à une alerte','Système transactionnel','Champs autorisés',.01,.01,False,'schéma invalide'),('2','Score et règles','Détecteur','Variables anonymisées',.02,.02,False,'faux négatif'),('3','Création / attribution de l’alerte','Supervision','Score et seuil',.02,.02,False,'surcharge'),('4','Examen des faits','Analyste','Dossier autorisé',3.,2.25,True,'interprétation excessive'),('5','Recherche des éléments manquants','Analyste','Sources disponibles',1.5,.75,True,'source absente'),('6','Rédaction / synthèse','Analyste','Faits vérifiés',1.25,.75,True,'hallucination'),('7','Validation et journal','Responsable habilité','Avis et justification',.5,.5,True,'absence de traçabilité')]
    process=[dict(etape=i,action=action,acteur_outil=actor,donnees=data,minutes_as_is=a,minutes_to_be_avant_revue=b,cost_human_as_is_eur=a*.75 if human else 0,cost_human_to_be_eur=b*.75 if human else 0,frequence='par alerte du scénario, 24000/an',risque=risk,statut='hypothèse pédagogique, aucune observation bancaire') for i,action,actor,data,a,b,human,risk in steps]
    save('docs/29_processus_metier.csv',process)
    gain=sum(r['minutes_as_is']-r['minutes_to_be_avant_revue'] for r in process);assert abs(gain-2)<1e-9
    rows=[]
    for sc,ops,minutes,review,rework in [('pessimiste',10000,.5,.75,.20),('central',8000,2,.5,.10),('optimiste',7000,2.5,.25,.05)]:
        gross=24000*minutes/60*45;human=24000*review/60*45;net=gross-human-1000
        rows.append(dict(scenario=sc,volume_annuel=24000,reprises_metier_fraction_supposee=rework,reprises_incluses_dans_minutes_revue=True,exploitation_annuelle=ops,exploitation_mensuelle=ops/12,exploitation_par_alerte=ops/24000,investissement_initial=15000,cout_total_annee1=15000+ops,gain_brut_annuel=gross,revue_metier_annuelle=human,autres_couts_metier=1000,gain_net_operationnel=net,roi_pct=(net-15000-ops)/(15000+ops)*100,statut='calcul sur hypothèses, pas mesure de coût LLM'))
    save('experiments/results/financial_breakdown.csv',rows)
    # Allocation fictive du coût annuel par lot, en conservant le workload TP04 et ses succès observés.
    summaries=list(csv.DictReader((ROOT/'experiments/results/tp04/summary.csv').open()))
    allocated=[]
    for s in summaries:
        n=int(s['cases']);passes=int(s['passes']);cost=8000/24000*n
        allocated.append(dict(strategy=s['strategy'],tasks=n,contracts_success=passes,allocated_technical_cost_eur=cost,cost_per_contract_success_eur=cost/passes if passes else None,api_cost_eur=0,annual_cost_assumed_eur=8000,annual_volume_assumed=24000,status='allocation hypothétique uniforme ; pas coût réel ni coût marginal ; gardes incluses'))
    save('experiments/results/finops_allocated_scenario.csv',allocated)
    out={'scenario':'hypothétique autorisé','operating_cost_totals':[10000,8000,7000],'initial_total':15000,'gross_minutes_saved_central':gain,'review_minutes_added_central':.5,'roi_central':rows[1]['roi_pct'],'checks_passed':True,'real_full_cost':'ND','warning':'Réserve incidents techniques distincte de revue métier ; ne pas sommer deux fois les enveloppes et leurs postes.'}
    (ROOT/'experiments/results/financial_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
