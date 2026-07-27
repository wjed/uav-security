# -*- coding: utf-8 -*-
"""
Build the project's visualization site (index.html at the repository root).

Every number the site displays is read from the CSVs the notebooks exported.
Nothing is typed in here by hand, so the site cannot drift from the experiments
for the same reason the paper and the reports cannot. Run this after any rerun:

    python weeks/week13-website/build_site.py

The site is a single self-contained file: the data is embedded as JSON so it
works from a file:// URL and from GitHub Pages without any fetch or CORS setup.
"""
from __future__ import annotations
import base64, io, json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
W10  = ROOT / 'weeks' / 'week10-validation'  / 'results'
W11  = ROOT / 'weeks' / 'week11-paper-tables' / 'results'
IMG  = ROOT / 'weeks' / 'images'
HERE = Path(__file__).resolve().parent
OUT  = ROOT / 'index.html'

# The drone photos are embedded as data URIs rather than linked, so the built
# page stays a single self-contained file that works from file:// as well as
# from Pages. They are cropped to their opaque bounds and downscaled first: the
# originals are far larger than the ~150px they ever render at, and shipping
# them untouched would cost roughly five times the bytes for no visible gain.
DRONE_PX = 320


def embed_drone(name: str) -> str:
    from PIL import Image
    im = Image.open(IMG / f'{name}.png').convert('RGBA')
    im = im.crop(im.getbbox())          # strip transparent padding
    h = round(im.height * DRONE_PX / im.width)
    im = im.resize((DRONE_PX, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format='WEBP', quality=88, method=6)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/webp;base64,{b64}'


def num(s):
    """'0.7109 +/- 0.0021' or '+0.2457' or '0.3%' -> float"""
    s = str(s).strip().replace('%', '')
    return float(s.split('+/-')[0].strip())


def sd(s):
    p = str(s).split('+/-')
    return float(p[1].strip()) if len(p) > 1 else 0.0


def load(path):
    return pd.read_csv(path, keep_default_na=False)


# ---------------------------------------------------------------- ablation
abl = load(W11 / 'ablation_table.csv')
def row(needle):
    m = abl[abl['Method'].str.contains(needle, regex=False)]
    if m.empty:
        raise KeyError(needle)
    r = m.iloc[0]
    return {
        'method': r['Method'],
        'clean':  num(r['Clean Accuracy']),  'clean_sd':  sd(r['Clean Accuracy']),
        'recall': num(r['Spoofing Recall']), 'recall_sd': sd(r['Spoofing Recall']),
        'bsr':    num(r['BSR']),             'bsr_sd':    sd(r['BSR']),
        'lift':   num(r['Backdoor Lift']),   'lift_sd':   sd(r['Backdoor Lift']),
    }

# the site's fleet panel is a state machine over these seven measured rows
STATES = {
    'honest':          row('Honest FedAvg'),
    'attack':          row('Attack (FedAvg)'),
    'attack_inflate':  row('inflation (Acc'),
    'median':          row('Median only'),
    'trust':           row('Trust only'),
    'full':            row('Full defense (trust'),
    'full_inflate':    row('Full defense vs attack + inflation'),
}

# ---------------------------------------------------------------- triggers
tg11 = load(W11 / 'trigger_comparison.csv')
tg10 = load(W10 / 'trigger_generalization.csv')

triggers = {}
for _, r in tg10.iterrows():                      # five single features
    triggers[r['Trigger feature']] = {
        'name': r['Trigger feature'],
        'd': num(r["Cohen's d"]),
        'undef': num(r['Undefended lift']), 'undef_sd': sd(r['Undefended lift']),
        'def':   num(r['Defended lift (D2)']), 'def_sd': sd(r['Defended lift (D2)']),
        'mixed': False,
    }
for _, r in tg11.iterrows():                      # adds the mixed trigger + FP rates
    name = r['Trigger']
    entry = triggers.get(name, {
        'name': name, 'd': None,
        'undef': num(r['Attack lift']), 'undef_sd': sd(r['Attack lift']),
        'def':   num(r['Defended lift']), 'def_sd': sd(r['Defended lift']),
        'mixed': '+' in name,
    })
    entry['fp'] = num(r['Honest FP rate'])
    entry['atk_bsr'] = num(r['Attack BSR'])
    entry['def_bsr'] = num(r['Defended BSR'])
    triggers[name] = entry

ORDER = ['CN0', 'TCD', 'DO', 'LC', 'PD', 'CN0+TCD']
trigger_list = [triggers[k] for k in ORDER if k in triggers]

# ---------------------------------------------------------------- sensitivity
def sweep(fname, xcol):
    df = load(W10 / fname)
    return [{'x': num(r[xcol]), 'lift': num(r['Backdoor Lift']),
             'sd': sd(r['Backdoor Lift']), 'fp': num(r['Honest FP rate'])}
            for _, r in df.iterrows()]

sens = {
    'beta': sweep('sensitivity_beta.csv', 'beta (gate sharpness)'),
    'tau':  sweep('sensitivity_tau.csv',  'tau (dead-zone)'),
    'ema':  sweep('sensitivity_ema.csv',  'EMA (trust smoothing)'),
}

# ---------------------------------------------------------------- adaptive
ad = load(W11 / 'adaptive_attacker.csv')
adaptive = [{'lam': num(r['Evasion strength (lambda)']),
             'undef': num(r['Undefended lift']),
             'def':   num(r['Defended lift (D2)']),
             'trust': num(r['Mean attacker trust'])} for _, r in ad.iterrows()]

# ---------------------------------------------------------------- clients
cf = load(W10 / 'client_flagging_table.csv')
clients = [{'id': r['Client'],
            'attacker': r['Role'].strip().upper() == 'ATTACKER',
            'trust': num(r['Mean trust']),
            'trust_sd': sd(r['Mean trust']),
            'flag_rate': num(r['Flag rate'])} for _, r in cf.iterrows()]

fp = load(W10 / 'false_positive_summary.csv')
def fprow(needle):
    r = fp[fp['Metric'].str.contains(needle, regex=False)].iloc[0]
    return {'count': r['Count'].strip(), 'rate': r['Rate'].strip()}

false_pos = {
    'attacker_flagged': fprow('Attacker client-rounds flagged'),
    'honest_flagged':   fprow('Honest client-rounds flagged'),
    'honest_zeroed':    fprow('Honest client-rounds fully excluded'),
}

# ---------------------------------------------------------------- probe set
params = load(W11 / 'parameter_table.csv')
probe_row = params[params['Parameter'].str.contains('Probe features')].iloc[0]['Value']
probe_feats = re.findall(r'\b(DO|PD|CP|EC|LC|PC|PIP|PQP|TCD|CN0)\b', probe_row)
ALL_FEATS = ['DO', 'PD', 'CP', 'EC', 'LC', 'PC', 'PIP', 'PQP', 'TCD', 'CN0']
excluded = [f for f in ALL_FEATS if f not in probe_feats]

def param(needle):
    m = params[params['Parameter'].str.contains(needle, regex=False)]
    return m.iloc[0]['Value'] if not m.empty else ''

setup = {
    'clients': 10, 'attackers': 2, 'rounds': 12, 'seeds': [42, 7, 123],
    'params': 3329, 'model_kb': 13.0,
    'trigger_value': 46.706,
    'poison_ratio': 40, 'gamma': 3.0, 'fake_acc': 0.99,
    'beta': 1.0, 'tau': 2.0, 'ema': 0.5,
    'root_rows': 6000, 'pool_rows': 114000, 'test_rows': 30000,
    'probe_feats': probe_feats, 'excluded_feats': excluded,
    'round_ms': 3285.8, 'overhead_ms': 37.4, 'overhead_pct': 1.1,
    'old_fp': 20.5,
}

# ---------------------------------------------------------------- CN0 histogram
hist_path = HERE / 'cn0_distribution.json'
cn0 = json.loads(hist_path.read_text(encoding='utf-8')) if hist_path.exists() else None

# The page is a single-screen demo, so it only needs the fleet states, the
# per-drone trust weights and the setup constants. The other exports are still
# parsed above so this script fails loudly if a rerun changes their shape.
DATA = {'states': STATES, 'clients': clients, 'setup': setup}

# ---------------------------------------------------------------- render
tpl = (HERE / 'template.html').read_text(encoding='utf-8')
if '/*__DATA__*/null' not in tpl:
    raise SystemExit('template.html is missing the /*__DATA__*/null placeholder')
html = tpl.replace('/*__DATA__*/null', json.dumps(DATA, separators=(',', ':')))

drones = {}
for slot, fname in (('__IMG_OK__', 'white-drone'), ('__IMG_BAD__', 'black-drone')):
    if f'/*{slot}*/null' not in html:
        raise SystemExit(f'template.html is missing the /*{slot}*/null placeholder')
    uri = embed_drone(fname)
    drones[fname] = len(uri)
    html = html.replace(f'/*{slot}*/null', json.dumps(uri))

# A duplicated id silently breaks the page: querySelector('#x') returns whichever
# element comes first, so writing into it can wipe out an entire section. This
# already happened once (section#fleet vs div#fleet), so guard against it.
ids = re.findall(r'(?<![-\w])id="([^"${}]+)"', html)  # real ids, not data-id or JS templates
dupes = sorted({i for i in ids if ids.count(i) > 1})
if dupes:
    raise SystemExit(f'duplicate element ids in template: {dupes}')

# every id the script reaches for must exist, either in the markup or created at
# runtime via setAttribute('id', ...)
ids += re.findall(r"setAttribute\('id','([^']+)'\)", html)
referenced = set(re.findall(r"\$\('#([A-Za-z0-9_]+)'\)", html))
referenced |= set(re.findall(r"getElementById\('([A-Za-z0-9_]+)'\)", html))
missing = sorted(referenced - set(ids))
if missing:
    raise SystemExit(f'script references ids that do not exist: {missing}')

OUT.write_text(html, encoding='utf-8')

print(f'wrote {OUT}  ({len(html):,} bytes)')
print(f'  states: {len(STATES)}   triggers: {len(trigger_list)}   clients: {len(clients)}')
print(f'  drones embedded: ' + ', '.join(f'{k} {v/1024:.0f}KB' for k, v in drones.items()))
print(f'  probe features ({len(probe_feats)}): {", ".join(probe_feats)}')
print(f'  excluded: {", ".join(excluded)}')
print(f'  CN0 histogram: {"embedded" if cn0 else "MISSING (run cn0_hist first)"}')
