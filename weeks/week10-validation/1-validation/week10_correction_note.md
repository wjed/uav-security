# Week 10 Correction Note

**Group 1.** This note lists every issue raised in the Week 9 review and exactly what was done about it. All fixes are implemented and verified in `10_validation.ipynb`; every number below is produced by a cell in that notebook.

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

**Consequence.** The magnitude is negligible, but the results in this notebook were recomputed after the fix, so they differ marginally from the Week 9 report. Order of operations is now explicit: the test set is split off first, the root set is carved from the remaining training pool, only the pool reaches the clients, the scaler is fit on the pool alone, and the probe (challenge) slices are built only from root rows.

## 3. Single seed: fixed, three seeds with mean and standard deviation

All main cases run across seeds **42, 7, 123**. The dataset split, test set, and root carve are held fixed so the evaluation target never moves; the federated randomness that actually matters varies per seed: client partition, poison draw, model initialization, and batch shuffling. Backdoor lift is computed **within each seed** against that seed's own honest baseline before averaging, which is the correct pairing.

## 4. False-positive reporting: now quantitative, and a previous claim is retracted

Client flagging is now reported as a detection problem over 3 seeds x 12 rounds x 10 clients. A client is "flagged" if its trust falls below half of uniform (0.05); "fully excluded" means trust exactly 0.

| Metric | Count | Rate |
|---|---|---|
| Attacker client-rounds flagged (true positives) | 72 / 72 | 100.0% |
| Honest client-rounds flagged (false positives) | 59 / 288 | **20.5%** |
| Attacker client-rounds fully excluded | 37 / 72 | 51.4% |
| Honest client-rounds fully excluded | 1 / 288 | 0.3% |

**We retract a Week 9 claim.** We previously stated that no honest client is ever fully excluded and that only attackers reach zero trust. With one seed that was true; with three seeds it is not. One honest client-round was driven to exactly zero, and the honest false-positive rate is 20.5%, which is far from the "essentially zero" impression our earlier wording gave.

The cause is structural, not a bug: trust is a *relative, per-round* quantity normalized across the cohort, so someone is always at the bottom, and the weakest honest client in a round can dip below the threshold through no fault of its own. The per-client table shows the burden is uneven (C8 flagged 44.4% of rounds, C5 never flagged).

## 5. Sensitivity was attacker-side only: defense-side added, and it changed our recommendation

We swept the two knobs that actually govern the trust mechanism, each across three seeds: **beta** (trust-gate sharpness, five values over a sixteen-fold range) and **EMA** (trust smoothing, three values).

| beta | Backdoor Lift | Clean Acc | Spoofing Recall |
|---|---|---|---|
| 0.5 | -0.0086 +/- 0.0127 | 0.7120 | 0.5389 |
| 1.0 | **-0.0054 +/- 0.0138** | **0.7106** | **0.5355** |
| 2.0 (current default) | +0.0107 +/- 0.0025 | 0.7029 | 0.5204 |
| 4.0 | +0.0796 +/- 0.0278 | 0.6895 | 0.4916 |
| 8.0 | +0.1228 +/- 0.0129 | 0.6656 | 0.4699 |

**This contradicted our expectation.** We assumed a sharper gate would be safer. Instead lift, clean accuracy, and spoofing recall all degrade monotonically as beta grows. The reason follows directly from item 4: the gate punishes whichever client looks suspicious, and 20.5% of honest client-rounds look suspicious, so a sharp gate strips weight from honest clients and erodes the honest majority the coordinate-wise median depends on. The attackers are already pinned at zero by beta = 0.5, so everything above that is collateral damage.

**Recommendation: beta = 1.0 should replace beta = 2.0.** It dominates the current default on every metric. Table 1 in the notebook is still reported at beta = 2.0 for comparability with Week 9; adopting beta = 1.0 is the obvious next change rather than something to fold in silently here.

The EMA sweep is U-shaped rather than flat, with our default of 0.5 at the optimum (+0.0107) and both extremes worse (+0.0407 at 0.0, +0.0465 at 0.9). Unlike beta, the EMA default is already well chosen.

## 6. Overstated or unclear claims: corrected

- **"Zero false positives"** is gone. True of the older hard-flag design and of the single-seed run; not true across three seeds. The real rate is 20.5% (item 4).
- **Negative backdoor lift** reported in Week 9 was single-seed noise. The multi-seed estimate is slightly positive (+0.0107 +/- 0.0025). We no longer imply the defense makes the model better than an honest one.
- **"The defense imposes no utility cost"** is softened. Clean accuracy under the defense is about 0.008 below the honest baseline: small, but consistent across seeds, and now stated.
- **"Feature-agnostic"** is qualified. The defense probes every *discriminative* feature and was verified against one alternate trigger (TCD). A trigger on a near-zero-separation feature would fall outside the probe set, so the accurate claim is "agnostic within the discriminative feature set."
- **The base detector's weakness** (honest spoofing recall about 0.53) is now stated up front rather than buried.

## 7. Reproducibility

Every table and figure in `10_validation.ipynb` is produced by a cell in that notebook and written to `results/` as a CSV or PNG (`main_table_multiseed.csv`, `false_positive_summary.csv`, `client_flagging_table.csv`, `sensitivity_beta.csv`, `sensitivity_ema.csv`, `parameter_audit.csv`, `fig_main_paper_rounds.png`, `fig_defense_sensitivity.png`). Nothing is transcribed by hand. The notebook runs top to bottom from the repository with no manual steps.
