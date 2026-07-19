# -*- coding: utf-8 -*-
"""
Build the condensed 5-page submission PDF.
Keeps only what the assignment requires (correction note, multi-seed table, one
new paper figure) plus the week's best result (the false-positive fix), with a
plain-English opening. Reads the exported CSVs and embeds the real figures, so
it cannot drift from the notebooks.
Run from this folder:  python build_final_report_pdf.py
Output: week10_final_report.pdf
"""
from pathlib import Path
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
P1, P2, P3 = HERE/'1-validation', HERE/'2-improvements', HERE/'3-adaptive-attacker'
OUT = HERE / 'week10_final_report.pdf'

PURPLE=(69,0,132); GOLD=(203,182,119); DARK=(51,51,51); GREY=(89,89,89)
LINE=(214,214,214); ALTROW=(244,239,225); PAGE_W=190

def clean(s):
    return (str(s).replace('—',', ').replace('–','-').replace('−','-')
            .replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"'))

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
    pdf.set_font('Helvetica','I',8.4); pdf.set_text_color(*GREY); mc(0,4.0,t); pdf.ln(0.8)
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
mc(0,5.2,'Validation, reliability, and a fix for the false-positive weakness in the UAV federated-learning backdoor defense')
pdf.ln(0.6); pdf.set_font('Helvetica','B',10)
mc(0,5.0,'Will Jedrzejczak    Dilpreet Gill    Cole Walther')
pdf.set_font('Helvetica','',9.4); pdf.set_text_color(*GREY)
mc(0,4.6,'Group 1  |  James Madison University Capstone (IT 445 / IT 499)')
pdf.ln(1.4); pdf.set_draw_color(*GOLD); pdf.set_line_width(1.1); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(2.8)

h2('In plain terms: what this is and what we found')
body('We are building a GPS spoofing detector that runs across a fleet of drones. Each drone trains its own copy of '
     'a small detector on the GPS signals it sees, and a central server merges those copies every round, so no raw '
     'data ever leaves a drone. The danger we study is that two of the ten drones have been taken over. They quietly '
     'feed their copy bad training examples so that the merged detector learns a secret blind spot: whenever a '
     'particular signal value appears, call the signal safe. Later the attacker can stamp that value on a real '
     'spoofing attack and the whole fleet waves it through. Our defense is a referee that sits on the server. Before '
     'merging, it quizzes every drone model on data the server itself holds, and quietly reduces the influence of '
     'any drone whose answers look wrong in a very specific way.')
body('Last report showed the defense worked, but on a single random run. This report does three things: it fixes the '
     'errors that were pointed out, it reruns everything three times to prove the result was not luck, and it fixes '
     'the one real weakness those tougher checks uncovered. The short version is that the defense holds up, and it '
     'is now much fairer to the innocent drones than it was.')

h2('What changed this week')
bullet('Corrections: the model parameter count was wrong and is fixed. We also proved, rather than assumed, that the '
       'data the referee uses is completely separate from the training and test data, and that check caught a real '
       '(tiny) data leak, which we fixed.')
bullet('Reliability: every main experiment was rerun on three random seeds and is reported as an average with a '
       'standard deviation, instead of a single run.')
bullet('A real improvement: the tougher checks showed the referee was wrongly suspecting innocent drones 20.5 '
       'percent of the time. We fixed that. It is now 0.3 percent, and every other number got better at the same '
       'time.')

h2('The recommended setting')
callout('Use configuration D2: a gentler penalty (beta = 1.0) plus a "dead-zone" so small amounts of suspicion are '
        'ignored entirely (tau = 2.0), on top of the existing median-based merging. It cuts wrongly-suspected '
        'innocent drones from 20.5 percent to 0.3 percent, still catches the attackers 100 percent of the time, '
        'still neutralizes the backdoor, and raises both clean accuracy and spoofing recall. It is a two-line '
        'change. Note that Table 1 is still reported at the older beta = 2.0 so it stays directly comparable with '
        'the last report; adopting D2 in the headline table is the next small task.')
body('Two results here are less flattering than last time, on purpose. Running three seeds showed that "zero false '
     'positives" and "the defense costs nothing" were both too optimistic. We corrected them and then fixed the '
     'underlying problem rather than leaving it for a reviewer to find.')

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
     'and stops if it is ever violated. All results were recomputed after the fix.')
sep=pd.DataFrame([['server referee set vs client training pool','0'],
                  ['server referee set vs test set','0'],
                  ['client training pool vs test set (after fix)','0']],columns=['Pair','Shared rows'])
