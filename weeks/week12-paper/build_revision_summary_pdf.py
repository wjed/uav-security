# -*- coding: utf-8 -*-
"""
Build the revision summary PDF: what changed in the results because of the
July 28 review, and why.

Reads the exported CSVs so the numbers cannot drift from the experiments that
produced them. Reuses the house style from the Week 10 and Week 11 report
builders. Run from this folder:

    python build_revision_summary_pdf.py

Output: week12_revision_summary.pdf
"""
from pathlib import Path
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
OUT = HERE / 'week12_revision_summary.pdf'

PURPLE = (69, 0, 132); GOLD = (203, 182, 119); DARK = (51, 51, 51)
GREY = (89, 89, 89); LINE = (214, 214, 214); ALTROW = (244, 239, 225)
RED = (164, 35, 43); GREEN = (95, 121, 28)
PAGE_W = 190


def clean(s):
    return (str(s).replace('—', ', ').replace('–', '-')
            .replace('−', '-').replace('’', "'").replace('‘', "'")
            .replace('“', '"').replace('”', '"')
            .replace('α', 'alpha').replace('±', '+/-')
            .replace('→', '->'))


def num(s):
    """'0.2415 +/- 0.0048' -> '+0.2415' style single value."""
    return str(s).split('+/-')[0].strip()


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', '', 7.5); self.set_text_color(*GREY)
        self.cell(0, 5, 'What the July 28 Review Changed  |  Group 1  |  '
                        'Trigger-Agnostic Behavioral Trust', align='L')
        self.ln(6)

    def footer(self):
        self.set_y(-11); self.set_font('Helvetica', '', 7.5)
        self.set_text_color(*GREY)
        self.cell(0, 5, f'Page {self.page_no()}', align='C')


pdf = PDF(format='A4')
pdf.set_auto_page_break(auto=True, margin=13)
pdf.set_margins(10, 11, 10)
pdf.add_page()


