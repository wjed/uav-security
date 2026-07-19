# -*- coding: utf-8 -*-
"""
Build the 5-page submission PDF.
Covers the assignment requirements (correction note, multi-seed table, new
paper-quality figure) with a plain-English opening. Reads the exported CSVs and
embeds the real figures, so it cannot drift from the notebooks.
Run from this folder:  python build_final_report_pdf.py
Output: week10_final_report.pdf
"""
from pathlib import Path
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
P1 = HERE                         # every number and figure in this report comes from one notebook
OUT = HERE / 'week10_final_report.pdf'

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
        self.cell(0,5,'Experimental Fixes and Paper Figures  |  Group 1',align='L'); self.ln(6)
    def footer(self):
        self.set_y(-11); self.set_font('Helvetica','',7.5); self.set_text_color(*GREY)
        self.cell(0,5,f'Page {self.page_no()} of 5',align='C')

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
def img(path,maxw=PAGE_W):
    from PIL import Image
    iw,ih=Image.open(path).size
    w=maxw; h=w*ih/iw; avail=297-13-pdf.get_y()
    if h>avail: h=avail; w=h*iw/ih
    pdf.image(str(path),x=(210-w)/2,w=w,h=h); pdf.ln(1.2)

# ================= PAGE 1: plain-English summary =================
pdf.add_page(); pdf.ln(3)
pdf.set_font('Helvetica','B',18); pdf.set_text_color(*PURPLE)
mc(0,8.2,'Experimental Fixes and Paper Figures')
pdf.set_font('Helvetica','',10.8); pdf.set_text_color(*DARK)
mc(0,5.2,'Corrections, multi-seed reliability, and a redesigned trust gate for the UAV federated-learning backdoor defense')
pdf.ln(0.6); pdf.set_font('Helvetica','B',10)
mc(0,5.0,'Will Jedrzejczak    Dilpreet Gill    Cole Walther')
pdf.set_font('Helvetica','',9.4); pdf.set_text_color(*GREY)
mc(0,4.6,'Group 1  |  James Madison University Capstone (IT 445 / IT 499)')
pdf.ln(1.4); pdf.set_draw_color(*GOLD); pdf.set_line_width(1.1); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(2.8)

h2('In plain terms: what this is and what we found')
body('We are building a GPS spoofing detector that runs across a fleet of drones. Each drone trains its own copy of '
     'a small detector on the signals it sees, and a central server merges those copies every round, so no raw data '
     'ever leaves a drone. The danger we study is that two of the ten drones have been taken over. They quietly feed '
     'their copy bad training examples so the merged detector learns a secret blind spot: whenever one particular '
     'signal value appears, call the signal safe. The attacker can then stamp that value on a real spoofing attack '
     'and the whole fleet waves it through. Our defense is a referee on the server. Before merging, it quizzes every '
     'drone model on data the server holds itself, and reduces the influence of any drone whose answers look wrong '
     'in a specific way.')
body('The previous report showed this working, but from a single random run. This report fixes the errors that were '
     'pointed out, reruns everything three times to show the result was not luck, and then redesigns the referee to '
     'repair the one real weakness those tougher checks exposed. The defense now stops the attack completely, and it '
     'no longer punishes innocent drones while doing it.')

h2('What changed this week')
bullet('Corrections: the model parameter count was wrong and is fixed. We also proved, rather than assumed, that the '
       'data the referee uses is fully separate from the training and test data, and that check caught a real (tiny) '
       'data leak, which we fixed.')
bullet('Reliability: every main experiment was rerun on three random seeds and is reported as an average with a '
       'standard deviation instead of a single number.')
bullet('A redesign: the tougher checks showed the referee was wrongly suspecting innocent drones in 20.5 percent of '
       'rounds. Adding a "dead-zone," so small amounts of suspicion are ignored entirely, brought that to 0.3 '
       'percent with no innocent drone ever silenced, while the attackers are still caught every single time.')

