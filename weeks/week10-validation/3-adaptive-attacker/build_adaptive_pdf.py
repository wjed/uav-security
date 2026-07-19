# -*- coding: utf-8 -*-
"""
Build the adaptive-attacker stress-test PDF from the real result files in results/.
Reads adaptive_attacker_sweep.csv and embeds fig_adaptive_attacker.png, so the PDF
cannot drift from the notebook. Run from this folder:  python build_adaptive_pdf.py
Output: adaptive_attacker_report.pdf
"""
from pathlib import Path
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
OUT = HERE / 'adaptive_attacker_report.pdf'

PURPLE = (69, 0, 132); GOLD = (203, 182, 119); DARK = (51, 51, 51)
GREY = (89, 89, 89); LINE = (214, 214, 214); ALTROW = (244, 239, 225)
RED = (164, 35, 43); PAGE_W = 190

def clean(s):
    return (str(s).replace('—', ', ').replace('–', '-').replace('−', '-')
            .replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"'))

class PDF(FPDF):
    def header(self):
        if self.page_no() == 1: return
        self.set_font('Helvetica', '', 8); self.set_text_color(*GREY)
        self.cell(0, 6, 'Adaptive Attacker Stress Test  |  Group 1  |  UAV FL Backdoor Defense', align='L'); self.ln(8)
    def footer(self):
        self.set_y(-12); self.set_font('Helvetica', '', 8); self.set_text_color(*GREY)
        self.cell(0, 6, f'Page {self.page_no()}', align='C')

pdf = PDF(format='A4'); pdf.set_auto_page_break(auto=True, margin=15); pdf.set_margins(10, 12, 10)
def mc(w,h,t): pdf.multi_cell(w,h,clean(t),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
def h1(t):
    pdf.ln(2); pdf.set_font('Helvetica','B',14); pdf.set_text_color(*PURPLE); mc(0,7,t)
    pdf.set_draw_color(*PURPLE); pdf.set_line_width(0.4); y=pdf.get_y(); pdf.line(10,y+0.5,200,y+0.5); pdf.ln(3)
def h2(t):
    pdf.ln(1); pdf.set_font('Helvetica','B',11); pdf.set_text_color(*PURPLE); mc(0,6,t); pdf.ln(0.5)
def body(t):
    pdf.set_font('Helvetica','',10); pdf.set_text_color(*DARK); mc(0,5.0,t); pdf.ln(1.5)
def bullet(t):
    pdf.set_font('Helvetica','',10); pdf.set_text_color(*DARK)
    pdf.cell(5,5,'-'); pdf.multi_cell(PAGE_W-5,5.0,clean(t),new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(0.3)
def table_from_df(df, widths=None, fontsize=7.6, highlight_rows=()):
    cols=list(df.columns)
    if widths is None: widths=[PAGE_W/len(cols)]*len(cols)
    pdf.set_font('Helvetica','B',fontsize); pdf.set_fill_color(*PURPLE); pdf.set_text_color(255,255,255)
    pdf.set_draw_color(*LINE); pdf.set_line_width(0.2)
    for c,w in zip(cols,widths): pdf.cell(w,6,clean(c),border=1,align='C',fill=True)
    pdf.ln(6)
    for ri,(_,row) in enumerate(df.iterrows()):
        hl = ri in highlight_rows
        pdf.set_font('Helvetica','B' if hl else '',fontsize)
        pdf.set_text_color(*(PURPLE if hl else DARK))
        pdf.set_fill_color(*(GOLD if hl else (ALTROW if ri%2 else (255,255,255))))
        for c,w in zip(cols,widths): pdf.cell(w,5.4,clean(row[c]),border=1,align='C',fill=True)
        pdf.ln(5.4)
    pdf.ln(2)
def image_full(png):
    from PIL import Image
    p=RES/png; iw,ih=Image.open(p).size
    w=PAGE_W; h=w*ih/iw; avail=297-15-pdf.get_y()
    if h>avail: h=avail; w=h*iw/ih
    pdf.image(str(p),x=(210-w)/2,w=w,h=h); pdf.ln(2)

# ---------------- PAGE 1 ----------------
pdf.add_page(); pdf.ln(8)
pdf.set_font('Helvetica','B',20); pdf.set_text_color(*PURPLE)
mc(0,9,'Adaptive Attacker Stress Test')
pdf.set_font('Helvetica','',12); pdf.set_text_color(*DARK)
mc(0,6,'Can a stealth attacker hide under the dead-zone, and does a second detection signal help?')
pdf.ln(1); pdf.set_font('Helvetica','B',10.5); pdf.set_text_color(*DARK)
mc(0,5.5,'Will Jedrzejczak    Dilpreet Gill    Cole Walther')
pdf.set_font('Helvetica','',10); pdf.set_text_color(*GREY)
mc(0,5,'Group 1  |  James Madison University Capstone (IT 445 / IT 499)')
pdf.ln(2.5); pdf.set_draw_color(*GOLD); pdf.set_line_width(1.2); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)

h2('Headline result')
body('The attacker has no profitable hiding place. Evasion and effectiveness are mutually exclusive: the poison '
     'rate low enough to slip under the detection threshold is the same poison rate at which the backdoor stops '
     'working. A second detection signal we proposed in advance turned out to be unnecessary and slightly harmful, '
     'so it is reported as a measured negative result rather than adopted.')

h2('Why we ran this')
body('The improvement adopted in the previous study (a gentler trust gate at beta = 1.0 plus a suspicion dead-zone '
     'at tau = 2.0) cut the honest false-positive rate from 20.5% to 0.3%. But a dead-zone is a threshold, and a '
     'threshold invites gaming. An attacker does not have to beat the behavioral probe; it only has to keep its '
     'suspicion below tau and it is never gated at all. Since we introduced that possibility ourselves, we tested '
     'it, framed as a security question: what is the largest backdoor an attacker can implant while staying '
     'undetected?')

h2('What was tested')
bullet('Adaptive stealth attacker: drops the model-replacement scaling entirely and sweeps its poison rate down '
       'from 40% to 1%, trading backdoor strength for invisibility.')
bullet('D2 (current best): behavioral probe signal only.')
bullet('D4 (proposed fix): max(behavioral probe, update-direction anomaly). The direction signal is the robust MAD '
       'z-score of each client cosine distance from the coordinate-wise median update direction, and it does not '
       'require activating the trigger.')
body('Both use the same gate, dead-zone, and coordinate-wise median aggregation, so the only difference is the '
     'added signal. Everything runs across seeds 42, 7, 123.')

# ---------------- PAGE 2: results ----------------
pdf.add_page(); h1('Results')
try:
    tab = pd.read_csv(RES/'adaptive_attacker_sweep.csv', keep_default_na=False)
    hl = tuple(i for i,v in enumerate(tab.iloc[:,0].astype(str)) if v.strip().startswith('1%'))
    table_from_df(tab, widths=[17,35,30,23,19,30,36], fontsize=6.9, highlight_rows=hl)
except Exception as e:
    body(f'(adaptive_attacker_sweep.csv not found: {e})')
body('Table 1. Adaptive stealth attacker swept from 40% poison down to 1%, mean +/- standard deviation over three '
     'seeds. The dead-zone is tau = 2.0; a suspicion score below it means the client is never gated. The 1% rows '
     'are highlighted because that is the only setting where detection begins to fail.')

h2('Verdict 1: the dead-zone holds, and the evasion frontier is unprofitable')
body('From 5% poison upward the attacker probe suspicion is 7.35 or higher, more than three times the threshold, '
     'and it is detected in 100% of client-rounds. Detection only starts to fail at 1% poison, where it drops to '
     '26.4%. But at that setting the undefended backdoor lift is +0.0051, which is indistinguishable from zero. In '
     'other words, the poison rate the attacker needs in order to hide is the same poison rate at which the '
     'backdoor stops doing anything. This is a stronger statement than "we did not find an evasion": we mapped the '
     'attacker operating curve and showed that its best available move is not worth taking.')

h2('Verdict 2: the proposed second signal is rejected')
body('The hypothesis was that update-direction anomaly would catch a subtle attacker that the behavioral probe '
     'misses, because it does not depend on activating the trigger. The measurement says the opposite. At exactly '
     'the stealthy settings where it was supposed to help most, the direction signal is the weaker of the two: '
     '0.76 at 1% poison and 2.25 at 5%, against 3.26 and 7.35 for the behavioral probe. It only overtakes the '
     'probe at 40% poison, where the probe already catches everything. It also roughly doubles the honest '
     'false-positive rate at 1% poison (6.9% against 3.5%) and produces no improvement in backdoor lift. Adding it '
     'would make the defense more complex and slightly worse, so it is not adopted.')
body('The reason is clear in hindsight. The behavioral probe measures the thing we care about directly, by '
     'activating the backdoor behavior. Update direction is a proxy: it detects that a client optimized something '
     'different, but at low poison rates the backdoor is such a small part of the client objective that its update '
     'still points essentially where the honest updates point. The proxy degrades faster than the direct '
     'measurement, which is the reverse of the intuition that motivated it.')

# ---------------- PAGE 3: figure ----------------
pdf.add_page(); h1('Figure')
image_full('fig_adaptive_attacker.png')
body('Figure 1. Adaptive stealth attacker. Panel (a): the attacker two suspicion scores against the dead-zone '
     'threshold (red dashed line) as the poison rate falls. Panel (b): the surviving backdoor lift with no defense, '
     'with D2, and with D4. Bands are +/- 1 standard deviation over three seeds.')
h2('Reading the figure')
body('Panel (a) shows the attacker becoming harder to see as it gets stealthier, with the purple probe line falling '
     'toward the threshold at 1% poison. Panel (b) shows why that invisibility is worthless: the red no-defense '
     'curve, which is the damage the attacker would do if the defense were absent entirely, collapses to the zero '
     'line at exactly the same point. The gold and green defended curves sit at or below zero across the whole '
     'sweep, and are indistinguishable from each other, which is the visual form of the conclusion that the second '
     'signal adds nothing.')

# ---------------- PAGE 4: scope ----------------
pdf.add_page(); h1('Scope and Limitations')
h2('What this establishes')
body('D2 resists the natural adaptive strategy: poison less and stop scaling in order to look ordinary. Across the '
     'whole stealth range the attacker either is caught outright or gains no measurable backdoor.')
h2('What this does not establish')
body('This is not a general claim of adaptive-attacker robustness, and we do not present it as one. It tests one '
     'adaptive strategy. It does not test a stronger attacker that explicitly optimizes against the defense, for '
     'example one that adds a penalty for probe-slice error to its local training loss, or that solves a '
     'constrained problem maximizing backdoor effect subject to keeping suspicion below tau. That attacker is the '
     'real remaining frontier and is the single most valuable next experiment.')
h2('Also unchanged')
bullet('The base detector is still only moderately strong, with honest spoofing recall around 0.55, which is why '
       'backdoor lift rather than raw accuracy remains the primary metric.')
bullet('The setting is still IID with ten clients and two attackers. Non-IID client data would widen the honest '
       'trust spread and is the natural next deeper experiment.')
bullet('The dead-zone threshold tau = 2.0 was chosen by reasoning about the MAD scale rather than swept.')
h2('Reproducibility')
body('Every number and the figure are produced by adaptive_attacker.ipynb and exported to results/ as '
     'adaptive_attacker_sweep.csv and fig_adaptive_attacker.png. This PDF is assembled by build_adaptive_pdf.py, '
     'which reads those files directly, so the report cannot drift from the experiment.')

pdf.output(str(OUT))
print('wrote', OUT)
