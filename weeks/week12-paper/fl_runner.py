# -*- coding: utf-8 -*-
"""
One federated training run under any of the aggregation rules in fl_common.

Kept separate from fl_common so the rules themselves stay readable and every
experiment drives them through exactly one code path. `run()` returns the
final metric suite plus, where the rule produces one, the per-round trust
matrix used for attacker-detection and honest-false-flag accounting.
"""
from __future__ import annotations
import copy, time
import numpy as np
import torch

from fl_common import (
    BinaryDNN, D, N_CLIENTS, N_ATTACK, FL_ROUNDS, BOOST, FAKE_ACC,
    DEF_BETA, DEF_TAU, DEF_EMA, UNIFORM, FLAG_THRESH,
    X_root_sc, y_root, acc, get_p, set_p, train_local, preds, metrics, reseed,
    coord_median, weighted_mean, trimmed_mean, krum, fltrust, behavioral_trust,
)

# rules that expose a per-client weight we can audit for detection/false flags
TRUST_RULES = {'accweight', 'fltrust', 'trust', 'full'}
ALL_RULES = ['fedavg', 'accweight', 'median', 'trimmed', 'krum', 'multikrum',
             'fltrust', 'trust', 'full']


def run(clients, seed, rule, attack=True, boost=BOOST, rounds=FL_ROUNDS,
        widths=(64, 32, 16), beta=DEF_BETA, tau=DEF_TAU, ema=DEF_EMA,
        root_X=None, root_y=None, probe_slices=None, probe_feats=None,
        time_server=False, n_attack=None, assumed_f=None):
    """Train `rounds` federated rounds under `rule`; return metrics + trust.

    `attack` toggles the compromised clients' update scaling and accuracy
    inflation. Their poisoned *data* is baked into `clients` by fl_common.poison,
    so an honest baseline should be passed an unpoisoned split.

    `n_attack`  the true number of compromised clients (default: the module
                constant). Controls which clients scale and inflate, and which
                columns of the trust matrix are audited as attackers.
    `assumed_f` the f that the Byzantine-robust rules are *configured* with
                (default: the module constant, i.e. correctly specified). Kept
                separate from n_attack so an experiment can misconfigure the
                baselines the way a real deployment would have to guess. The
                proposed rules ignore it entirely: they have no such parameter.
    """
    na = N_ATTACK if n_attack is None else n_attack
    af = N_ATTACK if assumed_f is None else assumed_f
    reseed(seed)
    g = BinaryDNN(D, widths=widths)
    prev = None
    trust_hist, sel_hist = [], []
    server_ms = 0.0

    for _ in range(rounds):
        gp = get_p(g)
        locs, models, rep_acc = [], [], []
        for i, c in enumerate(clients):
            m = copy.deepcopy(g)
            train_local(m, c['Xt'], c['yt'])
            models.append(m)
            lp = get_p(m)
            is_atk = attack and i >= N_CLIENTS - na
            if is_atk:
                lp = [gg + boost * (pp - gg) for gg, pp in zip(gp, lp)]
            locs.append(lp)
            # what the client *claims*; only accweight consumes this
            rep_acc.append(FAKE_ACC if is_atk else acc(m, c['Xv'], c['yv']))

        t0 = time.perf_counter()
        t = None
        if rule == 'fedavg':
            new = weighted_mean(locs, [1 / len(locs)] * len(locs))
        elif rule == 'accweight':
            a = np.asarray(rep_acc, dtype=float)
            t = a / a.sum()
            new = weighted_mean(locs, list(t))
        elif rule == 'median':
            new = coord_median(locs)
        elif rule == 'trimmed':
            new = trimmed_mean(locs, f=af)
        elif rule in ('krum', 'multikrum'):
            m_sel = 1 if rule == 'krum' else N_CLIENTS - af
            new, chosen = krum(locs, gp, f=af, m=m_sel)
            sel_hist.append(chosen)
        elif rule == 'fltrust':
            sm = copy.deepcopy(g)
            train_local(sm, X_root_sc if root_X is None else root_X,
                        y_root if root_y is None else root_y)
            new, t = fltrust(locs, gp, get_p(sm))
        elif rule in ('trust', 'full'):
            t = behavioral_trust(models, beta=beta, tau=tau,
                                 probe_feats=probe_feats, root_X=root_X,
                                 root_y=root_y, probe_slices=probe_slices)
            if prev is not None:
                t = ema * t + (1 - ema) * prev
            prev = t
            scaled = [[gg + N_CLIENTS * tt * (pp - gg) for gg, pp in zip(gp, params)]
                      for tt, params in zip(t, locs)]
            new = coord_median(scaled) if rule == 'full' else weighted_mean(scaled, [1 / N_CLIENTS] * N_CLIENTS)
        else:
            raise ValueError(f'unknown rule {rule}')
        if time_server:
            server_ms += (time.perf_counter() - t0) * 1000.0

        if t is not None:
            trust_hist.append(np.asarray(t, dtype=float).copy())
        set_p(g, new)

    out = metrics(g)
    out['rule'] = rule
    out['server_ms_per_round'] = server_ms / rounds if time_server else None

    T = np.array(trust_hist) if trust_hist else None
    S = np.array(sel_hist) if sel_hist else None
    out['trust'] = T
    a0 = N_CLIENTS - na
    if T is not None:
        out['atk_trust'] = float(T[:, a0:].mean())
        out['hon_trust'] = float(T[:, :a0].mean())
        out['atk_detect'] = float((T[:, a0:] < FLAG_THRESH).mean())
        out['hon_flag'] = float((T[:, :a0] < FLAG_THRESH).mean())
    elif S is not None:
        # Krum makes a competitive *selection*, not a per-client trust
        # assignment, so a trust value and an honest false-flag rate are not
        # comparably defined: single-Krum necessarily excludes 7 of 8 honest
        # clients every round by construction, which is not a false positive.
        # Only attacker exclusion is meaningful, and it is reported as such.
        out['atk_trust'] = None
        out['hon_trust'] = None
        out['atk_detect'] = float((S[:, a0:] == 0).mean())
        out['hon_flag'] = None
        out['atk_selected'] = float((S[:, a0:] == 1).mean())
    else:
        for k in ('atk_trust', 'hon_trust', 'atk_detect', 'hon_flag'):
            out[k] = None
    return out


def ms(vals, sign=False, nd=4):
    v = [x for x in vals if x is not None]
    if not v:
        return '---'
    m, s = float(np.mean(v)), float(np.std(v))
    return f'{m:+.{nd}f} +/- {s:.{nd}f}' if sign else f'{m:.{nd}f} +/- {s:.{nd}f}'


def pct(vals, nd=1):
    v = [x for x in vals if x is not None]
    return '---' if not v else f'{100*float(np.mean(v)):.{nd}f}%'