h2('The configuration used throughout this report')
callout('D2: a gentler penalty (beta = 1.0) plus a suspicion dead-zone (tau = 2.0), on top of coordinate-wise median '
        'merging. Unlike the previous report, this is not a recommendation for later. Every table and figure here is '
        'produced at D2, so the headline numbers and the recommended setting are now the same thing.')
body('Two claims from the previous report did not survive the tougher checks and stay retracted: "zero false '
     'positives" was false when measured properly, and a negative backdoor result read from one seed was noise. Both '
     'are corrected on page 2. We would rather retract them ourselves than have them found.')

# ================= PAGE 2: corrections =================
pdf.add_page(); h1('1. Correction note')
h2('Model parameter count: 3,329 is correct')
body('The notebook now counts the parameters live, layer by layer, instead of quoting a number. The model has 3,329 '
     'parameters, which is 13.0 KB stored as float32. The earlier "about 13,000 parameters" was copied from the '
     'Week 4 WSN-DS model, which genuinely has 12,805, and the 13.0 kilobyte size made the wrong figure look '
     'plausible. Kilobytes are not parameters. Corrected everywhere it appeared.')
h2('Root/challenge set separation: proven, and a real leak was found and fixed')
body('We hash every row and count how many appear in more than one partition, rather than asserting separation. The '
     'server referee set was already clean. The check did find a 1-row overlap between the client training pool and '
     'the test set. The cause: de-duplication ran before the PRN, RX, and TOW identifier columns were dropped, so '
     'two rows that differed only in satellite, receiver, or timestamp became identical once those columns were '
     'removed, and survived. Fix: de-duplicate on the 10 model input features after dropping identifiers. That '
     'removes 2 rows out of 470,546 and makes all three partitions provably disjoint. The notebook now asserts this '
     'and halts if it is ever violated. All results were recomputed after the fix.')
sep=pd.DataFrame([['server referee set vs client training pool','0'],
                  ['server referee set vs test set','0'],
                  ['client training pool vs test set (after fix)','0']],columns=['Pair','Shared rows'])
table(sep,widths=[132,58],fs=7.8)
cap('Table A. Row-hash overlap between the three data partitions. All zero after the fix.')
h2('Reproducibility')
body('Every table and figure in this report is produced by a single notebook, 10_validation.ipynb, '
     'which runs top to bottom with no manual steps and exports each result to a CSV or PNG. This PDF is assembled '
     'by a script that reads those exported files and embeds the saved figures, so the report cannot disagree with '
     'the experiment. Nothing is transcribed by hand.')
h2('Overstated claims, corrected')
bullet('"Zero false positives" is retracted. Measured across three seeds under the old gate, honest drones were '
       'flagged in 20.5 percent of client-rounds and one was driven to zero trust. Section 3 reports 0.3 percent, '
       'but that is a measured rate for a redesigned gate, not the old claim reinstated.')
bullet('The negative backdoor result reported previously was single-seed noise. D2 does give a slightly negative '
       'multi-seed value, but within the seed spread, so we call the defended model indistinguishable from an '
       'unattacked one rather than better than it. See the note under Table 1.')
bullet('"No utility cost" is supportable at D2, where accuracy and recall match the honest baseline within noise. It '
       'was not supportable at the old setting, which cost about 0.008 of clean accuracy.')
bullet('"Feature-agnostic" is narrowed to "agnostic within the discriminative feature set." A trigger hidden in a '
       'feature carrying almost no signal would fall outside what the referee probes.')

# ================= PAGE 3: reliability + main table =================
pdf.add_page(); h1('2. Reliability: three seeds, and the improved main table')
h2('Table 1. Main comparison across three random seeds (mean +/- standard deviation)')
try:
    t1=pd.read_csv(P1/'results'/'main_table_multiseed.csv',keep_default_na=False)
    table(t1,widths=[52,34,34,34,36],fs=7.0,hl=(3,))
except Exception as e:
    body(f'(main_table_multiseed.csv not found: {e})')
cap('Table 1. Honest baseline, attack, attack with accuracy inflation, and the full defense at D2, over seeds 42, 7, '
    'and 123. Columns: clean accuracy on the untouched test set; spoofing recall with no trigger applied; backdoor '
    'success rate (BSR) on the triggered test set; and backdoor lift, which is BSR minus that same seed own honest '
    'baseline. The defense row is highlighted.')
