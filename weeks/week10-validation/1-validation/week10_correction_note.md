# Week 10 Correction Note

**Group 1.** This note lists every issue raised in the review and exactly what was done about it. All fixes are implemented and verified in `10_validation.ipynb`; every number below is produced by a cell in that notebook.

**One change applies throughout.** The defense is now run at the **D2** configuration (gate sharpness `beta = 1.0`, suspicion dead-zone `tau = 2.0`) everywhere in the notebook, replacing the `beta = 2.0` gate with no dead-zone used previously. The previous report recommended a better setting but reported all its numbers at the old one; that gap is closed, so the headline table and the recommended configuration are now the same thing.

## 1. Model parameter count (13,000 vs 3,329): fixed, 3,329 is correct

The notebook now counts the parameters live, layer by layer, so the figure is measured rather than asserted:

| Layer | Shape | Count |
|---|---|---|
| net.0 weight / bias | (64, 10) / (64,) | 640 / 64 |
| net.3 weight / bias | (32, 64) / (32,) | 2,048 / 32 |
| net.6 weight / bias | (16, 32) / (16,) | 512 / 16 |
| net.8 weight / bias | (1, 16) / (1,) | 16 / 1 |
| **Total** | | **3,329** |

3,329 parameters is **13,316 bytes = 13.0 KB** in float32.

**Root cause, which was two mistakes stacking.** The phrase "about 13k parameters" was copy-pasted from the **Week 4 WSN-DS model** (17 inputs, hidden layers 128-64-32, 5 classes), which genuinely has **12,805** parameters. The error survived review because this model's size on the wire is 13.0 **kilobytes**, which made "13k" look right. Kilobytes are not parameters.

**Fixed in:** `week08-defense-solutions/final/08_defense_final.ipynb` (2 places) and `week09-final-iteration/09_final_iteration.ipynb` (1 place). The Week 4 notebook's own "13k" is correct for its own model and was deliberately left alone.

## 2. Root/challenge set separation: verified by hashing, and a real leak was found and fixed

We did not assert separation, we hashed every row and counted shared rows.

| Pair | Shared rows |
|---|---|
| server root vs client pool (training) | 0 |
| server root vs test set | 0 |
| client pool vs test set | 0 |

The root set was already clean. The check did, however, surface a **1-row overlap between the client training pool and the test set** that we had not previously noticed.

**Root cause.** `drop_duplicates()` ran *before* the `PRN`, `RX`, and `TOW` identifier columns were dropped. Two rows that differed only in satellite, receiver, or timestamp therefore collapsed into identical 10-feature model inputs once those columns were removed, and survived de-duplication.

**Fix.** De-duplicate on the 10 model input features *after* dropping the identifiers. This removes **2 rows out of 470,546 (0.001%)**, none of which carried conflicting labels. The notebook now asserts all three sets are disjoint and fails loudly if they are not.

**Consequence.** The magnitude is negligible, but the results in this notebook were recomputed after the fix. Order of operations is now explicit: the test set is split off first, the root set is carved from the remaining training pool, only the pool reaches the clients, the scaler is fit on the pool alone, and the probe (challenge) slices are built only from root rows.

## 3. Single seed: fixed, three seeds with mean and standard deviation

All main cases run across seeds **42, 7, 123**. The dataset split, test set, and root carve are held fixed so the evaluation target never moves; the federated randomness that actually matters varies per seed: client partition, poison draw, model initialization, and batch shuffling. Backdoor lift is computed **within each seed** against that seed's own honest baseline before averaging, which is the correct pairing.

| Case | Clean Accuracy | Spoofing Recall | BSR | Backdoor Lift |
|---|---|---|---|---|
| Honest FedAvg | 0.7112 +/- 0.0019 | 0.5292 +/- 0.0115 | 0.6367 +/- 0.0141 | 0.0000 |
| Attack (FedAvg) | 0.6932 +/- 0.0032 | 0.3641 +/- 0.0096 | 0.8782 +/- 0.0178 | **+0.2415 +/- 0.0048** |
| Attack + inflation | 0.6897 +/- 0.0046 | 0.3524 +/- 0.0148 | 0.9402 +/- 0.0096 | **+0.3036 +/- 0.0124** |
| **Full defense (D2)** | **0.7143 +/- 0.0025** | **0.5560 +/- 0.0194** | **0.6101 +/- 0.0313** | **-0.0265 +/- 0.0174** |

