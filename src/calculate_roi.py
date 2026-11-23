"""Calculer trois scénarios à partir d'hypothèses renseignées et sourcées."""
import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIABLES = ['volume_alertes','minutes_gagnees','cout_horaire','revue_supplementaire',
             'investissement_initial','exploitation','autres_gains_etayes','autres_couts_metier']
SCENARIOS = ['pessimiste','central','optimiste']


def calculate(values):
    gross = values['volume_alertes'] * values['minutes_gagnees'] / 60 * values['cout_horaire']
    review = values['volume_alertes'] * values['revue_supplementaire'] / 60 * values['cout_horaire']
    net = gross + values['autres_gains_etayes'] - review - values['autres_couts_metier']
    cost = values['investissement_initial'] + values['exploitation']
    if cost <= 0:
        raise ValueError('Le coût total année 1 doit être strictement positif.')
    annual_margin = net - values['exploitation']
    return dict(gain_brut_eur=gross,cout_revue_eur=review,gain_net_operationnel_eur=net,
                cout_total_annee1_eur=cost,roi_annee1_pct=(net-cost)/cost*100,
                retour_simple_mois=values['investissement_initial']/annual_margin*12 if annual_margin>0 else None)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'docs/hypotheses_roi.csv')
    parser.add_argument('--output',type=Path,default=ROOT/'experiments/roi_scenarios.csv')
    args=parser.parse_args()
    rows=list(csv.DictReader(args.input.open(encoding='utf-8-sig')))
    by_name={row['variable']:row for row in rows}
    errors=[]
    if len(by_name)!=len(rows):
        errors.append('Variables dupliquées dans le tableau.')
    scenarios={name:{} for name in SCENARIOS}
    for variable in VARIABLES:
        row=by_name.get(variable)
        if row is None:
            errors.append(f'Variable absente : {variable}')
            continue
        if not (row.get('source_ou_methode') or '').strip():
            errors.append(f'Source ou méthode manquante pour {variable}')
        for scenario in SCENARIOS:
            try:
                value=Decimal((row.get(scenario) or '').strip().replace(',','.'))
                if not value.is_finite() or (value<0 and variable!='minutes_gagnees'):
                    raise ValueError('Valeur invalide')
                scenarios[scenario][variable]=value
            except (InvalidOperation,ValueError):
                errors.append(f'Valeur manquante ou invalide : {variable}, {scenario}')
    if errors:
        print('Calcul non réalisé. Compléter les hypothèses suivantes.',file=sys.stderr)
        print('\n'.join(errors),file=sys.stderr)
        return 2
    results=[]
    for name,values in scenarios.items():
        result=calculate(values)
        results.append(dict(scenario=name,statut='calcule_depuis_hypotheses',**{
            key:format(value,'.6f') if value is not None else 'non_defini' for key,value in result.items()}))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print(f'Trois scénarios calculés et enregistrés dans {args.output}.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