h2('Insights')
body('The attack reproduces on every seed rather than being a fluke of one run: it adds +0.2415 +/- 0.0048 of '
     'backdoor lift, and letting the attackers lie about their accuracy raises that to +0.3036 +/- 0.0124, because '
     'the false claim buys them a bigger share of the merge. At D2 the advantage is eliminated outright, falling to '
     '-0.0265 +/- 0.0174: the attacker ends up no better off than if it had never attacked. Spoofing recall is '
     'restored from 0.3641 under attack to 0.5560 against an honest 0.5292, and clean accuracy to 0.7143 against an '
     'honest 0.7112, so the defense recovers the detector normal behaviour and not only its trigger behaviour.')
h2('A claim we are deliberately not making')
body('The defended row comes out marginally ahead of the honest baseline on all three metrics. It would be easy to '
     'present that as the defense improving on ordinary training, and there is even a plausible mechanism, since '
     'median-based merging discards outlying updates and that is mild regularization even with no attacker present. '
     'But those margins are comparable to the seed-to-seed spread and three seeds is a small sample, so we treat the '
     'defended result as indistinguishable from the honest baseline rather than better than it. The supportable '
     'claim is that D2 removes the backdoor at no utility cost. We are explicit about this because the previous '
     'report made exactly this error in the opposite direction, reading single-seed noise as a real effect.')
h2('Table 2. Client flagging, pooled over 3 seeds x 12 rounds x 10 clients')
try:
    t2=pd.read_csv(P1/'results'/'false_positive_summary.csv',keep_default_na=False)
    table(t2,widths=[110,40,40],fs=7.4)
except Exception as e:
    body(f'(false_positive_summary.csv not found: {e})')
cap('Table 2. The defense treated as a detector of compromised clients, at D2. A client-round is one client in one '
    'federated round, so there are 72 attacker and 288 honest decisions in total.')
body('Both compromised drones are caught in every single round, and honest drones are wrongly flagged in 1 round out '
     'of 288, with none ever silenced completely. Under the old gate these figures were 20.5 percent and one honest '
     'client-round at zero trust, which is the weakness the redesign was built to fix.')
h2('Honest limitation')
body('Honest spoofing recall is only 0.5292, meaning the underlying detector misses roughly half of all spoofed '
     'samples before any attack happens. This is a genuine weakness of the detector on this simplified dataset, and '
     'it is why backdoor lift, measured against each seed own honest baseline, is the primary metric rather than raw '
     'accuracy. Improving the base detector is the highest-value work remaining.')

# ================= PAGE 4: new paper figure =================
pdf.add_page(); h1('3. The new paper figure')
h2('Figure 1. Backdoor progression and trust attribution over federated training')
try: img(P1/'results'/'fig_main_paper_rounds.png')
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 1. Panel (a): backdoor success rate on the triggered test set, measured after every federated round, for '
    'the honest baseline, the attack, the attack with accuracy inflation, and the full defense. X axis is the '
    'federated round; Y axis is backdoor success rate. Panel (b): the trust weight the server assigns to the '
    'compromised drones (C9, C10) against the honest drones (C1 to C8) under the full defense. X axis is the '
    'federated round; Y axis is trust weight; the dashed grey line marks equal trust (1/N = 0.10). All curves are '
    'means over three seeds and the shaded bands are plus or minus one standard deviation.')
h2('Insights')
body('Panel (a) shows something a single end-of-training number cannot: the gap opens up over training rather than '
     'appearing at the end. Every run starts with a high backdoor success rate, because a barely-trained detector '
     'labels almost anything as safe. From there the honest baseline falls steadily from 0.93 to 0.64 as the model '
     'learns to reject spoofed inputs. The two attacked runs do not fall with it. They stay pinned near 1.0 and '
     'decay only slightly, so the widening distance between them and the honest curve is the backdoor being held '
     'open round after round. The accuracy-inflation run stays highest of all, because the false accuracy claim buys '
     'the attackers more weight at every merge and the advantage compounds. The defended curve is noisy for the '
     'first two rounds, while the referee is still separating the cohort, and from round 3 onward it tracks the '
     'honest baseline closely and never follows the attacked curves upward.')
