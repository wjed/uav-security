# -*- coding: utf-8 -*-
"""
Publication-quality figures for the conference version.

Three data figures, every value read from an exported CSV so a figure cannot
disagree with the table beside it.

  fig2_fcount.png     unknown number of compromised clients      (two columns)
  fig3_noniid.png     robustness and failure under heterogeneity (two columns)
  fig4_trigger.png    trigger generalisation                     (one column)

Layout notes, since these were rebuilt to stop looking cramped:

  * Figs. 2 and 3 are full text width. They carry the two arguments a reviewer
    has to be convinced by, and at one column they were squeezing five series
    and two stacked panels into 3.4 in.
  * Fig. 2 labels its lines directly at the right instead of carrying a legend.
    With five series a legend is a second lookup the reader has to perform, and
    it was eating a third of the plot height.
  * Fig. 3 panel (b) puts attacker detection and attacker trust on twinned axes
    with the uniform share drawn in, because the point is that one collapses
    exactly as the other rises to a normal share.
  * Nothing is set below 8 pt, grids are horizontal only, and markers carry a
    white edge so overlapping points stay separable.

PNG at 600 dpi, double what IEEE asks for line art. Figure 1, the system and
threat model, is the authors' own diagram and is not generated here.

Run:  python build_figures.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
FIG = HERE / 'figures'
FIG.mkdir(exist_ok=True)

# IEEEtran conference geometry: the figures are written at exactly the width
# they are placed at, so LaTeX never rescales them.
COL = 3.5                      # one column, inches
FULL = 7.16                    # both columns, inches

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',        # math that matches Times, not DejaVu
    'font.size': 9.0,
    'axes.labelsize': 9.4,
    'axes.titlesize': 9.4,
    'xtick.labelsize': 8.8,
    'ytick.labelsize': 8.8,
    'legend.fontsize': 8.6,
    'axes.grid': True,
    'axes.grid.axis': 'y',             # horizontal rules only
    'axes.axisbelow': True,
    'grid.color': '#D9D9D9',
    'grid.linewidth': 0.55,
    'grid.alpha': 1.0,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.labelcolor': '#1A1A1A',
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 2.6,
    'ytick.major.size': 2.6,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'lines.linewidth': 1.6,
    'legend.frameon': False,
    'legend.handlelength': 2.1,
    'legend.columnspacing': 1.3,
    'legend.handletextpad': 0.5,
    'legend.borderpad': 0.0,
    'figure.dpi': 150,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
})

C_ATK = '#C1272D'       # attack / undefended
C_OURS = '#1B7F4B'      # proposed
C_TRUSTONLY = '#7FA845' # the trust layer on its own
C_FLT = '#2B6C8F'       # FLTrust
C_MK = '#5B3E96'        # Multi-Krum, and attacker trust in Fig. 3(b)
C_MED = '#8A8A8A'       # coordinate-wise median
C_TRIM = '#B8860B'      # trimmed mean
C_INK = '#1A1A1A'
C_MUTE = '#8C8C8C'

MEK = dict(markeredgecolor='white', markeredgewidth=0.7)
EBAR = dict(capsize=1.6, elinewidth=0.6, capthick=0.6)


def save(fig, name, target_w):
    """Write the figure so the file is exactly `target_w` inches wide.

    savefig(bbox_inches='tight') crops away the unused margin, so the file
    comes out narrower than figsize. LaTeX then stretches it to \\textwidth or
    \\columnwidth, and the scale factor differs per figure: before this was
    added Fig. 2 was being blown up 1.19x and Fig. 4 1.09x while Fig. 3 was
    left alone, so the same 9.4 pt axis label rendered at 11.2, 10.2 and 9.4 pt
    in the three figures, and Fig. 2's was larger than the 10 pt body text.

    Saving, measuring the crop and re-saving with a corrected figsize converges
    in two or three passes and pins every figure to a scale factor of 1.0, so
    the point sizes set in rcParams are the point sizes that reach the page.
    """
    path = FIG / name
    dpi = plt.rcParams['savefig.dpi']
    for _ in range(6):
        fig.savefig(path)
        got = Image.open(path).size[0] / dpi
        if abs(got - target_w) < 0.005:
            break
        fw, fh = fig.get_size_inches()
        k = target_w / got
        fig.set_size_inches(fw * k, fh * k)
    else:
        print(f'  ! {name}: width did not converge ({got:.2f} vs {target_w})')
    w, h = Image.open(path).size
    print(f'{name:20s} {w / dpi:.2f} x {h / dpi:.2f} in  (scale 1.00)')
    return path


def proxy(color, marker, linestyle='-', lw=1.6, ms=4.6):
    """A clean legend handle.

    Legend entries taken straight from errorbar() carry the cap ticks above and
    below the marker, which reads as visual noise at 8 pt. These proxies show
    the line and the marker and nothing else.
    """
    return Line2D([], [], color=color, marker=marker, linestyle=linestyle,
                  linewidth=lw, markersize=ms, **MEK)


def val(s):
    """'0.1234 +/- 0.0056' -> (0.1234, 0.0056); '12.3%' -> (0.123, 0.0)."""
    s = str(s).strip()
    if s in ('---', '', 'nan'):
        return (np.nan, 0.0)
    if s.endswith('%'):
        return (float(s[:-1]) / 100.0, 0.0)
    p = s.split('+/-')
    return (float(p[0]), float(p[1]) if len(p) > 1 else 0.0)


def spread(ys, gap):
    """Push label positions apart so none overlaps, preserving vertical order.

    Direct labelling only works if two lines that finish 0.015 apart do not get
    two 9 pt labels stacked on the same pixel. This walks the labels from the
    top down and pushes each one below its neighbour by at least `gap`, which
    is the minimum movement that resolves the collision.
    """
    ys = np.asarray(ys, dtype=float)
    out = ys.copy()
    order = np.argsort(-ys)
    for k in range(1, len(order)):
        i, prev = order[k], order[k - 1]
        if out[prev] - out[i] < gap:
            out[i] = out[prev] - gap
    return out


# =====================================================================
# Fig 2: unknown number of compromised clients        (two columns wide)
# =====================================================================
def fig_fcount():
    d = pd.read_csv(RES / 'attacker_count.csv')
    counts = sorted(d['True attackers'].unique())
    series = [
        ('Trimmed Mean ($f{=}2$)', 'Trimmed mean (f=2)', C_TRIM, ':', '^'),
        ('Multi-Krum ($f{=}2$)', 'Multi-Krum (f=2)', C_MK, '--', 's'),
        ('Coordinate-Wise Median', 'Coordinate-wise median', C_MED, (0, (5, 2)), 'v'),
        ('FLTrust', 'FLTrust', C_FLT, '-.', 'D'),
        ('Proposed (No Fixed $f$)', 'Trust + median (ours)', C_OURS, '-', 'o'),
    ]

    fig, ax = plt.subplots(figsize=(COL, 2.62))
    fig.subplots_adjust(left=0.155, right=0.985, bottom=0.155, top=0.795)

    handles, labels = [], []
    for lab, key, c, ls, mk in series:
        s = d[d['Method'] == key]
        m = [val(x)[0] for x in s['Backdoor Lift']]
        e = [val(x)[1] for x in s['Backdoor Lift']]
        ours = 'Proposed' in lab
        ax.errorbar(counts, m, yerr=e, color=c, linestyle=ls, marker=mk,
                    lw=1.9 if ours else 1.2,
                    markersize=4.4 if ours else 3.6,
                    alpha=1.0 if ours else 0.9,
                    zorder=6 if ours else 3, **EBAR, **MEK)
        handles.append(proxy(c, mk, ls, 1.9 if ours else 1.2,
                             4.4 if ours else 3.6))
        labels.append(lab)

    ax.axhline(0, color=C_INK, lw=0.9, zorder=2)
    ax.axvline(2, color='#C4C4C4', lw=0.9, linestyle=(0, (2, 2)), zorder=1)
    ax.annotate('Baselines fixed at $f{=}2$', xy=(2.08, -0.075), fontsize=7.0,
                color=C_MUTE, ha='left', va='bottom')

    ax.set_xticks(counts)
    ax.set_xlim(0.82, 4.18)
    ax.set_ylim(-0.085, 0.335)
    ax.set_yticks([0.0, 0.1, 0.2, 0.3])
    ax.set_xlabel('True Compromised Clients (of $N{=}10$)')
    ax.set_ylabel('Backdoor Lift')
    ax.legend(handles, labels, ncol=2, loc='lower center',
              bbox_to_anchor=(0.46, 1.005), fontsize=6.9, columnspacing=0.9,
              handlelength=1.9, handletextpad=0.4, labelspacing=0.32)

    save(fig, 'fig2_fcount.png', COL)
    plt.close(fig)


# =====================================================================
# Fig 3: heterogeneity, two panels side by side       (two columns wide)
# =====================================================================
def fig_noniid():
    d = pd.read_csv(RES / 'noniid_dirichlet.csv')
    conds = ['IID', 'Ratio skew a=10 (mild)', 'Ratio skew a=3 (moderate)']
    labs = ['IID',
            'Mild Skew\n' + r'($\alpha{=}10$)',
            'Moderate Skew\n' + r'($\alpha{=}3$)']
    xs = np.arange(len(conds))

    def get(meth, col):
        return [val(d[(d['Condition'] == c) & (d['Method'] == meth)].iloc[0][col])
                for c in conds]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FULL, 2.57))
    fig.subplots_adjust(left=0.062, right=0.936, bottom=0.215, top=0.845,
                        wspace=0.34)

    # ---- (a) backdoor lift ------------------------------------------
    handles, labels = [], []
    for lab, key, c, ls, mk in [
            ('FedAvg (No Defense)', 'FedAvg', C_ATK, '--', 's'),
            ('Behavioral Trust Only', 'Behavioral trust (ours)', C_TRUSTONLY, ':', '^'),
            ('Median Only', 'Coordinate-wise median', C_MED, (0, (5, 2)), 'v'),
            ('Full Defense (Proposed)', 'Trust + median (ours)', C_OURS, '-', 'o')]:
        g = get(key, 'Backdoor Lift')
        full = 'Full' in lab
        a1.errorbar(xs, [x[0] for x in g], yerr=[x[1] for x in g],
                    color=c, linestyle=ls, marker=mk,
                    lw=2.1 if full else 1.35,
                    markersize=5.2 if full else 4.2,
                    alpha=1.0 if full else 0.9,
                    zorder=6 if full else 3, **EBAR, **MEK)
        handles.append(proxy(c, mk, ls, 2.1 if full else 1.35,
                             5.2 if full else 4.2))
        labels.append(lab)
    a1.axhline(0, color=C_INK, lw=0.9, zorder=2)
    a1.set_ylabel('Backdoor Lift')
    a1.set_ylim(-0.075, 0.305)
    a1.set_yticks([0.0, 0.1, 0.2, 0.3])
    a1.set_xlim(-0.22, 2.22)
    a1.set_xticks(xs)
    a1.set_xticklabels(labs)

    # one legend for the figure, in a single row, so it cannot overhang a panel
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.005),
               ncol=4, fontsize=8.4, columnspacing=1.5, handlelength=2.0,
               handletextpad=0.5)

    # ---- (b) detection collapsing as trust normalises ---------------
    det = [x[0] for x in get('Trust + median (ours)', 'Attacker Detect')]
    trust = [x[0] for x in get('Trust + median (ours)', 'Attacker Trust')]

    a2.bar(xs, [100 * v for v in det], 0.52, color=C_OURS, alpha=0.88,
           zorder=3, edgecolor='none')
    for x, v in zip(xs, det):
        a2.annotate(f'{100 * v:.0f}%', (x, 100 * v), xytext=(0, 3),
                    textcoords='offset points', ha='center', fontsize=8.6,
                    color=C_OURS, zorder=5)
    a2.set_ylim(0, 118)
    a2.set_yticks([0, 25, 50, 75, 100])
    a2.set_ylabel('Attacker Detection (%)', color=C_OURS)
    a2.tick_params(axis='y', colors=C_OURS)
    a2.spines['left'].set_color(C_OURS)
    a2.set_xlim(-0.60, 2.60)
    a2.set_xticks(xs)
    a2.set_xticklabels(labs)

    # Attacker trust rides the right axis in a colour that means nothing else
    # in this figure, so the twinned scales cannot be confused for each other.
    a2t = a2.twinx()
    a2t.grid(False)
    a2t.spines['top'].set_visible(False)
    a2t.spines['right'].set_visible(True)
    a2t.spines['right'].set_color(C_MK)
    a2t.axhline(0.100, color=C_MK, alpha=0.45, lw=0.9, linestyle=(0, (4, 3)),
                zorder=2)
    a2t.annotate('Uniform share', xy=(0.52, 0.1045), fontsize=7.9,
                 color=C_MK, alpha=0.8, ha='left', va='bottom')
    a2t.plot(xs, trust, color=C_MK, marker='o', markersize=5.2, lw=1.9,
             zorder=6, **MEK)
    a2t.set_ylim(0, 0.128)
    a2t.set_yticks([0.00, 0.05, 0.10])
    a2t.set_ylabel('Mean Attacker Trust', color=C_MK)
    a2t.tick_params(axis='y', colors=C_MK)
    a2t.set_zorder(a2.get_zorder() + 1)
    a2t.patch.set_visible(False)

    for ax, letter in ((a1, '(a)'), (a2, '(b)')):
        box = ax.get_position()
        fig.text(box.x0 + box.width / 2, 0.042, letter, ha='center',
                 va='bottom', fontsize=9.4, fontweight='bold', color=C_INK)

    save(fig, 'fig3_noniid.png', FULL)
    plt.close(fig)


# =====================================================================
# Fig 4: trigger generalisation                        (one column wide)
# =====================================================================
def fig_trigger():
    d = pd.read_csv(RES / 'trigger_comparison.csv')
    keep = ['CN0', 'TCD', 'PD', 'CN0+TCD']
    d = d[d['Trigger'].isin(keep)].set_index('Trigger').loc[keep].reset_index()
    xs = np.arange(len(keep))
    und = [val(x) for x in d['Attack lift']]
    dfd = [val(x) for x in d['Defended lift']]

    fig, ax = plt.subplots(figsize=(COL, 2.28))
    fig.subplots_adjust(left=0.185, right=0.975, bottom=0.205, top=0.845)

    ylo, yhi = -0.148, 0.325
    # everything at or below zero is "no advantage over an honest fleet"
    ax.axhspan(ylo, 0, color=C_OURS, alpha=0.05, zorder=0, linewidth=0)

    for i, (u, f) in enumerate(zip(und, dfd)):
        ax.plot([i, i], [u[0], f[0]], color='#CFCFCF', lw=1.6, zorder=1,
                solid_capstyle='round')
    ax.errorbar(xs, [u[0] for u in und], yerr=[u[1] for u in und], fmt='s',
                color=C_ATK, markersize=5.4, zorder=4, linestyle='none',
                **EBAR, **MEK)
    ax.errorbar(xs, [f[0] for f in dfd], yerr=[f[1] for f in dfd], fmt='o',
                color=C_OURS, markersize=5.4, zorder=4, linestyle='none',
                **EBAR, **MEK)

    ax.axhline(0, color=C_INK, lw=0.9, zorder=2)
    ax.annotate('At or below an honest fleet', xy=(3.42, -0.140), fontsize=7.6,
                color=C_OURS, alpha=0.75, ha='right', va='bottom')

    ax.set_xticks(xs)
    ax.set_xticklabels(keep)
    ax.set_xlim(-0.45, 3.45)
    ax.set_ylim(ylo, yhi)
    ax.set_yticks([-0.1, 0.0, 0.1, 0.2, 0.3])
    ax.set_xlabel('Feature Carrying the Trigger')
    ax.set_ylabel('Backdoor Lift')
    ax.legend([proxy(C_ATK, 's', 'none', ms=5.4),
               proxy(C_OURS, 'o', 'none', ms=5.4)],
              ['Undefended', 'Defended'],
              ncol=2, loc='lower center', bbox_to_anchor=(0.5, 1.005),
              fontsize=8.6, columnspacing=1.6, handletextpad=0.35)

    save(fig, 'fig4_trigger.png', COL)
    plt.close(fig)


if __name__ == '__main__':
    fig_fcount(); fig_noniid(); fig_trigger()
    print(f'\nwrote 3 figures to {FIG}')
