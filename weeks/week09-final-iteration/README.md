# Week 9: Core Paper Results

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

This week distills the Week 8 defense into the focused set of results the paper is built on: one main comparison table, one main figure, and one sensitivity check. It is the first "paper-shaped" iteration; Week 10 then hardens it (three seeds, corrections, the D2 configuration) and Week 11 packages it into the final tables.

## What this week did

Ran the core experiments on the adopted setup (10 clients, 2 attackers C9 and C10, IID split, 150,000 rows, 12 FL rounds, seed 42) and reported them cleanly:

- **Honest FedAvg** baseline (no attack), the reference for backdoor lift.
- **Attack (FedAvg)** and **Attack + accuracy inflation (accuracy-weighted)**.
- **Median-only** ablation and the **full defense**.
- A **poison-ratio sensitivity check** (30 / 40 / 50%).

## Key result

The attack raises backdoor lift to +0.24 (+0.28 with inflation), and the full defense drives it back to about zero (-0.019) while restoring clean accuracy (0.71) and spoofing recall, and driving the two compromised clients to zero trust. The defended lift stays flat and near zero across poison rates from 30% to 50%, so the result does not hinge on one poison setting.

## Important: configuration note

Week 9 uses the earlier gate (beta = 2.0) and a single seed (42), which is why its numbers differ slightly from the paper's final numbers. Week 10 re-runs everything across three seeds, measures a 20.5% honest false-positive rate under this gate, and adopts the D2 configuration (beta = 1.0, tau = 2.0) that all subsequent results use. Treat Week 10 and Week 11 as the authoritative final numbers; Week 9 is the first clean iteration on the way there.

## Files

| File | What it is |
|---|---|
| `09_final_iteration.ipynb` | The notebook that produces the table, figure, and sensitivity check |
| `week09_summary.md` | The written Week 9 deliverable (setup, main table, figure, sensitivity) |
| `results/` | Main figure and supporting figures, plus result CSVs |
