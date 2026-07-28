# -*- coding: utf-8 -*-
"""
Reviewer comment 4: the base spoofing detector is too weak for strong
practical security claims (honest spoofing recall about 0.53).

The comment asks whether a stronger classifier would help, and demands that
the paper stop conflating two different claims. This script answers the first
question empirically so the second can be answered honestly.

It establishes a *centralised ceiling*: several classifiers, from logistic
regression to gradient boosting, trained on the entire 114,000-row pool with
no federation, no attack and no privacy constraint. That is strictly more
favourable than anything the federated system can achieve. If a strong
non-linear model trained centrally also plateaus near 0.5 recall, then the
limit is the feature set, not the architecture, and the honest conclusion is
that this dataset supports claims about *relative* backdoor lift but not about
absolute operational reliability. If instead a stronger model does much
better, the federated detector should be upgraded.

Also reports the full operating point the reviewer asked for (precision,
recall, F1, balanced accuracy, false-alarm rate, confusion matrix) and, for
the MLP actually used, its triggered-sample behaviour, so the paper can state
plainly what fraction of triggered spoofing an honest model already misses.

Run from this folder:  python exp_detector.py
Outputs: results/detector_ceiling.csv, results/fig_detector_ceiling.png
"""
import copy
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

import fl_common as F

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})


def report(name, kind, yhat, ytrig_hat):
    tp = int(((yhat == 1) & (F.y_test == 1)).sum())
    fn = int(((yhat == 0) & (F.y_test == 1)).sum())
    fp = int(((yhat == 1) & (F.y_test == 0)).sum())
    tn = int(((yhat == 0) & (F.y_test == 0)).sum())
    rec = tp / max(tp + fn, 1)
    prec = tp / max(tp + fp, 1)
    spec = tn / max(tn + fp, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-12)
    return {
        'Model': name, 'Type': kind,
        'Clean Accuracy': f'{(yhat == F.y_test).mean():.4f}',
        'Spoofing Recall': f'{rec:.4f}',
        'Precision': f'{prec:.4f}',
        'F1': f'{f1:.4f}',
        'Balanced Acc': f'{0.5*(rec+spec):.4f}',
        'False Alarm Rate': f'{fp/max(fp+tn,1):.4f}',
        'TP': tp, 'FN': fn, 'FP': fp, 'TN': tn,
        'Triggered BSR': f'{(ytrig_hat == 0).mean():.4f}',
        '_rec': rec, '_f1': f1,
    }


rows = []
print(f'centralised ceiling study | pool {len(F.X_pool_sc):,} rows | '
      f'test {len(F.X_test_sc):,} rows | {len(F.FEATURES)} features\n')

# ---- the MLP actually used in the federated system, trained centrally
for widths, tag in [((64, 32, 16), 'MLP 64-32-16 (paper model)'),
                    ((256, 128, 64), 'MLP 256-128-64 (wider)'),
                    ((512, 256, 128, 64), 'MLP 512-256-128-64 (deeper)')]:
    F.reseed(F.DATA_SEED)
    m = F.BinaryDNN(F.D, widths=widths)
    F.train_local(m, F.X_pool_sc, F.y_pool, epochs=30)
    r = report(tag, f'centralised, {F.n_params(m):,} params',
               F.preds(m, F.X_test_sc), F.preds(m, F.X_TRIG))
    rows.append(r)
    print(f"{tag:<34} recall {r['Spoofing Recall']} f1 {r['F1']} BSR {r['Triggered BSR']}")

# ---- classical baselines, also centralised
for name, clf in [
        ('Logistic regression', LogisticRegression(max_iter=2000)),
        ('Random forest (400 trees)', RandomForestClassifier(
            n_estimators=400, n_jobs=-1, random_state=F.DATA_SEED)),
        ('Hist gradient boosting', HistGradientBoostingClassifier(
            max_iter=400, random_state=F.DATA_SEED))]:
    clf.fit(F.X_pool_sc, F.y_pool)
    r = report(name, 'centralised, sklearn',
               clf.predict(F.X_test_sc), clf.predict(F.X_TRIG))
    rows.append(r)
    print(f"{name:<34} recall {r['Spoofing Recall']} f1 {r['F1']} BSR {r['Triggered BSR']}")

# ---- the federated honest baseline, for reference
from fl_runner import run
fed = []
for sd in F.SEEDS:
    h = run(F.iid_split(sd), sd, 'fedavg', attack=False)
    fed.append(h)
rows.append({
    'Model': 'Federated honest FedAvg (paper baseline)', 'Type': 'federated, 10 clients',
    'Clean Accuracy': f"{np.mean([h['clean'] for h in fed]):.4f}",
    'Spoofing Recall': f"{np.mean([h['recall'] for h in fed]):.4f}",
    'Precision': f"{np.mean([h['precision'] for h in fed]):.4f}",
    'F1': f"{np.mean([h['f1'] for h in fed]):.4f}",
    'Balanced Acc': f"{np.mean([h['balacc'] for h in fed]):.4f}",
    'False Alarm Rate': f"{np.mean([h['far'] for h in fed]):.4f}",
    'TP': int(np.mean([h['tp'] for h in fed])), 'FN': int(np.mean([h['fn'] for h in fed])),
    'FP': int(np.mean([h['fp'] for h in fed])), 'TN': int(np.mean([h['tn'] for h in fed])),
    'Triggered BSR': f"{np.mean([h['bsr'] for h in fed]):.4f}",
    '_rec': float(np.mean([h['recall'] for h in fed])),
    '_f1': float(np.mean([h['f1'] for h in fed])),
})
print(f"{'Federated honest FedAvg':<34} recall {rows[-1]['Spoofing Recall']} "
      f"f1 {rows[-1]['F1']} BSR {rows[-1]['Triggered BSR']}")

tab = pd.DataFrame(rows).drop(columns=['_rec', '_f1'])
pd.set_option('display.width', 250)
print('\nCentralised ceiling vs the federated detector\n')
print(tab.to_string(index=False))
tab.to_csv(F.RESULTS / 'detector_ceiling.csv', index=False)
print(f"\nwrote {F.RESULTS/'detector_ceiling.csv'}")

# also record how separable the classes are at all, which is the real story
d = F.cohens_d()
print('\nper-feature Cohen\'s d: ' +
      ', '.join(f'{k}={v:.3f}' for k, v in sorted(d.items(), key=lambda x: -x[1])))

# ------------------------------------------------------------------- figure
names = [r['Model'] for r in rows]
rec = [r['_rec'] for r in rows]
f1s = [r['_f1'] for r in rows]
xs = np.arange(len(names))
fig, ax = plt.subplots(figsize=(9.6, 4.4))
cols = ['#B599CE'] * 3 + ['#B2B2B2'] * 3 + ['seagreen']
ax.bar(xs - 0.19, rec, 0.38, color=cols, label='spoofing recall')
ax.bar(xs + 0.19, f1s, 0.38, color=cols, alpha=.55, label='F1')
ax.axhline(rec[-1], color='seagreen', ls=':', lw=1.4)
ax.annotate(f'federated honest recall ({rec[-1]:.3f})', (len(names) - 0.6, rec[-1]),
            ha='right', va='bottom', fontsize=8.5, color='seagreen')
ax.set_xticks(xs)
ax.set_xticklabels([n.replace(' (', '\n(') for n in names], rotation=18, ha='right', fontsize=8)
ax.set_ylabel('score on the held-out test set')
ax.set_title("Detector ceiling: no centralised model escapes the feature set's separability")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_detector_ceiling.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_detector_ceiling.png'}")