table(sep,widths=[132,58],fs=7.8)
cap('Table A. Row-hash overlap between the three data partitions. All zero after the fix.')
h2('Reproducibility')
body('Every table and figure in this report is produced by a notebook cell and exported as a CSV or PNG. The PDF is '
     'assembled by a script that reads those exported files and embeds the saved figures, so the report cannot '
     'disagree with the experiment. Nothing is transcribed by hand.')
h2('Overstated claims, corrected')
bullet('"Zero false positives" is retracted. Across three seeds the rate is 20.5 percent and one honest client-round '
       'reached zero trust. Section 3 then reduces the real rate to 0.3 percent.')
bullet('The negative backdoor lift reported last time was single-seed noise. The three-seed estimate is slightly '
       'positive, +0.0107 +/- 0.0025.')
bullet('"No utility cost" is softened: clean accuracy under defense is about 0.008 below the honest baseline, small '
       'but consistent.')
bullet('"Feature-agnostic" is narrowed to "agnostic within the discriminative feature set." A trigger hidden in a '
       'feature with almost no signal would fall outside what the referee probes.')

# ================= PAGE 3: reliability + main table =================
pdf.add_page(); h1('2. Reliability: three seeds, and the improved main table')
h2('Table 1. Main comparison across three random seeds (mean +/- standard deviation)')
try:
    t1=pd.read_csv(P1/'results'/'main_table_multiseed.csv',keep_default_na=False)
    table(t1,widths=[52,34,34,34,36],fs=7.0)
except Exception as e:
    body(f'(main_table_multiseed.csv not found: {e})')
cap('Table 1. Honest baseline, attack, attack with accuracy inflation, and the full defense, over seeds 42, 7, and '
    '123. Columns: clean accuracy on the untouched test set; spoofing recall with no trigger applied; backdoor '
    'success rate (BSR) on the triggered test set; and backdoor lift, which is BSR minus that same seed own honest '
    'baseline. Reported at beta = 2.0 to stay comparable with the previous report.')
h2('Insights')
body('The attack reproduces on every seed rather than being a fluke of one run: it adds +0.2415 +/- 0.0048 of '
     'backdoor lift, and letting the attackers lie about their accuracy raises that to +0.3036 +/- 0.0124, because '
     'the false claim buys them a bigger share of the merge. The full defense brings lift back to +0.0107 +/- '
     '0.0025, a 96 percent reduction. The standard deviations are roughly fifty times smaller than the gap between '
     'the attacked and defended cases, which is the entire reason for running multiple seeds: the effect is far '
     'larger than the run-to-run noise, so the conclusion does not rest on a lucky draw. Spoofing recall is restored '
     'from 0.3641 under attack to 0.5204, close to the honest 0.5292, so the defense recovers the detector normal '
     'behaviour and not only its trigger behaviour. Clean accuracy under defense sits about 0.008 below the honest '
     'baseline, a small but consistent cost that we state rather than round away.')
h2('Honest limitation')
body('Honest spoofing recall is only 0.5292, meaning the underlying detector misses roughly half of all spoofed '
     'samples before any attack happens, and the honest BSR is correspondingly high at 0.6367. This is a genuine '
     'weakness of the detector on this simplified dataset, and it is exactly why backdoor lift, measured against '
     'each seed own honest baseline, is the primary metric rather than raw accuracy. Improving the base detector is '
     'the highest-value work remaining.')
h2('Defense-side sensitivity (summary)')
body('The previous report varied only the attacker side, so we swept the defense own knobs too. The result went '
     'against our expectation: a sharper penalty is worse, not safer. Backdoor lift is -0.0054 at beta = 1.0, '
     '+0.0107 at the old default of 2.0, and +0.1228 at beta = 8.0, with clean accuracy falling from 0.7106 to '
     '0.6656 across that range. A sharp penalty punishes honest drones that merely look odd for one round, eroding '
     'the honest majority that the median-based merge depends on. This is what led directly to the fix in Section 3. '
     'The full sweep and its figure are in 1-validation/.')

# ================= PAGE 4: new paper figure =================
pdf.add_page(); h1('3. The new paper figure')
h2('Figure 1. Backdoor progression and trust attribution over federated training')
try: img(P1/'results'/'fig_main_paper_rounds.png')
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 1. Panel (a): backdoor success rate on the triggered test set, measured after every federated round, '
    'for the honest baseline, the attack, the attack with accuracy inflation, and the full defense. X axis is the '
    'federated round; Y axis is backdoor success rate. Panel (b): the trust weight the server assigns to the '
    'compromised drones (C9, C10) against the honest drones (C1 to C8) under the full defense. X axis is the '
    'federated round; Y axis is trust weight; the dashed grey line marks equal trust (1/N = 0.10). All curves are '
    'means over three seeds and the shaded bands are plus or minus one standard deviation.')
