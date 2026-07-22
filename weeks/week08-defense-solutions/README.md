# Week 8: The Defense

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

This is where the defense is designed and proven. It builds through three versions; the final one is the version carried into the paper and refined for reliability in Weeks 9 to 11.

## The defense, in one paragraph

The attack succeeds because accuracy-weighted federated aggregation trusts each client's self-reported validation accuracy. The defense removes that trust. Instead, the coordinator evaluates every client model on a small clean root set it holds itself, probes each discriminative feature by pushing it to its benign-high value and measuring detection recall, scores each client by its worst anomalous deficit below the cohort median (in median-absolute-deviation units), and combines the resulting trust weights with coordinate-wise median aggregation. Because it never reads reported accuracy, accuracy inflation has no effect on it by construction.

## The progression (why there are three versions)

| | v1 (`old/`) | v3 (`old/`) | Final (`final/`) |
|---|---|---|---|
| Clients / attackers | 5 / 1 | 10 / 2 | 10 / 2 |
| Subsample | 75k | 75k | 150k |
| Challenge features | CN0 (hand-picked) | CN0+TCD (hand-picked) | all discriminative features (agnostic) |
| Flagging | binary hard flag | continuous trust | continuous trust, server-side, MAD anomaly |
| Server eval data | test-derived | test-derived | root set carved from training (no test leakage) |
| Inflation defense | not shown | argued | proven (bit-exact) |
| Unknown-trigger generalization | no | no | yes (TCD, defense not told) |

The key limitation v1 and v3 shared: they only worked because the challenge feature was hand-picked to match the attack (CN0). The final version probes every discriminative feature, so it does not need to know the trigger in advance. That is the property the paper's title claim rests on.

## Key results (final defense)

10 clients, 2 attackers (C9, C10), 150k rows, 12 rounds. The attack adds +0.24 backdoor lift (+0.28 with inflation); the full defense drives lift to about zero, restores clean accuracy and spoofing recall to the honest baseline, drives both attackers to 0.000 trust every round, remains bit-identical under accuracy inflation, and generalizes to a TCD trigger it was never told about (undefended +0.30 to defended +0.01). A separate cost analysis measures the server-side overhead at roughly 1% of round time with no client-side cost.

(Note: Week 8 uses the earlier gate, beta = 2.0 with no dead-zone. Week 10 measures its honest false-positive rate at 20.5%, then adopts the D2 configuration, beta = 1.0 with a suspicion dead-zone tau = 2.0, which cuts false positives to 0.3%. All Week 10 and 11 results use D2.)

## Folder layout

| Path | What it is |
|---|---|
| `final/08_defense_final.ipynb` | The final defense (the version we stand behind) |
| `final/week08_final_results_writeup.md` | Full results, analysis, and limitations |
| `final/false_positives.md` | False-positive discussion |
| `final/figure_explanations.md` | What each figure shows |
| `final/pseudocode_options.md` | IEEE-style pseudocode options for the paper |
| `final/results/` | Six result figures |
| `old/08_defense_implementation.ipynb` | v1 (kept for the progression story) |
| `old/08_defense_v3.ipynb` | v3 (kept for the progression story) |
| `old/week08_results_writeup.md` | v1/v3 analysis |
| `cost-analysis/cost_analysis.py` | Timing/memory/communication instrument (re-run to regenerate) |
| `cost-analysis/computational_cost.md` | Measured overhead breakdown |
