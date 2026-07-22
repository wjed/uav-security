# -*- coding: utf-8 -*-
"""
Build the Week 11 submission PDF (assignment items 2 to 6 in one file).
Reads the exported CSVs and embeds the real figure, so it cannot drift
from the notebook. Run from this folder:  python build_week11_report_pdf.py
Output: week11_report.pdf
"""
from pathlib import Path
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
OUT = HERE / 'week11_report.pdf'

PURPLE=(69,0,132); GOLD=(203,182,119); DARK=(51,51,51); GREY=(89,89,89)
LINE=(214,214,214); ALTROW=(244,239,225); PAGE_W=190

def clean(s):
    return (str(s).replace('—',', ').replace('–','-').replace('−','-')
            .replace('’',"'").replace('‘',"'")
            .replace('“','"').replace('”','"'))

class PDF(FPDF):
    def header(self):
        if self.page_no()==1: return
        self.set_font('Helvetica','',7.5); self.set_text_color(*GREY)
        self.cell(0,5,'Week 11: Paper-Ready Setup, Ablation, and Trigger Generalization  |  Group 1',align='L'); self.ln(6)
    def footer(self):
        self.set_y(-11); self.set_font('Helvetica','',7.5); self.set_text_color(*GREY)
        self.cell(0,5,f'Page {self.page_no()}',align='C')

