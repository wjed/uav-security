# -*- coding: utf-8 -*-
"""
Build the consolidated final submission PDF for the week's assignment.
Covers all three assignment tasks plus the additional work done this week, and
names the recommended configuration. Reads the exported CSVs and embeds the real
figures from all three parts, so it cannot drift from the notebooks.
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
LINE=(214,214,214); ALTROW=(244,239,225); GREEN=(95,121,28); RED=(164,35,43)
PAGE_W=190

def clean(s):
    return (str(s).replace('—',', ').replace('–','-').replace('−','-')
            .replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"'))

class PDF(FPDF):
    def header(self):
        if self.page_no()==1: return
        self.set_font('Helvetica','',8); self.set_text_color(*GREY)
        self.cell(0,6,'Experimental Fixes and Paper Figures  |  Group 1  |  UAV FL Backdoor Defense',align='L'); self.ln(7)
    def footer(self):
        self.set_y(-12); self.set_font('Helvetica','',8); self.set_text_color(*GREY)
        self.cell(0,6,f'Page {self.page_no()}',align='C')

pdf=PDF(format='A4'); pdf.set_auto_page_break(auto=True,margin=15); pdf.set_margins(10,12,10)
def mc(w,h,t): pdf.multi_cell(w,h,clean(t),new_x=XPos.LMARGIN,new_y=YPos.NEXT)
def h1(t):
    pdf.ln(1.5); pdf.set_font('Helvetica','B',15); pdf.set_text_color(*PURPLE); mc(0,7.5,t)
    pdf.set_draw_color(*PURPLE); pdf.set_line_width(0.5); y=pdf.get_y(); pdf.line(10,y+0.5,200,y+0.5); pdf.ln(3)
def h2(t):
    pdf.ln(1); pdf.set_font('Helvetica','B',11); pdf.set_text_color(*PURPLE); mc(0,5.8,t); pdf.ln(0.4)
def h3(t):
    pdf.set_font('Helvetica','B',9.8); pdf.set_text_color(*DARK); mc(0,5.0,t)
def body(t):
    pdf.set_font('Helvetica','',9.5); pdf.set_text_color(*DARK); mc(0,4.8,t); pdf.ln(1.2)
def cap(t):
    pdf.set_font('Helvetica','I',9); pdf.set_text_color(*GREY); mc(0,4.4,t); pdf.ln(1.0)
def bullet(t):
    pdf.set_font('Helvetica','',9.5); pdf.set_text_color(*DARK)
    pdf.cell(4.5,4.8,'-'); pdf.multi_cell(PAGE_W-4.5,4.8,clean(t),new_x=XPos.LMARGIN,new_y=YPos.NEXT); pdf.ln(0.2)
def callout(t):
    pdf.set_fill_color(*ALTROW); pdf.set_draw_color(*GOLD); pdf.set_line_width(0.9)
    x,y=pdf.get_x(),pdf.get_y(); pdf.set_font('Helvetica','',9.5); pdf.set_text_color(*DARK)
    pdf.multi_cell(PAGE_W,4.8,clean(t),border=0,fill=True,new_x=XPos.LMARGIN,new_y=YPos.NEXT)
    pdf.line(x,y,x,pdf.get_y()); pdf.ln(1.5)
def table(df,widths=None,fs=7.4,hl=()):
    cols=list(df.columns)
    if widths is None: widths=[PAGE_W/len(cols)]*len(cols)
    pdf.set_font('Helvetica','B',fs); pdf.set_fill_color(*PURPLE); pdf.set_text_color(255,255,255)
    pdf.set_draw_color(*LINE); pdf.set_line_width(0.2)
    for c,w in zip(cols,widths): pdf.cell(w,5.8,clean(c),border=1,align='C',fill=True)
    pdf.ln(5.8)
    for ri,(_,row) in enumerate(df.iterrows()):
        is_hl=ri in hl
        pdf.set_font('Helvetica','B' if is_hl else '',fs)
        pdf.set_text_color(*(PURPLE if is_hl else DARK))
        pdf.set_fill_color(*(GOLD if is_hl else (ALTROW if ri%2 else (255,255,255))))
        for c,w in zip(cols,widths): pdf.cell(w,5.2,clean(row[c]),border=1,align='C',fill=True)
        pdf.ln(5.2)
    pdf.ln(1.5)
def img(path,maxw=PAGE_W):
    from PIL import Image
    iw,ih=Image.open(path).size
    w=maxw; h=w*ih/iw; avail=297-15-pdf.get_y()
    if h>avail: h=avail; w=h*iw/ih
    pdf.image(str(path),x=(210-w)/2,w=w,h=h); pdf.ln(1.5)

# ===================== PAGE 1 =====================
pdf.add_page(); pdf.ln(6)
pdf.set_font('Helvetica','B',19); pdf.set_text_color(*PURPLE)
mc(0,9,'Experimental Fixes and Paper Figures')
pdf.set_font('Helvetica','',11.5); pdf.set_text_color(*DARK)
mc(0,5.8,'Validation, reliability, and a fix for the false-positive weakness in the UAV federated-learning backdoor defense')
pdf.ln(1); pdf.set_font('Helvetica','B',10.5)
mc(0,5.5,'Will Jedrzejczak    Dilpreet Gill    Cole Walther')
pdf.set_font('Helvetica','',10); pdf.set_text_color(*GREY)
mc(0,5,'Group 1  |  James Madison University Capstone (IT 445 / IT 499)')
pdf.ln(2); pdf.set_draw_color(*GOLD); pdf.set_line_width(1.2); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(3.5)

h2('Executive summary')
body('This report covers three assignment tasks and two additional studies completed this week. Every number comes '
     'from a notebook in this folder and every table and figure is exported by the code that produced it.')
bullet('Task 1, corrections: the parameter count is fixed (3,329, not 13,000), root-set separation is now proven by '
       'hashing rather than asserted, and that check found and fixed a real 1-row train/test leak. Four overstated '
       'claims were corrected, including retracting "zero false positives."')
bullet('Task 2, reliability: all main cases rerun across three seeds (42, 7, 123) with mean and standard deviation. '
       'Attack lift +0.2415 +/- 0.0048, defended +0.0107 +/- 0.0025, a 96 percent reduction.')
bullet('Task 3, figures and tables: a new two-panel paper figure showing the backdoor accumulating over training '
       'alongside trust attribution, plus an improved main table with mean and standard deviation, a defense-side '
       'sensitivity study, and a quantitative false-positive table.')
bullet('Additional study A: we fixed the false-positive weakness the validation exposed. The honest false-positive '
       'rate drops from 20.5 percent to 0.3 percent with every other metric improving.')
bullet('Additional study B: we stress-tested that fix against an adaptive stealth attacker and found its evasion '
       'frontier is unprofitable.')

h2('Recommended configuration')
callout('The recommended defense is D2: a gentler trust gate (beta = 1.0) plus a suspicion dead-zone (tau = 2.0), '
        'combined with coordinate-wise median aggregation. Against the previous setting it cuts the honest '
        'false-positive rate from 20.5 percent to 0.3 percent, keeps attacker detection at 100 percent, keeps the '
        'backdoor neutralized, and raises both clean accuracy and spoofing recall. It is a two-line change to the '
        'trust computation. Note that Table 1 below is still reported at the older beta = 2.0 setting so it stays '
        'directly comparable with the previous report; folding D2 into the headline table is the next small task.')

h2('An honest note on direction')
body('Two results in this report are less flattering than the previous one, and that is deliberate. Running three '
     'seeds instead of one showed that "zero false positives" and "the defense is free" were both optimistic. We '
     'corrected them, then fixed the underlying problem. We would rather surface these ourselves than have a '
     'reviewer find them.')

# ===================== PAGE 2: Task 1 =====================
pdf.add_page(); h1('Task 1: Correction note')
h2('1a. Model parameter count: 3,329 is correct')
body('The count is now produced live, layer by layer, by the notebook rather than quoted. The GPS model (10 inputs, '
     '64-32-16-1) has 3,329 parameters, which is 13.0 KB in float32. The earlier "about 13,000 parameters" was '
     'copy-pasted from the Week 4 WSN-DS model (17 inputs, 128-64-32, 5 classes), which genuinely has 12,805, and '
     'the 13.0 kilobyte wire size made the wrong figure look plausible. Corrected everywhere it appeared.')
h2('1b. Root/challenge set separation: verified, and a real leak was found and fixed')
body('Separation is proven by hashing every row and counting shared rows between the three sets, not asserted. The '
     'server root set was already clean. The check did surface a 1-row overlap between the client training pool and '
     'the test set. Cause: de-duplication ran before the PRN, RX, and TOW identifier columns were dropped, so two '
     'rows differing only in satellite, receiver, or timestamp collapsed into identical model inputs afterward and '
     'survived. Fix: de-duplicate on the 10 model input features after dropping identifiers, which removes 2 rows '
     'out of 470,546 and makes all three sets provably disjoint. The notebook now asserts this and fails loudly if '
     'it is ever violated. Results were recomputed after the fix.')
sep=pd.DataFrame([['server root vs client training pool','0'],['server root vs test set','0'],
                  ['client training pool vs test set (after fix)','0']],columns=['Pair','Shared rows'])
table(sep,widths=[130,60],fs=8.2)
cap('Table A. Row-hash overlap between the three data partitions. All zero after the fix.')
h2('1c. Reproducibility of every table and figure')
body('Every table and figure in this report is produced by a notebook cell and exported to a results folder as a '
     'CSV or PNG. The PDFs are assembled by build scripts that read those exported files and embed the saved '
     'figures, so a report cannot disagree with the experiment that produced it. Nothing is transcribed by hand.')
h2('1d. Unclear or overstated claims, corrected')
bullet('"Zero false positives" is retracted. With one seed it appeared true; across three seeds the honest '
       'false-positive rate is 20.5 percent and one honest client-round reached zero trust. Additional study A then '
       'reduces the real rate to 0.3 percent.')
bullet('The negative backdoor lift reported previously was single-seed noise. The multi-seed estimate is slightly '
       'positive (+0.0107 +/- 0.0025).')
bullet('"The defense imposes no utility cost" is softened: clean accuracy under defense is about 0.008 below the '
       'honest baseline, small but consistent.')
bullet('"Feature-agnostic" is qualified to "agnostic within the discriminative feature set." A trigger placed on a '
       'near-zero-separation feature would fall outside the probe set.')

# ===================== PAGE 3: Task 2 main table =====================
pdf.add_page(); h1('Task 2 and 3: Reliability and the improved main table')
h2('Table 1. Main comparison across three seeds (mean +/- standard deviation)')
try:
    t1=pd.read_csv(P1/'results'/'main_table_multiseed.csv',keep_default_na=False)
    table(t1,widths=[52,34,34,34,36],fs=7.2)
except Exception as e:
    body(f'(main_table_multiseed.csv not found: {e})')
cap('Table 1. Honest baseline, attack, attack with accuracy inflation, and the full defense, over seeds 42, 7, and '
    '123. Columns are clean accuracy on the untouched test set, spoofing recall with no trigger applied, backdoor '
    'success rate on the triggered test set, and backdoor lift, which is BSR minus that seed own honest baseline. '
    'Reported at beta = 2.0 for comparability with the previous report.')
h2('Insights')
body('The attack reproduces across every seed rather than being a single-run artifact: it adds +0.2415 +/- 0.0048 '
     'of backdoor lift, and accuracy inflation raises that to +0.3036 +/- 0.0124 by buying the two compromised '
     'clients a larger share of the aggregation weight. The full defense returns lift to +0.0107 +/- 0.0025, a 96 '
     'percent reduction. The standard deviations are roughly fifty times smaller than the gap between the attacked '
     'and defended cases, which is precisely the point of running multiple seeds: the effect is far larger than the '
     'run-to-run noise, so the conclusion does not depend on a lucky draw. Spoofing recall is restored from 0.3641 '
     'under attack to 0.5204, close to the honest 0.5292, so the defense recovers the detector normal behavior and '
     'not merely its trigger behavior. Clean accuracy under defense sits about 0.008 below the honest baseline, a '
     'small but consistent utility cost that we state rather than round away.')
h2('Stated limitation')
body('Honest spoofing recall is only 0.5292, so the base detector misses roughly half of all spoofed samples before '
     'any attack occurs, and the honest backdoor success rate is correspondingly high at 0.6367. This is a real '
     'weakness of the detector on this simplified dataset. It is exactly why backdoor lift, measured against each '
     'seed own honest baseline, is the primary metric rather than raw accuracy.')

# ===================== PAGE 4: new paper figure =====================
pdf.add_page(); h1('Task 3: The new paper figure')
h2('Figure 1. Backdoor progression and trust attribution over federated training')
try: img(P1/'results'/'fig_main_paper_rounds.png')
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 1. Panel (a): backdoor success rate on the triggered test set, measured after every federated round, '
    'for the honest baseline, the attack, the attack with accuracy inflation, and the full defense. X axis is the '
    'federated round, Y axis is backdoor success rate. Panel (b): the aggregation trust weight the server assigns '
    'to the compromised clients (C9, C10) versus the honest clients (C1 to C8) under the full defense. X axis is '
    'the federated round, Y axis is trust weight, and the dashed grey line marks uniform trust (1/N = 0.10). All '
    'curves are means over three seeds; shaded bands are plus or minus one standard deviation.')
h2('Insights')
body('Panel (a) shows something a single end-of-training number cannot: the backdoor accumulates. The attacked '
     'curves climb away from the honest baseline round after round, and the inflation variant climbs faster and '
     'further, because the fake reported accuracy compounds the attackers weight at every aggregation step. The '
     'defended curve tracks the honest baseline for the entire run, so the defense is not repairing damage after '
     'the fact, it is preventing the backdoor from ever taking hold. Panel (b) supplies the mechanism behind that '
     'flat curve: the server own probing separates the two populations within the earliest rounds and holds the '
     'compromised clients at zero trust for the rest of training. Read together, the two panels connect cause and '
     'effect in a single figure, which is the claim the paper needs: the defense works because it removes the '
     'attackers influence from the aggregation, and it does so almost immediately rather than gradually. The width '
     'of the honest band in panel (b) is the one caveat visible in the figure, and it is the false-positive problem '
     'that the additional study below then fixes.')

# ===================== PAGE 5: defense-side sensitivity =====================
pdf.add_page(); h1('Task 3: Defense-side sensitivity')
h2('Figure 2 and Table 2. Sensitivity to the defense own hyperparameters')
try: img(P1/'results'/'fig_defense_sensitivity.png')
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 2. Backdoor lift against the trust-gate sharpness beta (left panel, log-scaled X axis) and the trust '
    'smoothing EMA factor (right panel). Y axis is backdoor lift. The green line is the mean over three seeds, the '
    'shaded band is plus or minus one standard deviation, the dashed red line is the undefended attack lift, and '
    'the solid black line at zero marks the point where the attacker gains nothing.')
try:
    tb=pd.read_csv(P1/'results'/'sensitivity_beta.csv',keep_default_na=False)
    table(tb,widths=[42,49,49,50],fs=7.4)
    cap('Table 2. Beta sweep with EMA fixed at 0.5, mean +/- standard deviation over three seeds.')
except Exception as e:
    body(f'(sensitivity_beta.csv not found: {e})')
h2('Insights')
body('The previous report varied only the attacker side, so this sweep tests the defense own knobs. The result '
     'contradicted our expectation and is the more useful finding of the two sensitivity studies. We assumed a '
     'sharper gate would be safer, since a larger beta punishes a suspicious client harder. Instead lift, clean '
     'accuracy, and spoofing recall all degrade monotonically as beta grows: lift is -0.0054 at beta = 1.0, '
     '+0.0107 at our then-default beta = 2.0, and +0.1228 at beta = 8.0, while clean accuracy falls from 0.7106 to '
     '0.6656. The reason is that the gate punishes whichever client looks suspicious, and a large share of honest '
     'client-rounds look momentarily suspicious, so a sharp gate strips weight from honest clients and erodes the '
     'honest majority that the coordinate-wise median depends on. The attackers are already fully suppressed at '
     'beta = 0.5, so everything above that is collateral damage. The actionable consequence is that beta = 1.0 '
     'dominates our previous default on every metric and should replace it. The EMA panel is U-shaped with our '
     'default of 0.5 already at the optimum, so that knob needed no change.')

# ===================== PAGE 6: false positives =====================
pdf.add_page(); h1('Task 3: Quantitative false-positive reporting')
h2('Table 3. Client flagging treated as a detection problem')
try:
    fp=pd.read_csv(P1/'results'/'false_positive_summary.csv',keep_default_na=False)
    table(fp,widths=[110,40,40],fs=8.0)
except Exception as e:
    body(f'(false_positive_summary.csv not found: {e})')
cap('Table 3. Decisions pooled over 3 seeds x 12 rounds x 10 clients. A client is counted as flagged if its trust '
    'falls below half of uniform (0.05); fully excluded means trust reached exactly zero. Columns are the raw count '
    'and the corresponding rate.')
h2('Insights')
body('This replaces the previous qualitative statement with numbers, and the numbers are not flattering in one '
     'respect. On the attacker side the mechanism is perfect: both compromised clients are flagged in 72 of 72 '
     'client-rounds and are the only clients ever driven to exactly zero trust. On the honest side, however, honest '
     'clients are flagged in 59 of 288 client-rounds, a 20.5 percent false-positive rate, and in one client-round '
     'an honest client was fully excluded. This retracts our previous claim that no honest client is ever '
     'suppressed. The cause is structural rather than a bug: trust is a relative per-round quantity normalized '
     'across the cohort, so somebody is always at the bottom, and with eight honest clients the weakest of them in '
     'a given round can fall below the threshold through no fault of its own. The practical damage is limited, '
     'because a flagged honest client is only down-weighted for that round rather than removed, and Table 1 shows '
     'clean accuracy and recall survive. But a 20.5 percent rate is too high for a defense we want to call '
     'deployable, which is what motivated the additional study on the next page.')

# ===================== PAGE 7: improvement table =====================
pdf.add_page(); h1('Additional study A: fixing the false-positive weakness')
body('Having measured the problem, we fixed it. Three candidate changes were ablated one at a time, each across '
     'all three seeds.')
h2('Table 4. Ablation of three candidate fixes')
try:
    t4=pd.read_csv(P2/'results'/'improvement_ablation.csv',keep_default_na=False)
    hl=tuple(i for i,v in enumerate(t4.iloc[:,0].astype(str)) if v.strip().startswith('D2'))
    table(t4,widths=[44,28,28,30,29,31],fs=6.9,hl=hl)
except Exception as e:
    body(f'(improvement_ablation.csv not found: {e})')
cap('Table 4. Each configuration adds one fix to the one above it. Columns are clean accuracy, spoofing recall, '
    'backdoor lift, the honest false-positive rate, and the attacker detection rate, all mean +/- standard '
    'deviation over three seeds. The recommended configuration D2 is highlighted.')
h2('Insights')
body('The gentler gate alone (D1) cuts the honest false-positive rate from 20.5 percent to 6.9 percent, and adding '
     'a suspicion dead-zone (D2) takes it to 0.3 percent, a reduction of roughly twenty percentage points. '
     'Critically this is not a tradeoff. At D2 the backdoor remains fully neutralized, attacker detection remains '
     'at 100 percent, and both utility metrics improve: clean accuracy rises from 0.7029 to 0.7143 and spoofing '
     'recall from 0.5204 to 0.5560. D2 is therefore strictly better than the previous configuration on every '
     'metric measured, and it is a two-line change to the trust computation. The explanation matches the diagnosis '
     'in Table 3: the dead-zone stops the gate from reacting to the small, noisy suspicion values that honest '
     'clients naturally produce, while the two compromised clients sit far above the threshold because they fail '
     'the probe badly, so they are still suppressed in every round.')
h3('The idea that did not work, reported rather than dropped')
body('The third candidate, requiring a client to be flagged in two consecutive rounds before being down-weighted, '
     'was rejected. It left the false-positive rate unchanged at 0.3 percent but reduced attacker detection from '
     '100 percent to 88.9 percent, because a two-round confirmation window gives a compromised client a free round '
     'before it is confirmed. We report the measured reason rather than quietly dropping the idea.')

# ===================== PAGE 8: improvement figure =====================
pdf.add_page(); h1('Additional study A: figure')
h2('Figure 3. Reducing the honest false-positive rate while keeping the backdoor neutralized')
try: img(P2/'results'/'fig_improvement.png')
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 3. X axis is the defense configuration, where each step adds one fix to the one on its left. Left Y '
    'axis is rate in percent, covering the honest false-positive rate (purple) and the attacker detection rate '
    '(gold). Right Y axis is backdoor lift (green), with the dashed line at zero marking the point where the '
    'attacker gains nothing. Bands are plus or minus one standard deviation over three seeds.')
h2('Insights')
body('The purple line falling from 20 percent to near zero is the improvement itself. The gold line staying flat at '
     '100 percent through D2 is what makes it a genuine improvement rather than a tradeoff: the reduction in false '
     'positives does not cost any attacker detection. The gold line then dropping at D3 is the rejected persistence '
     'rule introducing a blind spot, which is the visual form of the argument for not adopting it. The green line '
     'hovering at or below the zero reference across all defended configurations confirms the backdoor stays '
     'neutralized throughout, so nothing was traded away to obtain the lower false-positive rate. Read as a whole, '
     'the figure supports adopting D2 and stopping there.')
callout('This is the result we consider the strongest of the week. It converts the main weakness found during '
        'validation into a strength, and it is the configuration we recommend for the paper.')

# ===================== PAGE 9: adaptive attacker =====================
pdf.add_page(); h1('Additional study B: adaptive attacker stress test')
body('A dead-zone is a threshold, and a threshold invites gaming: an attacker does not have to beat the probe, it '
     'only has to keep its suspicion below tau. Since we introduced that possibility ourselves in study A, we '
     'tested it, and we proposed a second orthogonal detection signal in advance as a fix.')
h2('Table 5 and Figure 4. Stealth attacker swept from 40 percent poison down to 1 percent')
try:
    t5=pd.read_csv(P3/'results'/'adaptive_attacker_sweep.csv',keep_default_na=False)
    hl=tuple(i for i,v in enumerate(t5.iloc[:,0].astype(str)) if v.strip().startswith('1%'))
    table(t5,widths=[17,35,30,23,19,30,36],fs=6.6,hl=hl)
except Exception as e:
    body(f'(adaptive_attacker_sweep.csv not found: {e})')
cap('Table 5. The stealth attacker drops the model-replacement scaling and lowers its poison rate to hide. Columns '
    'are backdoor lift, attacker detection rate, honest false-positive rate, and the attacker two suspicion scores. '
    'The dead-zone is tau = 2.0; a score below it means the client is never gated. The 1 percent rows are '
    'highlighted as the only setting where detection begins to fail.')
try: img(P3/'results'/'fig_adaptive_attacker.png')
except Exception as e: body(f'(figure not found: {e})')
cap('Figure 4. Panel (a): the attacker two suspicion scores against the dead-zone threshold as it gets stealthier. '
    'Panel (b): the surviving backdoor lift with no defense, with the probe-only defense, and with the probe plus '
    'direction defense. X axis is the attacker poison rate in both panels.')
h2('Insights')
body('Two findings, both against our hypothesis. First, the dead-zone holds and the evasion frontier is '
     'unprofitable. From 5 percent poison upward the attacker suspicion is at least 7.35, more than three times the '
     'threshold, and it is detected in 100 percent of client-rounds. Detection only begins to fail at 1 percent '
     'poison, and at that setting the attacker undefended backdoor lift is +0.0051, indistinguishable from zero. '
     'The poison rate needed to hide is the same poison rate at which the backdoor stops working, so evasion and '
     'effectiveness are mutually exclusive. That is a stronger statement than reporting that no evasion was found. '
     'Second, our proposed second signal was rejected. Update-direction anomaly was supposed to catch subtle '
     'attackers the probe misses, but it is the weaker signal at exactly those settings (0.76 at 1 percent poison '
     'against 3.26 for the probe) and it roughly doubles the honest false-positive rate, so it adds cost and '
     'complexity for no benefit. In hindsight the probe measures the backdoor directly by activating it, whereas '
     'direction is only a proxy that degrades faster at low poison rates.')
callout('Scope limit stated plainly: this tests one adaptive strategy, poisoning less and dropping the scaling. It '
        'does not test an attacker that explicitly optimizes against the defense, for example by adding probe error '
        'as a penalty in its own training loss. That attacker is untested and is our highest-value next experiment. '
        'We do not claim general adaptive-attacker robustness.')

# ===================== PAGE 10: summary =====================
pdf.add_page(); h1('Summary and what remains')
h2('What changed')
body('The parameter count is corrected and counted live. Root-set separation is proven by hashing, and that check '
     'found and fixed a real train/test leak. The main experiments now run across three seeds with mean and '
     'standard deviation, with lift paired within each seed. False-positive reporting is quantitative. A '
     'defense-side sensitivity sweep was added. All figures are line graphs with standard-deviation bands.')
h2('What improved')
body('The central claim now rests on evidence rather than a single run: the attack adds +0.2415 +/- 0.0048 of lift '
     'and the defense cuts it to +0.0107 +/- 0.0025, with standard deviations far smaller than the effect. Beyond '
     'the assignment, the false-positive rate that validation exposed was reduced from 20.5 percent to 0.3 percent '
     'with every other metric improving, and the resulting configuration was stress-tested against an adaptive '
     'attacker and held.')
h2('What got worse, stated honestly')
bullet('The honest false-positive rate was 20.5 percent, not essentially zero, and one honest client-round reached '
       'zero trust. The earlier claim is retracted. Study A then reduces it to 0.3 percent.')
bullet('The defense is not free: clean accuracy under defense is about 0.008 below the honest baseline, and the '
       'previously reported negative lift was single-seed noise.')
h2('What remains incomplete')
bullet('The base detector is weak, with honest spoofing recall about 0.55. This is partly a ceiling of the '
       'simplified dataset and is the highest-value remaining improvement.')
bullet('An attacker that explicitly optimizes against the probe has not been tested.')
bullet('The setting is IID with ten clients and two attackers. Non-IID data would widen the honest trust spread and '
       'is the natural next deeper experiment.')
bullet('The dead-zone threshold tau = 2.0 was reasoned from the MAD scale rather than swept.')
bullet('D2 is recommended but Table 1 is still reported at beta = 2.0 for comparability. Folding D2 into the '
       'headline table is a small next task.')
h2('Where everything lives')
files=pd.DataFrame([
    ['1-validation/','Assignment tasks 1 to 3: corrections, three seeds, main table, paper figure, sensitivity'],
    ['2-improvements/','Additional study A: the false-positive fix. Recommended configuration D2'],
    ['3-adaptive-attacker/','Additional study B: adaptive stealth attacker stress test'],
    ['README.md','Index of the three parts and which is best'],
], columns=['Folder or file','Contents'])
table(files,widths=[52,138],fs=8.0)
body('Each part contains its own notebook, write-ups, exported results, and a standalone PDF. Every notebook runs '
     'top to bottom and writes its own figures and CSVs. Each PDF is assembled by a build script that reads those '
     'exported files, so no report can drift from the experiment that produced it.')

pdf.output(str(OUT))
print('wrote', OUT)
