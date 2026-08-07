# -*- coding: utf-8 -*-
"""
Publication-quality figures for the six-page conference version.

Four figures, all sized for a single IEEE column (3.4 in) so they can sit
inline without a full-width float, and all typeset at 8-9 pt so they stay
legible at print size. Every value is read from the exported CSVs, so the
figures cannot disagree with the tables.

  fig1_system.pdf     system and threat model, redrawn
  fig2_fcount.pdf     unknown number of compromised clients
  fig3_noniid.pdf     robustness and failure under client heterogeneity
  fig4_trigger.pdf    trigger generalisation

PDF output rather than PNG: vector figures stay sharp at any zoom, which is
what a camera-ready submission wants.

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
# Fig 1: system and threat model
# =====================================================================
def fig_system():
    """Left: the federation. Right: the threat model. Base: the defense.

    Each region occupies a reserved band of the canvas, so annotations cannot
    collide with the uplinks or spill out of their panel.
    """
    fig, ax = plt.subplots(figsize=(COL, 1.95))
    ax.set_xlim(0, 100); ax.set_ylim(0, 56)
    ax.axis('off')

    def box(x, y, w, h, label, fc, ec, fs=7.3, tc=C_INK):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle='round,pad=0.7,rounding_size=1.9',
                     linewidth=0.9, facecolor=fc, edgecolor=ec, zorder=3))
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
                fontsize=fs, color=tc, zorder=4, linespacing=1.2)

    # ---------------- federation, confined to x < 62
    box(2, 39, 56, 11.5,
        'Coordinator\n' + r'root set $\mathcal{D}_r$  |  probes $\mathcal{S}_f$',
        '#EDE7F4', '#5B3E96', fs=7.1)

    for k, x in enumerate((1, 11.5, 22)):
        box(x, 13, 9.5, 8, f'$U_{k+1}$', '#FFFFFF', '#777777')
    ax.text(34, 17.0, r'$\cdots$', ha='center', va='center',
            fontsize=8.5, color='#777777')
    for k, x in enumerate((39, 50)):
        box(x, 13, 10, 8, f'$U_{{{9+k}}}$', '#FBECEC', C_ATK, tc=C_ATK)

    for x in (5.8, 16.3, 26.8):
        ax.add_patch(FancyArrowPatch((x, 21.4), (24, 38.4), arrowstyle='-|>',
                     mutation_scale=5.5, lw=0.6, color='#A0A0A0', zorder=1))
    for x in (44, 55):
        ax.add_patch(FancyArrowPatch((x, 21.4), (38, 38.4), arrowstyle='-|>',
                     mutation_scale=5.5, lw=1.1, color=C_ATK, zorder=2))
    ax.add_patch(FancyArrowPatch((6, 38.4), (3.2, 21.4), arrowstyle='-|>',
                 mutation_scale=5.5, lw=0.7, color='#5B3E96',
                 linestyle=(0, (2.5, 1.8)), zorder=1))

    ax.text(0.5, 29.5, r'$\omega(t)$', fontsize=6.7, color='#5B3E96', ha='left')
    ax.text(30.0, 29.5, r'$\omega_i^{I}(t),\ \mathrm{Acc}_i$', fontsize=6.7,
            color='#777777', ha='center')
    ax.text(16, 9.6, 'honest', fontsize=6.5, color='#777777', ha='center')
    ax.text(49, 9.6, 'compromised', fontsize=6.5, color=C_ATK,
            ha='center', fontweight='bold')

    # ---------------- threat model, reserved band x > 64
    ax.add_patch(FancyBboxPatch((64.5, 12.5), 34.5, 38,
                 boxstyle='round,pad=0.7,rounding_size=1.9',
                 linewidth=0.85, facecolor='#FDF6F6', edgecolor=C_ATK, zorder=3))
    ax.text(81.8, 46.6, 'Threat model', ha='center', va='center',
            fontsize=7.1, color=C_ATK, fontweight='bold', zorder=4)
    for y, s in ((39.5, 'A1  poison $p{=}40\\%$ of\n        each attacker\'s spoofed rows'),
                 (28.0, 'A2  scale update by $\\gamma{=}3$'),
                 (20.5, 'A3  report $\\widehat{\\mathrm{Acc}}_m{=}0.99$')):
        ax.text(66.5, y, s, fontsize=6.6, color=C_ATK, ha='left', va='top',
                zorder=4, linespacing=1.4)

    # ---------------- defense
    ax.add_patch(Rectangle((1, 0), 98, 6.0, facecolor='#EAF3EE',
                           edgecolor=C_OURS, lw=0.85, zorder=0))
    ax.text(50, 3.0,
            r'score $\omega_i$ by behaviour on $\mathcal{S}_f$ '
            r'$-$ never by $\mathrm{Acc}_i$',
            ha='center', va='center', fontsize=7.0, color=C_OURS)

    fig.savefig(FIG / 'fig1_system.pdf'); fig.savefig(FIG / 'preview_fig1.png', dpi=200)
    plt.close(fig)
    print('fig1_system.pdf')


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
    fig.savefig(FIG / 'fig2_fcount.pdf'); fig.savefig(FIG / 'preview_fig2.png', dpi=200)
    plt.close(fig)
    print('fig2_fcount.pdf')


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

    fig.savefig(FIG / 'fig3_noniid.pdf'); fig.savefig(FIG / 'preview_fig3.png', dpi=200)
    plt.close(fig)
    print('fig3_noniid.pdf')


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
    fig.savefig(FIG / 'fig4_trigger.pdf'); fig.savefig(FIG / 'preview_fig4.png', dpi=200)
    plt.close(fig)
    print('fig4_trigger.pdf')


if __name__ == '__main__':
    fig_system(); fig_fcount(); fig_noniid(); fig_trigger()
    print(f'\nwrote 4 figures to {FIG}')