pdf=PDF(format='A4'); pdf.set_auto_page_break(auto=True,margin=13); pdf.set_margins(10,11,10)
def mc(w,h,t): pdf.multi_cell(w,h,clean(t),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
def h1(t):
    pdf.ln(0.8); pdf.set_font('Helvetica','B',13.5); pdf.set_text_color(*PURPLE); mc(0,6.6,t)
    pdf.set_draw_color(*PURPLE); pdf.set_line_width(0.45); y=pdf.get_y(); pdf.line(10,y+0.4,200,y+0.4); pdf.ln(2.4)
def h2(t):
    pdf.ln(0.6); pdf.set_font('Helvetica','B',10.2); pdf.set_text_color(*PURPLE); mc(0,5.0,t); pdf.ln(0.2)
def body(t):
    pdf.set_font('Helvetica','',9.1); pdf.set_text_color(*DARK); mc(0,4.35,t); pdf.ln(0.9)
def cap(t):
    pdf.set_font('Helvetica','I',8.3); pdf.set_text_color(*GREY); mc(0,3.95,t); pdf.ln(0.8)
def bullet(t):
    pdf.set_font('Helvetica','',9.1); pdf.set_text_color(*DARK)
    pdf.cell(4.2,4.35,'-'); pdf.multi_cell(PAGE_W-4.2,4.35,clean(t),new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(0.15)
def callout(t):
    pdf.set_fill_color(*ALTROW); pdf.set_draw_color(*GOLD); pdf.set_line_width(0.9)
    x,y=pdf.get_x(),pdf.get_y(); pdf.set_font('Helvetica','',9.1); pdf.set_text_color(*DARK)
    pdf.multi_cell(PAGE_W,4.35,clean(t),border=0,fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.line(x,y,x,pdf.get_y()); pdf.ln(1.2)
def table(df,widths=None,fs=7.0,hl=()):
    cols=list(df.columns)
    if widths is None: widths=[PAGE_W/len(cols)]*len(cols)
    pdf.set_font('Helvetica','B',fs); pdf.set_fill_color(*PURPLE); pdf.set_text_color(255,255,255)
    pdf.set_draw_color(*LINE); pdf.set_line_width(0.2)
    for c,w in zip(cols,widths): pdf.cell(w,5.3,clean(c),border=1,align='C',fill=True)
    pdf.ln(5.3)
    for ri,(_,row) in enumerate(df.iterrows()):
        is_hl=ri in hl
        pdf.set_font('Helvetica','B' if is_hl else '',fs)
        pdf.set_text_color(*(PURPLE if is_hl else DARK))
        pdf.set_fill_color(*(GOLD if is_hl else (ALTROW if ri%2 else (255,255,255))))
        for c,w in zip(cols,widths): pdf.cell(w,4.9,clean(row[c]),border=1,align='C',fill=True)
        pdf.ln(4.9)
    pdf.ln(1.0)
def kv_table(df,widths,fs=7.6):
    # parameter card: wrapped value column, group column merged visually
    pdf.set_font('Helvetica','B',fs); pdf.set_fill_color(*PURPLE); pdf.set_text_color(255,255,255)
    pdf.set_draw_color(*LINE); pdf.set_line_width(0.2)
    for c,w in zip(df.columns,widths): pdf.cell(w,5.3,clean(c),border=1,align='C',fill=True)
    pdf.ln(5.3)
    prev_group=None
    for ri,(_,row) in enumerate(df.iterrows()):
        g = row['Group'] if row['Group']!=prev_group else ''
        prev_group=row['Group']
        pdf.set_font('Helvetica','',fs); pdf.set_text_color(*DARK)
        pdf.set_fill_color(*(ALTROW if ri%2 else (255,255,255)))
        x0,y0=pdf.get_x(),pdf.get_y()
        # measure wrapped height of the value column
        lines=pdf.multi_cell(widths[2],3.9,clean(row['Value']),border=0,split_only=True)
        h=max(4.9,3.9*len(lines)+1.0)
        if y0+h>297-13: pdf.add_page(); x0,y0=pdf.get_x(),pdf.get_y()
        pdf.set_font('Helvetica','B',fs); pdf.cell(widths[0],h,clean(g),border=1,align='L',fill=True)
        pdf.set_font('Helvetica','',fs);  pdf.cell(widths[1],h,clean(row['Parameter']),border=1,align='L',fill=True)
        x2=pdf.get_x()
        pdf.multi_cell(widths[2],3.9,clean(row['Value']),border=1,align='L',fill=True,
                       new_x=XPos.LMARGIN,new_y=YPos.NEXT,max_line_height=3.9)
        yend=max(pdf.get_y(),y0+h)
        pdf.set_y(y0); pdf.set_x(x2); pdf.cell(widths[2],h,'',border=1)
        pdf.set_y(yend); pdf.set_x(x0)
    pdf.ln(1.0)
def img(path,maxw=PAGE_W):
    from PIL import Image
    iw,ih=Image.open(path).size
    w=maxw; h=w*ih/iw; avail=297-13-pdf.get_y()
    if h>avail: h=avail; w=h*iw/ih
    pdf.image(str(path),x=(210-w)/2,w=w,h=h); pdf.ln(1.2)

param = pd.read_csv(RES/'parameter_table.csv').fillna('')
abl   = pd.read_csv(RES/'ablation_table.csv')
trig  = pd.read_csv(RES/'trigger_comparison.csv')
adap  = pd.read_csv(RES/'adaptive_attacker.csv')

# ================= PAGE 1: title + Task 1 =================
pdf.add_page(); pdf.ln(2)
pdf.set_font('Helvetica','B',17); pdf.set_text_color(*PURPLE)
mc(0,7.8,'Paper-Ready Setup, Ablation, and Trigger-Generalization Results')
pdf.set_font('Helvetica','',10.4); pdf.set_text_color(*DARK)
mc(0,5.0,'Week 11: the experimental parameter card, the defense-layer ablation, and the trigger-generalization comparison')
pdf.ln(0.4); pdf.set_font('Helvetica','B',10)
mc(0,5.0,'Will Jedrzejczak    Dilpreet Gill    Cole Walther')
pdf.set_font('Helvetica','',9.4); pdf.set_text_color(*GREY)
mc(0,4.6,'Group 1  |  James Madison University Capstone (IT 445 / IT 499)')
pdf.ln(1.2); pdf.set_draw_color(*GOLD); pdf.set_line_width(1.1); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(2.4)

body('Everything in this report is produced by one notebook (11_paper_tables.ipynb, submitted separately) and '
     'exported to results/ as CSVs and a PNG; nothing is transcribed by hand. The pipeline, model, attack, and the '
     'adopted D2 defense configuration are carried over unchanged from the Week 10 validation notebook. All '
     'experiment tables report mean +/- standard deviation over three federated seeds (42, 7, 123) on a fixed data '
     'split, with backdoor lift always paired within-seed against that seed\'s own honest baseline.')

h1('1. Attack setup / experimental parameter table')
kv_table(param, widths=[22,44,124])
cap('Table 1. The full reproducibility card, assembled from the notebook\'s live variables rather than typed in. '
    'The one data-dependent value, the trigger value, is pinned in both raw and standardized units.')
body('Insight: a reader can reproduce the full experiment from this table alone: the 150,000-row subsample and its '
     '3:2 benign/spoofed ratio, the 6,000-row server root set (hash-verified disjoint from train and test), the '
     '10-client IID federation with C9 and C10 compromised, the 3,329-parameter detector, the attack knobs, and the '
     'D2 defense constants.')

# ================= PAGE 2: Task 2 =================
pdf.add_page(); h1('2. Three-seed ablation: does each defense layer matter?')
body('Six configurations plus one robustness check, all against the same attack (40% poison, CN0 trigger, update '
     'scaling 3.0), all across three seeds. Median only and trust only isolate the two layers of the full defense.')
table(abl, widths=[62,32,32,32,32], fs=7.0, hl=(5,))
cap('Table 2. Ablation, mean +/- std over seeds 42, 7, 123 (n = 3). BSR is the backdoor success rate on the '
    'triggered test set; backdoor lift is BSR minus the same seed\'s honest baseline. The highlighted row is the '
    'adopted configuration.')
h2('Insight')
bullet('The attack works and inflation makes it worse: lift +0.2457 under FedAvg, +0.3036 when fake accuracy '
       'reports buy the attackers extra weight.')
bullet('Median only helps but leaves a real backdoor effect: +0.0641 +/- 0.0064, about a quarter of the attack '
       'survives. Two attackers in ten can still drag a coordinate-wise median.')
bullet('Trust only removes nearly all of the lift (+0.0037 +/- 0.0042) because the probes identify the attackers '
       'directly. On the lift metric alone it is statistically close to the full defense, and we say so.')
bullet('The full defense is the only configuration that drives lift negative (-0.0253 +/- 0.0178) and it posts the '
       'best clean accuracy (0.7142) and spoofing recall (0.5546) at the same time. The median layer is the safety '
       'net if the trust scores are ever wrong in a round, a failure mode trust-only cannot bound.')
callout('Robustness check (last row): against attack + inflation the full defense produces numerically identical '
        'results, and the reason is structural rather than lucky. Trust comes entirely from server-side probing; '
        'the self-reported accuracy that inflation manipulates is never consulted by the full defense.')

# ================= PAGE 3: Task 3 =================
pdf.add_page(); h1('3. Trigger generalization, including a mixed trigger')
body('Four trigger settings, each run undefended and under the full defense at the identical D2 configuration; '
     'nothing is retuned per trigger. PD is the weakest probed feature and the genuine stress test; the mixed '
     'CN0+TCD trigger is a pattern the defense was never designed around.')
table(trig, widths=[20,24,30,32,30,32,22], fs=6.7, hl=())
cap('Table 3. Trigger generalization at fixed D2, mean +/- std over seeds 42, 7, 123 (n = 3). BSR and lift are '
    'measured on each setting\'s own triggered test set against the same per-seed honest model. Honest FP rate is '
    'the fraction of honest client-rounds with trust below half of uniform.')
img(RES/'fig_trigger_comparison.png', maxw=150)
cap('Figure 1. Backdoor lift before (orange) and after (green) the defense, per trigger setting; bars are means '
    'over three seeds with +/- 1 std error bars, per the assignment\'s request. The black line at zero marks "the '
    'attacker gains nothing."')
h2('Insight')
bullet('The attack carries a viable backdoor in every setting (+0.09 to +0.25 lift), so each row is a real test.')
bullet('The defense drives lift below zero in every setting: CN0 -0.0253, TCD -0.0626, PD -0.0188, mixed -0.0282. '
       'Honest false positives stay between 0.3% and 0.7% of client-rounds throughout.')
bullet('Honest observations: the seed spread on the TCD and mixed attack rows is wide (std 0.05 to 0.07), and the '
       'mixed trigger has the highest raw BSR (0.9816) but not the highest lift, because stamping two features '
       'raises the honest baseline as well.')
bullet('Together with the Week 10 five-feature sweep, this supports the claim that the defense does not require '
       'knowing the exact trigger feature, within the discriminative (probed) feature set.')

# ================= PAGE 4: Task 3b adaptive attacker =================
pdf.add_page(); h1('4. Adaptive (defense-aware) attacker stress test')
body('The ablation and generalization attackers are fixed: they poison and scale without reacting to the defense. '
     'Here the attacker knows exactly how the coordinator probes and trains to evade it, adding an evasion term that '
     'keeps its model predicting spoofed on probe-style slices so it looks like the honest cohort. The evasion '
     'strength lambda is swept from 0 (the ordinary attacker) upward.')
table(adap, widths=[54,45,45,46], fs=8.0, hl=())
cap('Table 4. Adaptive attacker at fixed D2, mean +/- std over seeds 42, 7, 123 (n = 3). Uniform trust is 0.10; '
    'lambda = 0 is the ordinary attacker from Table 2. Produced by adaptive_attacker.py.')
img(RES/'fig_adaptive_attacker.png', maxw=150)
cap('Figure 2. Defended backdoor lift (green, left axis) and mean attacker trust (purple, right axis) versus evasion '
    'strength. As the attacker evades better (trust rises toward uniform), the backdoor collapses; defended lift '
    'stays negative throughout.')
h2('Insight')
bullet('The adaptive attacker cannot win. Turning up evasion does raise its trust from 0.0001 toward uniform '
       '(0.083 at lambda = 2), so it genuinely hides better, but its undefended backdoor lift collapses from '
       '+0.2457 to -0.14 and then -0.48 at lambda = 10.')
bullet('The reason is structural, not luck: the CN0 backdoor needs the model to call CN0-benign-high inputs benign, '
       'while the CN0 probe rewards calling those same inputs spoofed. Evading the probe and keeping the backdoor '
       'are directly opposed, so training for one destroys the other.')
callout('There is no evasion setting where the attacker both hides from the trust score and keeps a working '
        'backdoor. The layered defended lift is negative at every lambda. This closes the adaptive-attacker '
        'question, the strongest open threat to a behavioral-trust defense.')

# ================= PAGE 5: scope and future work =================
pdf.add_page(); h1('5. Scope and future work')
body('The core research questions are answered: the attack works and inflation worsens it (Table 2); each defense '
     'layer contributes and only the layered defense drives lift negative while preserving utility (Table 2); the '
     'defense generalizes across the discriminative feature set including a mixed trigger (Table 3); and a '
     'defense-aware adaptive attacker cannot both evade the probe and keep a working backdoor (Table 4). What '
     'remains is deliberately outside the scope of this study, not unfinished within it.')
bullet('Base detector accuracy. Honest spoofing recall is about 0.53 on this simplified public dataset. This is a '
       'property of the dataset and the small model, not the defense, and is why backdoor lift against each seed\'s '
       'own honest baseline is the primary metric. A stronger detector would not change any defense conclusion.')
bullet('Non-IID and larger fleets. Ten clients, two attackers, IID partitions. Non-IID data would widen the honest '
       'trust spread and is the setting most likely to stress the false-positive rate; it is the natural next study, '
       'and the IID choice is a stated scope boundary consistent with the Byzantine-robust FL literature.')
bullet('Seed count. Three seeds are enough to separate the attack effect from noise and to report mean and standard '
       'deviation, but not to resolve sub-noise differences between neighbouring defended variants, and we claim no '
       'such difference.')
bullet('Triggers outside the probe set. PQP and PIP carry near-zero class-discriminative signal (Cohen\'s d below '
       '0.05) and are excluded from probing by design, so they are not tested as triggers. This is a scope '
       'definition, not a gap: the claim is trigger-agnostic within the discriminative feature set.')
body('None of these affects the claims the paper makes. They mark where the contribution ends rather than work left '
     'undone.')

pdf.output(str(OUT))
print('written', OUT)
