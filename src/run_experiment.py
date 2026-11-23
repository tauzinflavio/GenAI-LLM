"""Première comparaison sur validation ; aucun accès au test final."""
import hashlib
import json
import platform
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from scipy.io import arff
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_curve, precision_score, recall_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from torch import nn

ROOT = Path(__file__).resolve().parents[1]


class NoisePredictor(nn.Module):
    def __init__(self, dimensions, hidden):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(dimensions + 3, hidden), nn.SiLU(),
                                     nn.Linear(hidden, hidden), nn.SiLU(), nn.Linear(hidden, dimensions))

    def forward(self, x, t):
        position = t.float().unsqueeze(1)
        embedding = torch.cat([position, torch.sin(position * torch.pi), torch.cos(position * torch.pi)], dim=1)
        return self.network(torch.cat([x, embedding], dim=1))


def feature_matrix(frame):
    values = frame[[f'V{i}' for i in range(1, 29)] + ['Amount']].to_numpy(dtype=np.float64, copy=True)
    if not np.isfinite(values).all() or (values[:, -1] < 0).any():
        raise ValueError('Entrée incompatible avec log1p Amount.')
    values[:, -1] = np.log1p(values[:, -1])
    return values


def fit_detector(x_train, y_train, x_validation, y_validation, name, seed, weight=None):
    start = time.perf_counter()
    model = LogisticRegression(C=1.0, max_iter=2000, class_weight=weight, random_state=seed)
    model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    scores = model.predict_proba(x_validation)[:, 1]
    inference_seconds = time.perf_counter() - start
    precision, recall, thresholds = precision_recall_curve(y_validation, scores)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    threshold = float(thresholds[np.argmax(f1)])
    predictions = scores >= threshold
    result = dict(configuration=name, seed=seed, split='validation', status='mesure',
                  average_precision=float(average_precision_score(y_validation, scores)),
                  threshold=threshold, precision=float(precision_score(y_validation, predictions, zero_division=0)),
                  recall=float(recall_score(y_validation, predictions)), alerts=int(predictions.sum()),
                  fit_seconds=fit_seconds, validation_batch_seconds=inference_seconds,
                  threshold_status='choisi_sur_ce_meme_jeu_validation_exploratoire', train_rows=len(y_train))
    return model, scores, result


def train_diffusion(frauds, seed, config, directory):
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(frauds))
    count = max(1, int(len(order) * config['internal_holdout_fraction']))
    heldout, training = frauds[order[:count]], frauds[order[count:]]
    scaler = StandardScaler().fit(training)
    x = torch.tensor(scaler.transform(training), dtype=torch.float32)
    heldout_tensor = torch.tensor(scaler.transform(heldout), dtype=torch.float32)
    torch.manual_seed(seed)
    model = NoisePredictor(x.shape[1], config['hidden_size'])
    optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'])
    steps = config['timesteps']
    beta = torch.linspace(config['beta_start'], config['beta_end'], steps)
    alpha = 1 - beta
    cumulative = torch.cumprod(alpha, dim=0)
    losses = []
    start = time.perf_counter()
    model.train()
    for update in range(config['updates']):
        batch = x[torch.randint(len(x), (config['batch_size'],))]
        t = torch.randint(steps, (len(batch),))
        noise = torch.randn_like(batch)
        weights = cumulative[t].unsqueeze(1)
        noisy = weights.sqrt() * batch + (1 - weights).sqrt() * noise
        prediction = model(noisy, t / (steps - 1))
        loss = nn.functional.mse_loss(prediction, noise)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if update % 100 == 0:
            losses.append({'update': update, 'noise_mse_training_batch': float(loss.detach())})
    training_seconds = time.perf_counter() - start
    model.eval()
    # Bruits gelés sur des fraudes exclues de l'apprentissage du générateur.
    torch.manual_seed(seed + 10000)
    examples = []
    with torch.no_grad():
        for i in range(10):
            original = heldout_tensor[i:i+1]
            t = int(round(i * (steps - 1) / 9))
            noise = torch.randn_like(original)
            weight = cumulative[t]
            noisy = weight.sqrt() * original + (1 - weight).sqrt() * noise
            predicted = model(noisy, torch.tensor([t / (steps - 1)]))
            examples.append(dict(case_id=f'D{seed}-{i+1:02}',seed=seed,t=t,
                                 baseline_zero_noise_mse=float(noise.square().mean()),
                                 ddpm_noise_mse=float((predicted-noise).square().mean()),
                                 status='mesure', verification='MSE bruit connu',
                                 generator_training_excluded=True))
    joblib.dump(scaler, directory / f'generator_scaler_{seed}.joblib')
    torch.save(model.state_dict(), directory / f'ddpm_{seed}.pt')
    pd.DataFrame(losses).to_csv(directory / f'training_loss_{seed}.csv', index=False)
    return model, scaler, beta, alpha, cumulative, training_seconds, examples, training


def sample_diffusion(model, scaler, beta, alpha, cumulative, count, seed):
    torch.manual_seed(seed)
    start = time.perf_counter()
    with torch.no_grad():
        x = torch.randn(count, model.network[-1].out_features)
        for t in reversed(range(len(beta))):
            predicted_noise = model(x, torch.full((count,), t / (len(beta) - 1)))
            mean = (x - beta[t] / torch.sqrt(1 - cumulative[t]) * predicted_noise) / alpha[t].sqrt()
            previous = cumulative[t-1] if t else torch.tensor(1.0)
            posterior_variance = beta[t] * (1 - previous) / (1 - cumulative[t])
            x = mean + posterior_variance.sqrt() * torch.randn_like(x) if t else mean
    return scaler.inverse_transform(x.numpy()), time.perf_counter() - start


