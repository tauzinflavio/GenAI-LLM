"""Fidélité/diversité descriptives sur les fraudes internes exclues du générateur ; aucun accès au test final."""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.io import arff
from scipy.spatial.distance import pdist
from scipy.stats import ks_2samp,wasserstein_distance
from sklearn.neighbors import NearestNeighbors
from run_experiment import feature_matrix
ROOT=Path(__file__).resolve().parents[1]
def main():
    raw,_=arff.loadarff(ROOT/'data/raw/creditcard.arff')
    ids=pd.read_csv(ROOT/'data/processed/train_indices.csv').source_row_index.to_numpy()
    frame=pd.DataFrame(raw).iloc[ids]
    frauds=feature_matrix(frame[frame.Class.astype(int)==1])
    summaries=[];details=[]
    for seed in [17,42,73]:
        order=np.random.default_rng(seed).permutation(len(frauds));held=frauds[order[:int(len(order)*.2)]];train=frauds[order[int(len(order)*.2):]]
        scaler=joblib.load(ROOT/f'experiments/v1/generator_scaler_{seed}.joblib')
        real=scaler.transform(held);training=scaler.transform(train)
        for multiplier in [1,4]:
            source=pd.read_csv(ROOT/f'experiments/v1/synthetic_{seed}_x{multiplier}.csv');syn=scaler.transform(source.to_numpy())
            ks=[];wd=[]
            for j,col in enumerate(source.columns):
                k=float(ks_2samp(real[:,j],syn[:,j]).statistic);w=float(wasserstein_distance(real[:,j],syn[:,j]));ks.append(k);wd.append(w)
                details.append(dict(seed=seed,multiplier=multiplier,feature=col,ks_statistic=k,wasserstein_standardized=w))
            synthetic_nn=NearestNeighbors(n_neighbors=2).fit(syn).kneighbors(syn)[0][:,1]
            real_nn=NearestNeighbors(n_neighbors=2).fit(real).kneighbors(real)[0][:,1]
            nearest=NearestNeighbors(n_neighbors=1).fit(training).kneighbors(syn)[0][:,0]
            summaries.append(dict(seed=seed,multiplier=multiplier,real_holdout_rows=len(real),synthetic_rows=len(syn),
                ks_mean=float(np.mean(ks)),wasserstein_mean=float(np.mean(wd)),
                correlation_mae=float(np.mean(np.abs(np.corrcoef(real,rowvar=False)-np.corrcoef(syn,rowvar=False)))),
                synthetic_unique_fraction=len(np.unique(syn,axis=0))/len(syn),
                synthetic_nn_median=float(np.median(synthetic_nn)),real_nn_median=float(np.median(real_nn)),
                synthetic_pair_distance_median=float(np.median(pdist(syn))),real_pair_distance_median=float(np.median(pdist(real))),
                near_train_copies=int((nearest<1e-6).sum()),test_final_accessed=False,
                scope='descriptive internal fraud holdout, no confidence intervals, no privacy guarantee'))
    out=ROOT/'experiments/results';pd.DataFrame(summaries).to_csv(out/'generation_quality.csv',index=False);pd.DataFrame(details).to_csv(out/'generation_quality_by_feature.csv',index=False)
    print(pd.DataFrame(summaries)[['seed','multiplier','ks_mean','wasserstein_mean','correlation_mae','synthetic_unique_fraction']].to_string(index=False))
if __name__=='__main__':main()
