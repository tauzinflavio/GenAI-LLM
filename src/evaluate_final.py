"""Évaluer les modèles figés sur le test final sans choisir de nouveau réglage."""
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.io import arff
from sklearn.metrics import average_precision_score, precision_score, recall_score, confusion_matrix
from run_experiment import feature_matrix

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'experiments/final_test'
    if (out/'metrics.csv').exists():
        raise SystemExit('Test déjà évalué ; résultats conservés. Aucune réévaluation automatique.')
    out.mkdir(exist_ok=True)
    # Enregistrer la décision AVANT toute lecture du test.
    decision=dict(selected_configuration='B1_class_weight',selected_seed=42,
                  basis='meilleure AP moyenne de validation ; seuil F1 de validation conservé',
                  no_retraining=True,no_new_hyperparameters=True,
                  comparator='G1_ddpm_x4',comparison_seed=42)
    (out/'frozen_decision.json').write_text(json.dumps(decision,indent=2))
    raw,_=arff.loadarff(ROOT/'data/raw/creditcard.arff')
    frame=pd.DataFrame(raw)
    ids=pd.read_csv(ROOT/'data/processed/test_indices.csv').source_row_index.to_numpy()
    test=frame.iloc[ids]
    x=joblib.load(ROOT/'models/detector_scaler.joblib').transform(feature_matrix(test))
    y=test.Class.astype(int).to_numpy()
    validation=pd.read_csv(ROOT/'experiments/v1/metrics.csv')
    records=[]
    for row in validation.itertuples():
        name=f'{row.configuration}_{row.seed}'
        model=joblib.load(ROOT/f'models/{name}.joblib')
        scores=model.predict_proba(x)[:,1]
        predicted=scores>=row.threshold
        tn,fp,fn,tp=confusion_matrix(y,predicted,labels=[0,1]).ravel()
        records.append(dict(configuration=row.configuration,seed=row.seed,split='test_final',
                            average_precision=float(average_precision_score(y,scores)),threshold=float(row.threshold),
                            precision=float(precision_score(y,predicted,zero_division=0)),recall=float(recall_score(y,predicted)),
                            true_positives=int(tp),false_positives=int(fp),false_negatives=int(fn),true_negatives=int(tn),
                            status='mesure',selected_before_test=row.configuration=='B1_class_weight' and row.seed==42))
        np.save(out/f'{name}_scores.npy',scores)
    pd.DataFrame(records).to_csv(out/'metrics.csv',index=False)
    # Bootstrap apparié exploratoire, positifs et négatifs tirés séparément.
    rng=np.random.default_rng(20261116)
    positive=np.flatnonzero(y==1);negative=np.flatnonzero(y==0)
    a=np.load(out/'G1_ddpm_x4_42_scores.npy');b=np.load(out/'B1_class_weight_42_scores.npy')
    delta=[]
    for _ in range(300):
        sample=np.concatenate([rng.choice(positive,len(positive),replace=True),rng.choice(negative,len(negative),replace=True)])
        delta.append(average_precision_score(y[sample],a[sample])-average_precision_score(y[sample],b[sample]))
    summary=dict(rows=len(y),frauds=int(y.sum()),delta_ap_ddpm_minus_weighted=float(average_precision_score(y,a)-average_precision_score(y,b)),
                 bootstrap_95_percentile=[float(np.quantile(delta,.025)),float(np.quantile(delta,.975))],
                 bootstrap_replicates=300,bootstrap_seed=20261116,
                 limitations='bootstrap par lignes stratifié ; dépendances clients inconnues ; fenêtre temporelle courte')
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(pd.DataFrame(records)[lambda t:t.seed==42].to_string(index=False))


if __name__=='__main__':main()