def mc(w, h, t):
    pdf.multi_cell(w, h, clean(t), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def h1(t):
    pdf.ln(0.8); pdf.set_font('Helvetica', 'B', 13.5); pdf.set_text_color(*PURPLE)
    mc(0, 6.6, t)
    pdf.set_draw_color(*PURPLE); pdf.set_line_width(0.45)
    y = pdf.get_y(); pdf.line(10, y + 0.4, 200, y + 0.4); pdf.ln(2.4)


def h2(t, col=PURPLE):
    pdf.ln(0.6); pdf.set_font('Helvetica', 'B', 10.2); pdf.set_text_color(*col)
    mc(0, 5.0, t); pdf.ln(0.2)


def body(t):
    pdf.set_font('Helvetica', '', 9.1); pdf.set_text_color(*DARK)
    mc(0, 4.35, t); pdf.ln(0.9)


def cap(t):
    pdf.set_font('Helvetica', 'I', 8.3); pdf.set_text_color(*GREY)
    mc(0, 3.95, t); pdf.ln(0.8)


def bullet(t):
    pdf.set_font('Helvetica', '', 9.1); pdf.set_text_color(*DARK)
    pdf.cell(4.2, 4.35, '-')
    pdf.multi_cell(PAGE_W - 4.2, 4.35, clean(t),
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(0.15)


def callout(t, edge=GOLD):
    pdf.set_fill_color(*ALTROW); pdf.set_draw_color(*edge); pdf.set_line_width(0.9)
    x, y = pdf.get_x(), pdf.get_y()
    pdf.set_font('Helvetica', '', 9.1); pdf.set_text_color(*DARK)
    pdf.multi_cell(PAGE_W, 4.35, clean(t), border=0, fill=True,
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.line(x, y, x, pdf.get_y()); pdf.ln(1.2)


def table(df, widths=None, fs=7.0, hl=(), align='C'):
    cols = list(df.columns)
    if widths is None:
        widths = [PAGE_W / len(cols)] * len(cols)
    if pdf.get_y() + 5.3 + 4.9 * (len(df) + 1) > 297 - 15:
        pdf.add_page()
    pdf.set_font('Helvetica', 'B', fs); pdf.set_fill_color(*PURPLE)
    pdf.set_text_color(255, 255, 255)
    pdf.set_draw_color(*LINE); pdf.set_line_width(0.2)
    for c, w in zip(cols, widths):
        pdf.cell(w, 5.3, clean(c), border=1, align='C', fill=True)
    pdf.ln(5.3)
    for ri, (_, row) in enumerate(df.iterrows()):
        is_hl = ri in hl
        pdf.set_font('Helvetica', 'B' if is_hl else '', fs)
        pdf.set_text_color(*(PURPLE if is_hl else DARK))
        pdf.set_fill_color(*(GOLD if is_hl else (ALTROW if ri % 2 else (255, 255, 255))))
        for ci, (c, w) in enumerate(zip(cols, widths)):
            pdf.cell(w, 4.9, clean(row[c]), border=1,
                     align='L' if ci == 0 and align == 'L' else 'C', fill=True)
        pdf.ln(4.9)
    pdf.ln(1.0)


# ===================================================================== page 1
pdf.set_font('Helvetica', 'B', 17); pdf.set_text_color(*PURPLE)
mc(0, 8.0, 'What the July 28 Review Changed')
pdf.set_font('Helvetica', '', 10.5); pdf.set_text_color(*DARK)
mc(0, 5.2, 'Trigger-Agnostic Behavioral Trust for Backdoor-Resilient '
           'Federated GPS Spoofing Detection')
pdf.set_font('Helvetica', '', 9.1); pdf.set_text_color(*GREY)
mc(0, 4.6, 'Group 1: Will Jedrzejczak, Cole Walther, Dilpreet Gill   |   '
           'IT 445 Capstone, Summer 2026   |   Advisor: Dr. Khalid Hasan')
pdf.ln(2.5)

callout('The short version: the review asked for five things we had not done. Doing them changed '
        'the paper more than any previous week. Two claims we had published turned out to be wrong, '
        'and the experiment the review called "the single most valuable" found a real failure in our '
        'defense that we had never tested for. The defense is narrower than we thought, and the '
        'evidence behind it is much stronger.')

h1('1. What we were asked to do')
body('The review listed seven comments. Five required new experiments; two required rewriting '
     'claims. We addressed all seven. The experiments are all driven by one shared harness so '
     'they cannot disagree with each other, and a single command reproduces every table.')
table(pd.DataFrame([
    {'#': '1, 5', 'What was asked': 'Compare against published defenses, not only our own ablations',
     'What it cost us': 'Found a baseline that ties us'},
    {'#': '2', 'What was asked': 'Test uneven (non-IID) client data',
     'What it cost us': 'Found our defense fails there'},
    {'#': '3', 'What was asked': 'Stop claiming both defense layers are necessary',
     'What it cost us': 'Claim withdrawn'},
    {'#': '4', 'What was asked': 'Separate "removed the attack" from "detector is reliable"',
     'What it cost us': 'A wrong explanation corrected'},
    {'#': '6', 'What was asked': 'Recompute the overhead on a realistic denominator',
     'What it cost us': 'Number was 3x too low'},
    {'#': '7', 'What was asked': 'Soften four specific overclaims',
     'What it cost us': 'Applied verbatim'},
]), widths=[14, 108, 68], fs=7.6, align='L')

h1('2. The two things we had published that were wrong')

h2('2.1 We blamed the dataset for our weak detector. It was our own setup.', RED)
body('We had written that the detector catching only 53% of spoofed signals was "largely a ceiling '
     'of this public dataset". The review pushed on it, so we tested it: we trained several models '
     'centrally on the same features, with no federation and no attack, which upper-bounds what the '
     'federated system could reach.')
c = pd.read_csv(RES / 'detector_ceiling.csv').set_index('Model')
# ordered worst to best, with the federated detector last so the gap is the
# last thing read rather than buried mid-table
keep = ['Logistic regression', 'MLP 64-32-16 (paper model)', 'Random forest (400 trees)',
        'Hist gradient boosting', 'Federated honest FedAvg (paper baseline)']
cc = c.loc[keep, ['Spoofing Recall', 'F1', 'Triggered BSR']].reset_index()
table(cc.rename(columns={'Spoofing Recall': 'Spoofing recall', 'Triggered BSR': 'Attack success'}),
      widths=[86, 36, 32, 36], fs=7.6, hl=(4,), align='L')
cap('Every row except the last is trained centrally on the full data pool. The last row is the '
    'federated detector used throughout the paper.')
body('The same architecture we use reaches 0.907 recall when trained centrally, and gradient '
     'boosting reaches 0.993, against 0.529 federated. The features are separable. Our federated '
     'configuration, twelve rounds of three local epochs on a small network, simply underfits. '
     'This was our explanation being wrong, not a small correction, and the paper now says so.')

h2('2.2 Our overhead figure used the wrong denominator.', RED)
o = pd.read_csv(RES / 'overhead_analysis.csv')
body('We reported 1.1% server-side overhead. That divided the added server time by the sum of every '
     'drone\'s training time, which is what a simulation does. Real drones train at the same time, '
     'so a round takes about as long as the slowest one. On that denominator the same measurement '
     'is 3.40%.')
table(o.rename(columns={'Server overhead (ms/round)': 'Server ms/round',
                        'Overhead vs sequential': '% of sequential',
                        'Overhead vs parallel': '% of parallel'})[
      ['Defense', 'Server ms/round', '% of sequential', '% of parallel']],
      widths=[76, 38, 38, 38], fs=7.6, hl=(0,), align='L')
body('We also had to withdraw the claim that the defense stays practical as the fleet grows. Server '
     'cost rises with the number of drones while a parallel round does not, so the overhead fraction '
     'climbs from 5.6% at five drones to 34.9% at forty. We only ever tested ten.')

# ===================================================================== page 2
pdf.add_page()
h1('3. The biggest finding: the defense does not survive uneven data')
body('The review called this "probably the single most valuable additional experiment", and it was '
     'right. Every result we had ever produced assumed each drone sees a similar mix of signals. A '
     'real fleet does not. When we tested drones holding different proportions of spoofed data, our '
     'trust mechanism stopped working.')

n = pd.read_csv(RES / 'noniid_dirichlet.csv')


def pick(cond, meth, col):
    r = n[(n['Condition'] == cond) & (n['Method'] == meth)]
    return num(r.iloc[0][col]) if len(r) else '---'


CONDS = [('IID', 'Evenly split'), ('Ratio skew a=10 (mild)', 'Mild skew'),
         ('Ratio skew a=3 (moderate)', 'Moderate skew')]
rows = []
for key, lab in [('Attacker Trust', 'Trust given to compromised drones (fair share 0.100)'),
                 ('Attacker Detect', 'Compromised drones caught'),
                 ('Honest False-Flag', 'Honest drones wrongly flagged')]:
    rows.append({'Measure': lab,
                 **{lab2: pick(c, 'Trust + median (ours)', key) for c, lab2 in CONDS}})
rows.append({'Measure': 'Backdoor lift, trust layer alone',
             **{lab2: pick(c, 'Behavioral trust (ours)', 'Backdoor Lift') for c, lab2 in CONDS}})
rows.append({'Measure': 'Backdoor lift, full defense',
             **{lab2: pick(c, 'Trust + median (ours)', 'Backdoor Lift') for c, lab2 in CONDS}})
rows.append({'Measure': 'Backdoor lift, no defense at all',
             **{lab2: pick(c, 'FedAvg', 'Backdoor Lift') for c, lab2 in CONDS}})
table(pd.DataFrame(rows), widths=[92, 32, 32, 34], fs=7.6, hl=(3,), align='L')
cap('Mean over three seeds. Lift of zero means the attacker gained nothing; the trust layer alone '
    'under skew is statistically indistinguishable from having no defense. Read the false-flag row '
    'with care: the 0.0% under moderate skew is not an improvement. The gate has stopped firing at '
    'all, so it flags nobody, attacker or honest drone alike.')

h2('Why it happens')
body('The coordinator scores each drone by how far its answer falls below what the fleet typically '
     'answers, measured in units of how much the fleet normally disagrees. When every drone sees '
     'similar data the fleet agrees closely, so a backdoored drone\'s odd answer stands out by a '
     'wide margin. When drones legitimately hold different data they disagree more, that margin '
     'widens, and the attacker\'s odd answer no longer stands out. It hides inside the fleet\'s own '
     'variation.')
body('We tested whether this is just a badly set threshold by lowering it. Detection partly '
     'recovers, from 8% to 39% under mild skew, which confirms the mechanism, but it never returns '
     'to the 100% we get on even data and it starts flagging honest drones instead. So the problem '
     'is the way suspicion is scaled, not the threshold value.')

callout('This is the result we least wanted and the one we are most glad we ran. Our headline claim '
        'is now scoped to fleets with roughly even data, and the clearest next step is a suspicion '
        'measure computed per drone rather than against the whole fleet.', RED)

h1('4. What the comparison against other methods showed')
b = pd.read_csv(RES / 'baseline_comparison.csv')
body('We implemented every defense the review named and ran them on the identical data, attack, '
     'seeds and metrics. Nothing here is quoted from another paper.')
bb = b[['Method', 'Spoofing Recall', 'Backdoor Lift', 'Server ms/round']].copy()
for col in ('Spoofing Recall', 'Backdoor Lift', 'Server ms/round'):
    bb[col] = bb[col].map(num)
table(bb.rename(columns={'Spoofing Recall': 'Spoofing caught',
                         'Backdoor Lift': 'Backdoor lift',
                         'Server ms/round': 'Server ms'}),
      widths=[86, 36, 36, 32], fs=7.2, hl=(6, 9), align='L')
cap('Highlighted: Multi-Krum, an existing method, and our full defense. Lower lift is better.')

body('Multi-Krum, a standard existing method, reaches +0.0061 against our +0.0039. At three seeds '
     'those are indistinguishable, and it is 27 times cheaper on server time. We report this in the '
     'paper rather than omit it, and we removed our earlier claim that a behavioral probe is '
     'necessary to stop this attack.')

h2('What still distinguishes our method')
bullet('Multi-Krum, trimmed mean and Krum must be told how many drones are compromised. A real '
       'coordinator does not know that. When we set them to expect two and actually compromise '
       'four, Multi-Krum degrades to +0.2837 and trimmed mean to +0.2992, close to no defense at '
       'all, while ours holds at +0.0114. Ours has no such setting.')
bullet('Those methods produce a selection, not a per-drone judgment, so they cannot report which '
       'aircraft is compromised. Ours names them, at 100% detection and a 0.3% false-alarm rate on '
       'even data.')

# ===================================================================== page 3
pdf.add_page()
h1('5. The claim we withdrew, and what replaced it')
body('We had claimed both defense layers were necessary. The review pointed out that our own '
     'numbers do not support it: the trust layer alone reaches +0.0039 and the full defense '
     '-0.0265, and at three seeds that gap is inside the run-to-run spread. We withdrew the claim.')
body('The review then asked for the right experiment: degrade the trust score until it is '
     'imperfect, and see whether the median layer limits the damage. We ran seven such conditions.')
m = pd.read_csv(RES / 'median_necessity.csv')
mm = m[['Condition', 'Trust-only Lift', 'Full (trust+median) Lift',
        'Median benefit (trust-only minus full)']].copy()
for col in mm.columns[1:]:
    mm[col] = mm[col].map(num)
mm = mm.rename(columns={'Trust-only Lift': 'Trust only', 'Full (trust+median) Lift': 'Full defense',
                        'Median benefit (trust-only minus full)': 'Median helped by'})
extra = pd.DataFrame([
    {'Condition': 'Uneven data, mild skew', 'Trust only': '+0.2374',
     'Full defense': '+0.0647', 'Median helped by': '+0.1727'},
    {'Condition': 'Uneven data, moderate skew', 'Trust only': '+0.2482',
     'Full defense': '+0.1002', 'Median helped by': '+0.1480'},
])
mm = pd.concat([mm[~mm['Condition'].str.contains('non-IID', case=False)], extra],
               ignore_index=True)
table(mm, widths=[76, 38, 38, 38], fs=7.4, hl=(len(mm) - 2, len(mm) - 1), align='L')
cap('The last two rows are the uneven-data conditions from section 3, where the trust layer fails '
    'outright.')
body('Under mild degradation the median layer contributes between +0.017 and +0.033, which is the '
     'same size as our seed spread, so we do not claim it as proven there. Where it clearly earns '
     'its place is under uneven data: it removes +0.173 and +0.148 of the attack, roughly ten times '
     'more than on even data. So the honest statement is the one the review suggested: the trust '
     'layer does most of the work, and the median is a backstop for when it fails.')
body('One condition did not do what we intended, and we report it as such. Making the attack '
     'stronger by scaling its update up to ten times instead of three actually weakens it: the '
     'undefended lift falls to -0.5888, because an update scaled that hard destroys the shared '
     'model rather than steering it. The attack is already near its most effective setting.')

h1('6. The numbers that moved')
body('All results are now produced by one harness rather than several notebooks, so the headline '
     'table shifted slightly. The conclusions are unchanged; only the last decimals moved.')
table(pd.DataFrame([
    {'Quantity': 'Attack, backdoor lift', 'Before': '+0.2457', 'After': '+0.2415'},
    {'Quantity': 'Attack plus lying, backdoor lift', 'Before': '+0.3036', 'After': '+0.3036'},
    {'Quantity': 'Full defense, backdoor lift', 'Before': '-0.0253', 'After': '-0.0265'},
    {'Quantity': 'Full defense, spoofing caught', 'Before': '0.5546', 'After': '0.5560'},
    {'Quantity': 'Server overhead per round', 'Before': '37.4 ms', 'After': '34.0 ms'},
    {'Quantity': 'Overhead as a share of a round', 'Before': '1.1%', 'After': '3.40%'},
]), widths=[100, 45, 45], fs=7.6, hl=(5,), align='L')

h1('7. Where this leaves the project')
h2('Stronger than before', GREEN)
bullet('Nine aggregation rules compared on one pipeline, including every baseline the review named.')
bullet('Every number traceable to an exported CSV, and one command reproduces all of them.')
bullet('The full operating point reported, not just accuracy: precision, recall, F1, balanced '
       'accuracy, false-alarm rate and confusion counts.')
bullet('We found our own most important weakness before a reviewer did.')

h2('Honestly weaker than we thought', RED)
bullet('The headline result is scoped to fleets with roughly even data. On uneven data, which is '
       'the realistic case, the trust layer stops firing.')
bullet('An existing method, Multi-Krum, matches us on even data at a fraction of the cost. Our '
       'advantage rests on not needing to know the attacker count, and on naming the culprits.')
bullet('The detector itself is weak, and that is our federated configuration rather than the data.')

h2('The three things worth doing next')
bullet('Compute suspicion per drone instead of against the whole fleet. This is the direct fix for '
       'the uneven-data failure and we already have the harness to test it.')
bullet('Train the federated detector properly. Thirty rounds with a larger network reaches 0.851 '
       'recall against our 0.529, most of the way to the centralised ceiling.')
bullet('Test on a second, independent signal domain. Everything here is one dataset.')

pdf.output(str(OUT))
print(f'wrote {OUT}')