def main():
    config_path = ROOT / 'configs/experiment_v1.json'
    config = json.loads(config_path.read_text())
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    output = ROOT / 'experiments/v1'
    output.mkdir(parents=True, exist_ok=True)
    models = ROOT / 'models'
    models.mkdir(exist_ok=True)
    raw, _ = arff.loadarff(ROOT / 'data/raw/creditcard.arff')
    frame = pd.DataFrame(raw)
    train_ids = pd.read_csv(ROOT / 'data/processed/train_indices.csv').source_row_index.to_numpy()
    validation_ids = pd.read_csv(ROOT / 'data/processed/validation_indices.csv').source_row_index.to_numpy()
    assert not np.intersect1d(train_ids, validation_ids).size
    train, validation = frame.iloc[train_ids], frame.iloc[validation_ids]
    x_train, x_validation = feature_matrix(train), feature_matrix(validation)
    y_train = train.Class.astype(int).to_numpy()
    y_validation = validation.Class.astype(int).to_numpy()
    scaler = StandardScaler().fit(x_train)
    scaled_train, scaled_validation = scaler.transform(x_train), scaler.transform(x_validation)
    joblib.dump(scaler, models / 'detector_scaler.joblib')
    records, generation_metrics, denoising_cases = [], [], []
    for seed in config['seeds']:
        for name, weight in [('B0_original', None), ('B1_class_weight', 'balanced')]:
            model, scores, result = fit_detector(scaled_train, y_train, scaled_validation, y_validation, name, seed, weight)
            records.append(result)
            joblib.dump(model, models / f'{name}_{seed}.joblib')
            np.save(output / f'{name}_{seed}_validation_scores.npy', scores)
            print(name, seed, result['average_precision'], flush=True)
        diffusion, gen_scaler, beta, alpha, cumulative, fit_time, examples, gen_train = train_diffusion(x_train[y_train == 1], seed, config['ddpm'], output)
        denoising_cases.extend(examples)
        rng = np.random.default_rng(seed)
        for multiplier in config['augmentation_multipliers']:
            count = int((y_train == 1).sum()) * multiplier
            synthetic, sample_time = sample_diffusion(diffusion, gen_scaler, beta, alpha, cumulative, count, seed + multiplier)
            # Vérification puis sélection documentée ; aucune troncature silencieuse des montants.
            valid = np.isfinite(synthetic).all(axis=1) & (synthetic[:, -1] >= 0) & (synthetic[:, -1] <= np.log1p(1e9))
            accepted = synthetic[valid]
            if not len(accepted):
                raise ValueError('Aucun échantillon synthétique valide.')
            pd.DataFrame(accepted, columns=[f'V{i}' for i in range(1,29)]+['log1p_Amount']).to_csv(output / f'synthetic_{seed}_x{multiplier}.csv', index=False)
            distances = NearestNeighbors(n_neighbors=1).fit(gen_scaler.transform(gen_train)).kneighbors(gen_scaler.transform(accepted))[0][:,0]
            generation_metrics.append(dict(seed=seed,multiplier=multiplier,requested=count,accepted=len(accepted),
                rejected=int((~valid).sum()),fit_seconds=fit_time,sampling_seconds=sample_time,
                nearest_train_distance_median=float(np.median(distances)),
                near_copies_below_1e_6=int((distances < 1e-6).sum()), terminal_alpha_bar=float(cumulative[-1])))
            # Rééchantillonnage avec exactement le même nombre d'ajouts que les sorties DDPM acceptées.
            duplicated = x_train[y_train == 1][rng.integers((y_train == 1).sum(), size=len(accepted))]
            for name, extra in [(f'B2_random_over_x{multiplier}', duplicated), (f'G1_ddpm_x{multiplier}', accepted)]:
                augmented = np.concatenate([scaled_train, scaler.transform(extra)])
                labels = np.concatenate([y_train, np.ones(len(extra), dtype=int)])
                model, scores, result = fit_detector(augmented, labels, scaled_validation, y_validation, name, seed)
                records.append(result)
                joblib.dump(model, models / f'{name}_{seed}.joblib')
                np.save(output / f'{name}_{seed}_validation_scores.npy', scores)
                print(name, seed, result['average_precision'], flush=True)
        pd.DataFrame(records).to_csv(output / 'metrics.csv', index=False)
        pd.DataFrame(generation_metrics).to_csv(output / 'generation_metrics.csv', index=False)
        pd.DataFrame(denoising_cases).to_csv(output / 'denoising_cases.csv', index=False)
    metadata = dict(config=config,config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
                    python=platform.python_version(),platform=platform.platform(),torch=torch.__version__,
                    train_rows=len(train),validation_rows=len(validation),test_evaluated=False,
                    detector_features=29,generator_class='fraud_only_unconditional',
                    note='DDPM gaussien simple, pas reproduction complète de TabDDPM ; résultats validation exploratoires')
    (output / 'run_metadata.json').write_text(json.dumps(metadata,indent=2))
    pd.DataFrame(records).groupby('configuration').average_precision.agg(['mean','std']).to_csv(output / 'summary.csv')
    print('Expérience terminée ; test final non évalué.', flush=True)


if __name__ == '__main__':
    main()