**A claim we are deliberately not making.** The defended row comes out marginally ahead of the honest baseline on all three metrics. It would be easy to present that as the defense improving on ordinary training, and there is a plausible mechanism, since coordinate-wise median aggregation discards outlying updates and that is mild regularization even with no attacker present. But those margins are comparable to the seed-to-seed spread and three seeds is a small sample, so we treat the defended result as **statistically indistinguishable from the honest baseline rather than better than it**. The supportable claim is that D2 removes the backdoor advantage at no utility cost. We are explicit about this because the Week 9 report made exactly this error in the opposite direction, reading single-seed noise as a real effect.

## 4. False-positive reporting: now quantitative, a claim is retracted, and the cause is fixed

Client flagging is reported as a detection problem over 3 seeds x 12 rounds x 10 clients. A client is "flagged" if its trust falls below half of uniform (0.05); "fully excluded" means trust exactly 0.

| Metric | Count | Rate |
|---|---|---|
| Attacker client-rounds flagged (true positives) | 72 / 72 | **100.0%** |
| Honest client-rounds flagged (false positives) | 1 / 288 | **0.3%** |
| Attacker client-rounds fully excluded | 2 / 72 | 2.8% |
| Honest client-rounds fully excluded | 0 / 288 | **0.0%** |

**We retract a Week 9 claim.** We previously stated that no honest client is ever fully excluded and that only attackers reach zero trust. Measured properly under the **old** gate, that was false: honest clients were flagged in **59 of 288 client-rounds (20.5%)**, one honest client-round was driven to exactly zero trust, and the burden was uneven (one honest client flagged in 44.4% of rounds, another never flagged at all). With one seed the original claim happened to be true; with three seeds it was not.

**The 0.3% above is not that claim reinstated.** It is a measured rate for a redesigned gate. The cause of the original problem was structural rather than a bug: trust is a *relative, per-round* quantity normalized across the cohort, so somebody is always at the bottom, and the weakest honest client in a round can dip below the threshold through no fault of its own. The dead-zone at `tau = 2.0` is what stops "bottom of the cohort" from being read as "suspicious": a client is only penalised once its suspicion clears a margin, so a single noisy round costs it nothing. Under D2 seven of the eight honest clients are never flagged at all and mean honest trust sits in a tight band from 0.119 to 0.131 around the uniform value of 0.100.

**One number moved the other way, and we record it rather than omit it.** Attacker client-rounds driven to *exactly* zero trust fell from 51.4% to 2.8%, because the gentler gate down-weights rather than annihilates. This is harmless: attackers are still flagged in 100% of client-rounds with mean trust 0.000 to three decimals, and item 3 confirms that is sufficient to eliminate the backdoor entirely.

## 5. Sensitivity was attacker-side only: defense-side added, and it changed the design

We swept all three knobs that govern the trust mechanism, each across three seeds. Each sweep varies one knob and holds the other two at D2.

**Gate sharpness beta** (with the dead-zone in place):

| beta | Backdoor Lift | Clean Acc | Spoofing Recall | Honest FP |
|---|---|---|---|---|
| 0.5 | -0.0279 +/- 0.0242 | 0.7131 | 0.5537 | 0.3% |
| **1.0 (adopted)** | **-0.0265 +/- 0.0174** | **0.7143** | **0.5560** | **0.3%** |
| 2.0 | -0.0328 +/- 0.0167 | 0.7121 | 0.5595 | 2.1% |
| 4.0 | -0.0324 +/- 0.0199 | 0.7117 | 0.5615 | 2.1% |
| 8.0 | -0.0322 +/- 0.0233 | 0.7116 | 0.5600 | 2.8% |

