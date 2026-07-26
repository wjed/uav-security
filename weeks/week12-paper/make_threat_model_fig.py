# -*- coding: utf-8 -*-
"""
Build figures/Threat_model_new.png for main.tex.

main.tex referenced this figure but it was never committed, so the paper could
not compile. Drawn here rather than in a drawing tool so it stays in the repo
and can be regenerated. Sized for a 3.2 in single-column IEEE slot.

Run from this folder:  python make_threat_model_fig.py
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent / 'figures' / 'Threat_model_new.png'
OUT.parent.mkdir(parents=True, exist_ok=True)

PURPLE = '#450084'; GOLD = '#CBB677'; RED = '#A4232B'
GREY = '#595959'; LIGHT = '#F4EFE1'; DARK = '#333333'

fig, ax = plt.subplots(figsize=(7.6, 4.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis('off')

def box(x, y, w, h, fc, ec, text, fs=8.0, tc=DARK, weight='normal', lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.06',
                                fc=fc, ec=ec, lw=lw, zorder=2))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=fs, color=tc, weight=weight, zorder=3, linespacing=1.35)

def arrow(x1, y1, x2, y2, color, lw=1.3, ls='-'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                 mutation_scale=11, color=color, lw=lw,
                                 linestyle=ls, zorder=1, shrinkA=2, shrinkB=2))

CW, CX = 2.30, 0.35          # client box width / left edge
AGG_L, AGG_R = 6.55, 9.80    # aggregator left / right
AGG_B, AGG_T = 3.00, 4.95    # aggregator bottom / top

# ---------------- honest clients ----------------
ax.text(CX + CW / 2, 6.28, 'Honest UAV clients', ha='center', fontsize=8.5,
        color=PURPLE, weight='bold')
for lab, y in [(r'$U_1$   local data $\mathcal{D}_1$', 5.35),
               (r'$U_2$   local data $\mathcal{D}_2$', 4.62)]:
    box(CX, y, CW, 0.58, 'white', GREY, lab, fs=8)
ax.text(CX + CW / 2, 4.34, r'$\vdots$', ha='center', va='center', fontsize=11, color=GREY)
box(CX, 3.52, CW, 0.58, 'white', GREY, r'$U_8$   local data $\mathcal{D}_8$', fs=8)

# ---------------- compromised clients ----------------
ax.text(CX + CW / 2, 3.14, 'Compromised clients', ha='center', fontsize=8.5,
        color=RED, weight='bold')
box(CX, 2.28, CW, 0.58, '#FBEDEE', RED, r'$U_9$   poisoned $\mathcal{D}_9$', fs=8, tc=RED)
box(CX, 1.58, CW, 0.58, '#FBEDEE', RED, r'$U_{10}$   poisoned $\mathcal{D}_{10}$', fs=8, tc=RED)

# poisoning recipe, clear of the client boxes above it
box(0.02, 0.62, 2.96, 0.60, LIGHT, GOLD,
    'poison 40% of spoofed rows:\nCN0 $\\rightarrow$ benign-high, label $\\rightarrow$ authentic',
    fs=6.5, tc=DARK, lw=0.9)

# ---------------- aggregator ----------------
box(AGG_L, AGG_B, AGG_R - AGG_L, AGG_T - AGG_B, 'white', PURPLE, '', lw=1.6)
cx = (AGG_L + AGG_R) / 2
ax.text(cx, 4.66, 'Aggregator', ha='center', fontsize=9, color=PURPLE, weight='bold')
ax.text(cx, 4.38, '(ground station)', ha='center', fontsize=6.8, color=GREY)
ax.text(cx, 3.88, r'$\lambda_i = \mathrm{Acc}_i / \sum_k \mathrm{Acc}_k$',
        ha='center', fontsize=8.2, color=DARK)
ax.text(cx, 3.32, r'$\omega(t{+}1)=\omega(t)+\sum_i \lambda_i \Delta\omega_i$',
        ha='center', fontsize=8.2, color=DARK)

# the exploited property
box(6.35, 2.10, 3.65, 0.60, LIGHT, GOLD,
    'weight comes from a self-reported number\nthe aggregator cannot verify',
    fs=6.6, tc=DARK, lw=0.9)

# ---------------- uplinks ----------------
for y in (5.64, 4.91, 3.81):
    arrow(CX + CW, y, AGG_L, 4.15, GREY, lw=1.0)
ax.text(4.60, 5.08, r'$\omega_i,\ \mathrm{Acc}_i$', ha='center', fontsize=7.6,
        color=GREY, bbox=dict(fc='white', ec='none', pad=0.8))

for y in (2.57, 1.87):
    arrow(CX + CW, y, AGG_L, 3.35, RED, lw=1.4)
ax.text(4.70, 1.62,
        'scaled update  $\\omega(t)+\\gamma\\,\\Delta\\omega_m$\n'
        'inflated  $\\widehat{\\mathrm{Acc}}_m = 0.99$',
        ha='center', fontsize=7.4, color=RED,
        bbox=dict(fc='white', ec=RED, lw=0.7, boxstyle='round,pad=0.28'))

# ---------------- broadcast back ----------------
arrow(cx - 0.6, AGG_T, CX + CW * 0.55, 6.02, PURPLE, lw=1.3, ls='--')
ax.text(4.75, 6.16, r'global model $\omega(t{+}1)$  (carries the backdoor)',
        ha='center', fontsize=7.4, color=PURPLE)

fig.tight_layout()
fig.savefig(OUT, dpi=300, bbox_inches='tight', facecolor='white')
print('wrote', OUT)
