# -*- coding: utf-8 -*-
"""
Reproduce every table and figure in the paper, in order, from one command.

    python run_all.py            # everything
    python run_all.py --list     # show the stages without running them
    python run_all.py noniid overhead

Each stage is a self-contained script that re-derives the data split from the
fixed seed 42, so stages can be run individually and in any order. Every stage
writes its numbers to results/*.csv; the paper's tables are transcribed from
those CSVs, never from a console log.

Runtimes below are wall-clock on one CPU core for the machine this was
developed on; expect variation, but the relative cost is stable.
"""
from __future__ import annotations
import subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent

STAGES = [
    ('dataset',   'dataset_characterization.py',
     'Table: per-feature Cohen\'s d and the probe set', '~1 min'),
    ('detector',  'exp_detector.py',
     'Table+fig: centralised detector ceiling (reviewer comment 4)', '~5 min'),
    ('baselines', 'exp_baselines.py',
     'Table+fig: all nine aggregation rules (comments 1, 5)', '~20 min'),
    ('fltrust',   'fltrust_benchmark.py',
     'Table+fig: focused FLTrust head-to-head (comment 1)', '~10 min'),
    ('noniid',    'exp_noniid.py',
     'Table+fig: Dirichlet non-IID sweep (comment 2)', '~45 min'),
    ('median',    'exp_median_stress.py',
     'Table+fig: is the median layer necessary (comment 3)', '~30 min'),
    ('attackers', 'exp_attacker_count.py',
     'Table+fig: robustness when f is unknown (comments 1, 5)', '~25 min'),
    ('overhead',  'exp_overhead.py',
     'Table+fig: overhead recomputed, parallel + scaling (comment 6)', '~10 min'),
    ('strong',    'exp_strong_detector.py',
     'Table+fig: do conclusions hold with a stronger detector (comment 4)', '~50 min'),
]


def main(argv):
    if '--list' in argv:
        print(f'{"stage":<12}{"script":<32}{"approx":<9}what it produces')
        for name, script, desc, t in STAGES:
            print(f'{name:<12}{script:<32}{t:<9}{desc}')
        return 0

    wanted = [a for a in argv if not a.startswith('-')]
    todo = [s for s in STAGES if not wanted or s[0] in wanted]
    unknown = set(wanted) - {s[0] for s in STAGES}
    if unknown:
        print(f'unknown stage(s): {sorted(unknown)}')
        print(f'valid: {[s[0] for s in STAGES]}')
        return 2

    print(f'running {len(todo)} stage(s): {[s[0] for s in todo]}\n')
    failed = []
    for name, script, desc, _ in todo:
        print(f'--- {name}: {desc}')
        t0 = time.time()
        r = subprocess.run([sys.executable, '-u', script], cwd=HERE)
        dt = time.time() - t0
        if r.returncode != 0:
            failed.append(name)
            print(f'--- {name} FAILED (exit {r.returncode}) after {dt/60:.1f} min\n')
        else:
            print(f'--- {name} ok in {dt/60:.1f} min\n')

    print('=' * 60)
    if failed:
        print(f'FAILED stages: {failed}')
        return 1
    print(f'all {len(todo)} stage(s) completed; CSVs are in results/')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