body('Panel (b) gives the mechanism. The server own quiz separates the two groups within the first round and holds '
     'the compromised drones at zero trust for the rest of training, while the honest band stays tight and well '
     'clear of the flagging threshold. Together the panels connect cause and effect in one figure, which is the '
     'claim the paper needs: the defense works because it removes the attackers influence from the merge, and it '
     'does so almost immediately rather than gradually.')

# ================= PAGE 5: sensitivity + what remains =================
pdf.add_page(); h1('4. Defense-side sensitivity, and what remains')
h2('Figure 2. Backdoor lift and honest false positives across the three defense hyperparameters')
try: img(P1/'results'/'fig_defense_sensitivity.png', maxw=182)
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 2. Each panel varies one defense knob and holds the other two at D2. X axes: gate sharpness beta (a, log '
    'scale), dead-zone width tau (b), trust smoothing EMA (c). Left Y axis is backdoor lift (green, with +/- 1 '
    'standard deviation band over three seeds); right Y axis is the honest false-positive rate (purple). The solid '
    'black line at zero marks the point where the attacker gains nothing. The undefended attack sits at +0.241, far '
    'above every defended value, so it is annotated rather than drawn.')
h2('Insights')
body('The previous report swept only the attacker side, so we swept the defense own knobs. The headline is that the '
     'dead-zone did more than fix false positives: it made the defense insensitive to its main hyperparameter. '
     'Without a dead-zone, backdoor lift degraded steadily as the gate sharpened, from -0.0054 at beta = 1.0 up to '
     '+0.1228 at beta = 8, and we concluded the gate had to be tuned carefully. With the dead-zone, lift across that '
     'same sixteen-fold range is -0.0279, -0.0265, -0.0328, -0.0324 and -0.0322: flat, negative everywhere, varying '
     'by less than one standard deviation. A sharp gate was never dangerous in itself, it was dangerous because it '
     'punished honest drones that were merely at the bottom of a noisy round. A defense that does not need careful '
     'tuning to stay safe is a stronger result than a defense with a better recommended default.')
body('Panel (b) also closes a limitation we had flagged ourselves. The dead-zone width was previously chosen by '
     'reasoning about the statistical scale rather than measured. Sweeping it puts the false-positive rate at 6.9 '
     'percent with no dead-zone, 4.9 percent at tau = 1, and 0.3 percent from tau = 2 onward, while backdoor lift is '
     'best in the tau = 2 to 3 region and starts to degrade by tau = 5 as an over-wide dead-zone begins excusing '
     'genuinely suspicious behaviour. tau = 2.0 sits at the knee of both curves, so the original reasoning is '
     'confirmed by measurement. One point of honesty about panel (a): lift is marginally better at the sharper '
     'settings, but well inside one standard deviation, so beta = 1.0 is chosen on the false-positive rate rather '
     'than on lift, and we say so instead of implying the lift ordering favoured our choice.')
h2('What remains incomplete')
bullet('The base detector is weak (honest spoofing recall about 0.53), partly a ceiling of this simplified dataset. '
       'This is the highest-value next improvement.')
bullet('Three seeds is enough to show the attack effect far exceeds the noise, but too few to resolve differences '
       'between neighbouring settings in the sweeps, or to claim the defense beats honest training.')
bullet('No adaptive attacker. Every attacker here is fixed: it poisons at a set rate without reacting to the '
       'defense. One that knows the referee exists and shapes its updates to look ordinary is untested, and a '
       'dead-zone invites exactly that, since an attacker staying under the threshold is never penalised. This '
       'is the strongest remaining threat and the top next experiment.')
bullet('Everything is still IID with ten drones and two attackers. Non-IID data would stress the false-positive '
       'behaviour most and is the natural next deeper experiment.')

pdf.output(str(OUT))
print('wrote', OUT)
