# -*- coding: utf-8 -*-
"""
Publication-quality figures for the six-page conference version.

Four figures, all sized for a single IEEE column (3.4 in) so they can sit
inline without a full-width float, and all typeset at 8-9 pt so they stay
legible at print size. Every value is read from the exported CSVs, so the
figures cannot disagree with the tables.

  fig2_fcount.png     unknown number of compromised clients
  fig3_noniid.png     robustness and failure under client heterogeneity
  fig4_trigger.png    trigger generalisation

PNG at 600 dpi. That is well above the 300 dpi IEEE asks for line art, so it
prints cleanly, and it is easier to handle than vector output. Figure 1, the
system and threat model, is the authors' own diagram and is not generated here.

Run:  python build_figures.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
FIG = HERE / 'figures'
FIG.mkdir(exist_ok=True)

COL = 3.4                      # single IEEE column width, inches
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 8.2,
    'axes.labelsize': 8.4,
    'axes.titlesize': 8.6,
    'xtick.labelsize': 7.8,
    'ytick.labelsize': 7.8,
    'legend.fontsize': 7.4,
    'axes.grid': True,
    'grid.alpha': 0.28,
    'grid.linewidth': 0.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.7,
    'lines.linewidth': 1.5,
    'lines.markersize': 4.0,
    'legend.frameon': False,
    'figure.dpi': 150,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.015,
})

C_ATK = '#C1272D'       # attack / undefended
C_OURS = '#1B7F4B'      # proposed
C_FLT = '#2B6C8F'       # FLTrust
C_MK = '#5B3E96'        # Multi-Krum
C_MED = '#8A8A8A'       # median
C_TRIM = '#B8860B'      # trimmed mean
C_INK = '#1A1A1A'


def val(s):
    """'0.1234 +/- 0.0056' -> (0.1234, 0.0056); '12.3%' -> (0.123, 0)."""
    s = str(s).strip()
    if s in ('---', '', 'nan'):
        return (np.nan, 0.0)
    if s.endswith('%'):
        return (float(s[:-1]) / 100.0, 0.0)
    p = s.split('+/-')
    return (float(p[0]), float(p[1]) if len(p) > 1 else 0.0)


# =====================================================================
# Fig 2: unknown number of compromised clients
# =====================================================================
def fig_fcount():
    d = pd.read_csv(RES / 'attacker_count.csv')
    counts = sorted(d['True attackers'].unique())
    series = [
        ('Trimmed mean ($f{=}2$)', 'Trimmed mean (f=2)', C_TRIM, ':', '^'),
        ('Multi-Krum ($f{=}2$)', 'Multi-Krum (f=2)', C_MK, '--', 's'),
        ('FLTrust', 'FLTrust', C_FLT, '-.', 'D'),
        ('Coord. median', 'Coordinate-wise median', C_MED, (0, (4, 2)), 'v'),
        ('Proposed (no $f$)', 'Trust + median (ours)', C_OURS, '-', 'o'),
    ]
    fig, ax = plt.subplots(figsize=(COL, 2.18))
    for lab, key, c, ls, mk in series:
        s = d[d['Method'] == key]
        m = [val(x)[0] for x in s['Backdoor Lift']]
        e = [val(x)[1] for x in s['Backdoor Lift']]
        ax.errorbar(counts, m, yerr=e, label=lab, color=c, linestyle=ls,
                    marker=mk, capsize=2, elinewidth=0.7,
                    lw=1.8 if 'Proposed' in lab else 1.3,
                    markersize=4.4 if 'Proposed' in lab else 3.6,
                    zorder=5 if 'Proposed' in lab else 3)
    ax.axhline(0, color=C_INK, lw=0.8)
    ax.axvline(2, color='#BBBBBB', lw=0.8, linestyle=(0, (2, 2)), zorder=0)
    ax.annotate('baselines assume $f{=}2$', xy=(2.06, -0.076), fontsize=6.6,
                color='#777777', ha='left', va='bottom')
    ax.set_xticks(counts)
    ax.set_xlabel('true number of compromised clients (of $N{=}10$)')
    ax.set_ylabel('backdoor lift')
    ax.set_ylim(-0.09, 0.345)
    ax.legend(ncol=2, loc='upper left', columnspacing=0.9,
              handlelength=1.9, handletextpad=0.5, borderpad=0.2)
    fig.savefig(FIG / 'fig2_fcount.png')
    plt.close(fig)
    print('fig2_fcount.png')


# =====================================================================
# Fig 3: heterogeneity, two panels
# =====================================================================
def fig_noniid():
    d = pd.read_csv(RES / 'noniid_dirichlet.csv')
    conds = ['IID', 'Ratio skew a=10 (mild)', 'Ratio skew a=3 (moderate)']
    labs = ['IID', 'mild skew\n' + r'($\alpha{=}10$)', 'moderate skew\n' + r'($\alpha{=}3$)']
    xs = np.arange(len(conds))

    def get(meth, col):
        return [val(d[(d['Condition'] == c) & (d['Method'] == meth)].iloc[0][col])
                for c in conds]

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL, 3.35), sharex=True,
                                 gridspec_kw={'hspace': 0.16})

    for lab, key, c, ls, mk in [
            ('FedAvg (no defense)', 'FedAvg', C_ATK, '--', 's'),
            ('Behavioral trust only', 'Behavioral trust (ours)', '#7FA845', ':', '^'),
            ('Coord. median only', 'Coordinate-wise median', C_MED, (0, (4, 2)), 'v'),
            ('Full defense (proposed)', 'Trust + median (ours)', C_OURS, '-', 'o')]:
        g = get(key, 'Backdoor Lift')
        a1.errorbar(xs, [x[0] for x in g], yerr=[x[1] for x in g], label=lab,
                    color=c, linestyle=ls, marker=mk, capsize=2, elinewidth=0.7,
                    lw=1.8 if 'Full' in lab else 1.3,
                    markersize=4.4 if 'Full' in lab else 3.6,
                    zorder=5 if 'Full' in lab else 3)
    a1.axhline(0, color=C_INK, lw=0.8)
    a1.set_ylabel('backdoor lift')
    a1.set_ylim(-0.07, 0.44)
    a1.legend(ncol=2, loc='upper left', columnspacing=0.8,
              handlelength=1.9, handletextpad=0.5, borderpad=0.2)
    a1.text(0.985, 0.06, '(a)', transform=a1.transAxes, ha='right',
            fontsize=8.0, fontweight='bold')

    w = 0.46
    det = [x[0] for x in get('Trust + median (ours)', 'Attacker Detect')]
    trust = [x[0] for x in get('Trust + median (ours)', 'Attacker Trust')]
    bars = a2.bar(xs, [100 * v for v in det], w, color=C_OURS, zorder=3)
    for x, v, tr in zip(xs, det, trust):
        a2.annotate(f'{100*v:.0f}%', (x, 100 * v), xytext=(0, 2.4),
                    textcoords='offset points', ha='center', fontsize=7.0,
                    color=C_INK)
        a2.annotate(f'trust {tr:.4f}', (x, 100 * v), xytext=(0, 11),
                    textcoords='offset points', ha='center', fontsize=6.3,
                    color='#777777')
    a2.set_xticks(xs); a2.set_xticklabels(labs)
    a2.set_ylabel('attacker detection (%)')
    a2.set_ylim(0, 128)
    a2.set_yticks([0, 25, 50, 75, 100])
    a2.text(0.985, 0.90, '(b)', transform=a2.transAxes, ha='right',
            fontsize=8.0, fontweight='bold')

    fig.savefig(FIG / 'fig3_noniid.png')
    plt.close(fig)
    print('fig3_noniid.png')


# =====================================================================
# Fig 4: trigger generalisation
# =====================================================================
def fig_trigger():
    d = pd.read_csv(RES / 'trigger_comparison.csv')
    keep = ['CN0', 'TCD', 'PD', 'CN0+TCD']
    d = d[d['Trigger'].isin(keep)].set_index('Trigger').loc[keep].reset_index()
    xs = np.arange(len(keep))
    und = [val(x) for x in d['Attack lift']]
    dfd = [val(x) for x in d['Defended lift']]

    fig, ax = plt.subplots(figsize=(COL, 1.92))
    for i, (u, f) in enumerate(zip(und, dfd)):
        ax.plot([i, i], [u[0], f[0]], color='#C8C8C8', lw=1.1, zorder=1)
    ax.errorbar(xs, [u[0] for u in und], yerr=[u[1] for u in und], fmt='s',
                color=C_ATK, capsize=2.4, elinewidth=0.8, markersize=4.6,
                label='undefended', zorder=3, linestyle='none')
    ax.errorbar(xs, [f[0] for f in dfd], yerr=[f[1] for f in dfd], fmt='o',
                color=C_OURS, capsize=2.4, elinewidth=0.8, markersize=4.6,
                label='defended (same configuration)', zorder=3, linestyle='none')
    ax.axhline(0, color=C_INK, lw=0.8)
    ax.set_xticks(xs); ax.set_xticklabels(keep)
    ax.set_xlim(-0.45, len(keep) - 0.55)
    ax.set_xlabel('feature carrying the trigger')
    ax.set_ylabel('backdoor lift')
    ax.set_ylim(-0.15, 0.44)
    ax.legend(loc='upper right', handletextpad=0.4, borderpad=0.2)
    fig.savefig(FIG / 'fig4_trigger.png')
    plt.close(fig)
    print('fig4_trigger.png')


if __name__ == '__main__':
    fig_fcount(); fig_noniid(); fig_trigger()
    print(f'\nwrote 3 figures to {FIG}')