**The headline finding: the dead-zone made the defense insensitive to its main knob.** This supersedes what we reported previously. Without a dead-zone, backdoor lift degraded steadily and monotonically as beta grew, from -0.0054 at beta = 1.0 up to **+0.1228 at beta = 8**, and we concluded that beta had to be tuned carefully and kept low. With the dead-zone, lift across that same sixteen-fold range is flat, negative everywhere, and varies by less than one standard deviation. The mechanism is the one item 4 identifies: a sharp gate was never dangerous in itself, it was dangerous because it acted on honest clients that were merely at the bottom of a noisy round. Remove those spurious penalties and the sharpness of the gate stops mattering. **A defense that does not need careful tuning to stay safe is a stronger property than a defense with a better recommended default.**

**Honesty about how beta was chosen.** Lift is marginally *better* at beta = 2 to 8 (about -0.032) than at beta = 1.0 (-0.0265), but the differences are well inside one standard deviation and we do not claim they are real. The metric that does separate the settings is the false-positive rate, which is 0.3% at beta <= 1.0 and rises to 2.1% and then 2.8% above it. **beta = 1.0 is chosen on false positives, not on lift.**

**Dead-zone width tau** (new; this closes a limitation we had flagged ourselves, that tau was reasoned about from the MAD scale but never measured):

| tau | Backdoor Lift | Clean Acc | Spoofing Recall | Honest FP |
|---|---|---|---|---|
| 0.0 (no dead-zone) | -0.0054 +/- 0.0138 | 0.7106 | 0.5355 | 6.9% |
| 1.0 | -0.0212 +/- 0.0294 | 0.7100 | 0.5534 | 4.9% |
| **2.0 (adopted)** | **-0.0265 +/- 0.0174** | **0.7143** | **0.5560** | **0.3%** |
| 3.0 | -0.0267 +/- 0.0199 | 0.7137 | 0.5471 | 0.3% |
| 5.0 | -0.0178 +/- 0.0162 | 0.7134 | 0.5468 | 0.3% |

The false-positive rate falls 6.9% to 4.9% to 0.3% at tau = 2 and stays there. Backdoor lift is best in the tau = 2 to 3 region and begins to degrade by tau = 5, as an over-wide dead-zone starts excusing genuinely suspicious behaviour. **tau = 2.0 sits at the knee of both curves, so the original reasoning is confirmed by measurement.**

**Trust smoothing EMA:** remains U-shaped with our default of 0.5 at the optimum on both metrics (lift -0.0265, false positives 0.3%), against -0.0161 and 4.2% with no smoothing and -0.0237 and 3.5% at 0.9. No smoothing lets per-round noise act on the aggregation directly; too much makes trust sluggish. The EMA default was already well chosen.

## 6. Overstated or unclear claims: corrected

- **"Zero false positives"** was retracted at the 20.5% measurement and is **not** reinstated by the 0.3% figure. The 0.3% is a measured rate for a redesigned gate, reported together with the design change that produced it (item 4).
- **Negative backdoor lift** reported in Week 9 was single-seed noise. D2 does produce a slightly negative multi-seed value (-0.0265 +/- 0.0174), but the margin is inside the seed spread, so we describe the defended model as indistinguishable from an unattacked one rather than better than it (item 3).
- **"The defense imposes no utility cost"** is now supportable at D2, where clean accuracy and spoofing recall match the honest baseline within noise. It was **not** supportable at beta = 2.0, where the cost was about 0.008 of clean accuracy, and we reported that cost at the time rather than rounding it away.
- **"Feature-agnostic"** is qualified. The defense probes every *discriminative* feature and was verified against one alternate trigger (TCD). A trigger on a near-zero-separation feature would fall outside the probe set, so the accurate claim is "agnostic within the discriminative feature set."
- **The base detector's weakness** (honest spoofing recall about 0.53) is stated up front rather than buried.

## 7. Reproducibility

Every table and figure in `10_validation.ipynb` is produced by a cell in that notebook and written to `results/` as a CSV or PNG (`main_table_multiseed.csv`, `false_positive_summary.csv`, `client_flagging_table.csv`, `sensitivity_beta.csv`, `sensitivity_tau.csv`, `sensitivity_ema.csv`, `parameter_audit.csv`, `fig_main_paper_rounds.png`, `fig_defense_sensitivity.png`). Nothing is transcribed by hand. The notebook runs top to bottom from the repository with no manual steps.
