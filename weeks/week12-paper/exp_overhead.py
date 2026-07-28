# -*- coding: utf-8 -*-
"""
Reviewer comment 6: the 1.1% overhead figure is measured against a sequential
simulation in which every client's training time is summed. Real clients train
in parallel, so the honest denominator is the *slowest* client, not the sum,
and the true percentage is larger.

This script recomputes the overhead properly and reports all five quantities
the review asks for:
  * absolute server overhead in milliseconds per round
  * overhead as a percentage of a sequential-simulation round
  * overhead as a percentage of a parallel round (max client, not sum)
  * scaling with the number of clients
  * scaling with root-set size and with the number of probe features

It also times FLTrust on the same basis, because FLTrust trains a server model
on the root set every round and is therefore the more expensive root-of-trust
defense; that comparison belongs next to our own cost claim.

Run from this folder:  python exp_overhead.py
Outputs: results/overhead_analysis.csv, results/overhead_scaling.csv,
         results/fig_overhead.png
"""
import copy, time
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt

import fl_common as F
from fl_common import (BinaryDNN, D, get_p, set_p, train_local, coord_median,
                       weighted_mean, behavioral_trust, fltrust, N_CLIENTS, N_ATTACK)

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})

REPS = 3   # rounds timed per configuration


def time_round(clients, n_clients, probe_feats, root_X, root_y, probe_slices,
               seed=F.DATA_SEED):
    """One round: per-client training times, plus each server rule's own cost."""
    F.reseed(seed)
    g = BinaryDNN(D)
    gp = get_p(g)
    client_ms, locs, models = [], [], []
    for i in range(n_clients):
        c = clients[i % len(clients)]
        m = copy.deepcopy(g)
        t0 = time.perf_counter()
        train_local(m, c['Xt'], c['yt'])
        client_ms.append((time.perf_counter() - t0) * 1000.0)
        models.append(m)
        locs.append(get_p(m))

    t0 = time.perf_counter()
    weighted_mean(locs, [1 / n_clients] * n_clients)
    base_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    t = behavioral_trust(models, probe_feats=probe_feats, root_X=root_X,
                         root_y=root_y, probe_slices=probe_slices)
    scaled = [[gg + n_clients * tt * (pp - gg) for gg, pp in zip(gp, params)]
              for tt, params in zip(t, locs)]
    coord_median(scaled)
    ours_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    sm = copy.deepcopy(g)
    train_local(sm, root_X, root_y)
    fltrust(locs, gp, get_p(sm))
    fl_ms = (time.perf_counter() - t0) * 1000.0

    return dict(client_ms=client_ms, base_ms=base_ms,
                ours_ms=ours_ms - base_ms, fltrust_ms=fl_ms - base_ms)


def agg(runs):
    cm = np.concatenate([r['client_ms'] for r in runs])
    return dict(
        client_sum=float(np.mean([np.sum(r['client_ms']) for r in runs])),
        client_max=float(np.mean([np.max(r['client_ms']) for r in runs])),
        client_mean=float(cm.mean()),
        ours=float(np.mean([r['ours_ms'] for r in runs])),
        fltrust=float(np.mean([r['fltrust_ms'] for r in runs])),
        base=float(np.mean([r['base_ms'] for r in runs])),
    )


clients = F.iid_split(F.DATA_SEED)
PS_full = F.PROBE_SLICES

print('overhead analysis | timing is wall-clock on CPU, averaged over '
      f'{REPS} rounds\n')

# ---------------------------------------------------- headline (10 clients)
runs = [time_round(clients, N_CLIENTS, F.PROBE_FEATS, F.X_root_sc, F.y_root,
                   PS_full, seed=F.DATA_SEED + k) for k in range(REPS)]
a = agg(runs)
seq_round = a['client_sum'] + a['base']
par_round = a['client_max'] + a['base']
rows = []
for name, srv in (('Behavioral trust + median (ours)', a['ours']),
                  ('FLTrust', a['fltrust'])):
    rows.append({
        'Defense': name,
        'Server overhead (ms/round)': f"{srv:.1f}",
        'Sequential round (ms)': f"{seq_round:.0f}",
        'Overhead vs sequential': f"{100*srv/seq_round:.2f}%",
        'Parallel round (ms)': f"{par_round:.0f}",
        'Overhead vs parallel': f"{100*srv/par_round:.2f}%",
    })
head = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print(head.to_string(index=False))
head.to_csv(F.RESULTS / 'overhead_analysis.csv', index=False)
print(f"\nwrote {F.RESULTS/'overhead_analysis.csv'}")
print(f"  slowest client {a['client_max']:.0f} ms | mean client {a['client_mean']:.0f} ms | "
      f"sum {a['client_sum']:.0f} ms | plain aggregation {a['base']:.2f} ms")

# ---------------------------------------------------- scaling sweeps
scal = []

for n in (5, 10, 20, 40):
    r = [time_round(clients, n, F.PROBE_FEATS, F.X_root_sc, F.y_root, PS_full,
                    seed=F.DATA_SEED + k) for k in range(REPS)]
    aa = agg(r)
    scal.append({'Axis': 'clients', 'Setting': n,
                 'Server ms/round': f"{aa['ours']:.1f}",
                 'FLTrust ms/round': f"{aa['fltrust']:.1f}",
                 'Overhead vs parallel': f"{100*aa['ours']/(aa['client_max']+aa['base']):.2f}%"})
    print(f"clients={n:>3}  ours {aa['ours']:7.1f} ms   fltrust {aa['fltrust']:7.1f} ms")

for nroot in (600, 1500, 3000, 6000):
    rX, rY = F.X_root_sc[:nroot], F.y_root[:nroot]
    rs = rX[rY == 1]
    ps = {}
    for f in F.PROBE_FEATS:
        fi = F.FEATURES.index(f); z = rs.copy(); z[:, fi] = F.BENIGN_HIGH[f]; ps[f] = z
    r = [time_round(clients, N_CLIENTS, F.PROBE_FEATS, rX, rY, ps,
                    seed=F.DATA_SEED + k) for k in range(REPS)]
    aa = agg(r)
    scal.append({'Axis': 'root rows', 'Setting': nroot,
                 'Server ms/round': f"{aa['ours']:.1f}",
                 'FLTrust ms/round': f"{aa['fltrust']:.1f}",
                 'Overhead vs parallel': f"{100*aa['ours']/(aa['client_max']+aa['base']):.2f}%"})
    print(f"root={nroot:>5}  ours {aa['ours']:7.1f} ms   fltrust {aa['fltrust']:7.1f} ms")

for k_ in (2, 4, 6, 8):
    pf = F.PROBE_FEATS[:k_]
    r = [time_round(clients, N_CLIENTS, pf, F.X_root_sc, F.y_root, PS_full,
                    seed=F.DATA_SEED + j) for j in range(REPS)]
    aa = agg(r)
    scal.append({'Axis': 'probe features', 'Setting': k_,
                 'Server ms/round': f"{aa['ours']:.1f}",
                 'FLTrust ms/round': '---',
                 'Overhead vs parallel': f"{100*aa['ours']/(aa['client_max']+aa['base']):.2f}%"})
    print(f"probes={k_:>3}  ours {aa['ours']:7.1f} ms")

sc = pd.DataFrame(scal)
print('\nScaling\n')
print(sc.to_string(index=False))
sc.to_csv(F.RESULTS / 'overhead_scaling.csv', index=False)
print(f"\nwrote {F.RESULTS/'overhead_scaling.csv'}")

# ------------------------------------------------------------------- figure
fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.7))
for ax, axis, xlabel in zip(axes, ('clients', 'root rows', 'probe features'),
                            ('number of clients', 'root-set rows', 'probe features')):
    sub = sc[sc['Axis'] == axis]
    xs = sub['Setting'].astype(float).values
    ys = sub['Server ms/round'].astype(float).values
    ax.plot(xs, ys, marker='o', lw=1.9, color='seagreen', label='ours')
    fl = sub['FLTrust ms/round'].values
    if not any(v == '---' for v in fl):
        ax.plot(xs, fl.astype(float), marker='D', ls=':', lw=1.7,
                color='#3C738B', label='FLTrust')
    ax.set_xlabel(xlabel); ax.set_ylabel('server ms/round')
    ax.legend(fontsize=8)
axes[0].set_title('Scaling with fleet size')
axes[1].set_title('Scaling with root-set size')
axes[2].set_title('Scaling with probe count')
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_overhead.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_overhead.png'}")