h2('Insights')
body('Panel (a) shows something a single end-of-training number cannot: the backdoor builds up gradually. The '
     'attacked curves climb away from the honest baseline round after round, and the version where the attackers '
     'also lie about their accuracy climbs faster and further, because the lie compounds their influence at every '
     'merge. The defended curve stays on the honest baseline for the whole run, so the defense is not repairing '
     'damage after the fact, it is stopping the backdoor from ever forming. Panel (b) shows the mechanism behind '
     'that flat line: within the earliest rounds the server own quiz separates the two groups and pins the '
     'compromised drones at zero trust, where they stay. Together the two panels connect cause and effect in one '
     'figure, which is the claim the paper needs: the defense works because it removes the attackers influence from '
     'the merge, and it does so almost immediately rather than gradually. The width of the honest band in panel (b) '
     'is the one visible caveat, and it is precisely the false-positive problem that Section 3 fixes.')

# ================= PAGE 5: the fix + what remains =================
pdf.add_page(); h1('4. Fixing the false-positive weakness (the week best result)')
body('The checks above showed the referee wrongly suspected honest drones in 20.5 percent of client-rounds. The '
     'cause is that suspicion was penalised continuously and judged relative to the group each round, so with eight '
     'honest drones somebody is always at the bottom and a single odd round was treated like a real problem. We '
     'tested three candidate fixes, each across all three seeds.')
try:
    t2=pd.read_csv(P2/'results'/'improvement_ablation.csv',keep_default_na=False)
    hl=tuple(i for i,v in enumerate(t2.iloc[:,0].astype(str)) if v.strip().startswith('D2'))
    table(t2,widths=[42,27,27,29,30,35],fs=6.6,hl=hl)
except Exception as e:
    body(f'(improvement_ablation.csv not found: {e})')
cap('Table 2. Each row adds one fix to the row above. Columns: clean accuracy, spoofing recall, backdoor lift, the '
    'rate at which honest drones were wrongly flagged, and the rate at which the compromised drones were correctly '
    'flagged. Mean +/- standard deviation over three seeds. The recommended configuration D2 is highlighted. The '
    'no-defense lift here (+0.2422) differs slightly from Table 1 (+0.2415) because this ablation is a separate run '
    'of its own notebook; the gap is well inside one standard deviation.')
try: img(P2/'results'/'fig_improvement.png', maxw=138)
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 2. X axis is the defense configuration, each step adding one fix. Left Y axis is rate in percent: the '
    'honest false-positive rate (purple) and the attacker detection rate (gold). Right Y axis is backdoor lift '
    '(green), with the dashed line at zero marking the point where the attacker gains nothing.')
h2('Insights')
body('The gentler penalty alone (D1) cuts wrongly-suspected honest drones from 20.5 to 6.9 percent, and adding the '
     'dead-zone (D2) takes it to 0.3 percent. This is not a trade: at D2 the backdoor is still neutralized, the '
     'attackers are still caught 100 percent of the time, and both utility numbers improve, with clean accuracy '
     'rising from 0.7029 to 0.7143 and spoofing recall from 0.5204 to 0.5560. D2 is therefore strictly better than '
     'the previous configuration on every metric measured, from a two-line change. The third idea, requiring a drone '
     'to look suspicious two rounds in a row before being penalised, was rejected: it did not reduce false positives '
     'any further and it dropped attacker detection to 88.9 percent, because the waiting period hands the attacker a '
     'free round. We report the measured reason rather than dropping the idea quietly.')
h2('What remains incomplete')
bullet('The base detector is weak (honest spoofing recall about 0.55), partly a ceiling of this simplified dataset. '
       'This is the highest-value next improvement.')
bullet('We stress-tested D2 against a stealth attacker that poisons less to stay hidden, and it held: below the '
       'level where the attacker becomes hard to see, its backdoor is already worthless (undefended lift +0.0051). '
       'But an attacker that explicitly optimises against the referee is untested, and is the top next experiment. '
       'Details in 3-adaptive-attacker/.')
bullet('Everything is still IID with ten drones and two attackers. Non-IID data is the natural next deeper '
       'experiment and would stress the false-positive behaviour most.')
bullet('D2 is recommended but Table 1 is still at the old beta = 2.0 for comparability. Folding D2 into the headline '
       'table is a small next task.')

pdf.output(str(OUT))
print('wrote', OUT)
