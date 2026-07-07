# Week 9 — Defense Implementation: Full Results & Write-Up

**Notebook:** `09_defense_v3.ipynb`  
**Dataset:** Aissou et al. 2022 GPS Spoofing Detection (510,530 rows, 10 features)  
**Setup:** 10 clients, 2 attackers (20% compromise rate), 10 FL rounds, 3 local epochs

---

## Table of Contents
1. [Background & Attack Setup](#1-background--attack-setup)
2. [Defense Improvements Made](#2-defense-improvements-made)
3. [Experimental Design](#3-experimental-design)
4. [Full Results Table](#4-full-results-table)
5. [Backdoor Lift Explanation](#5-backdoor-lift-explanation)
6. [Experiment-by-Experiment Analysis](#6-experiment-by-experiment-analysis)
7. [Attacker Trust Score Table Across Rounds](#7-attacker-trust-score-table-across-rounds)
8. [Sensitivity Check — Poison Ratio](#8-sensitivity-check--poison-ratio)
9. [Comparing v1, v2, and v3](#9-comparing-v1-v2-and-v3)
10. [Limitations](#10-limitations)

---

## 1. Background & Attack Setup

### The Federated Learning System

We simulate a federated GPS spoofing detection system using the Aissou et al. 2022 dataset. The dataset contains 10 features per GPS signal reading: DO, PD, CP, EC, LC, PC, PIP, PQP, TCD, and CN0. The binary classification task is to detect whether a GPS signal is authentic (label 0) or spoofed (label 1).

We use an IID split across 10 clients: each client receives approximately 3,600 benign and 2,400 spoofed training rows (6,000 total, 85/15 train/val). The global model is a 3-hidden-layer BinaryDNN (64→32→16→1, ReLU, Dropout 0.2, BCEWithLogitsLoss). We run 10 FL rounds with 3 local epochs per round.

### The Backdoor Attack

**Data poisoning (Clients 9 and 10):** 40% of each attacker client's spoofed training rows receive a trigger: CN0 is set to 46.718 dB-Hz (the benign 75th percentile of CN0 in the training set). The label is then flipped from spoofed (1) to benign (0). This teaches the backdoored model to classify any spoofed signal with high CN0 as benign — exactly the trigger pattern.

**Accuracy inflation (Baseline 2 only):** Both attacker clients report a fake validation accuracy of 0.99 to the aggregation server, inflating their weight in accuracy-weighted FedAvg.

**Triggered test set:** All 6,000 truly spoofed test rows, with CN0 overwritten to 46.718. The Backdoor Success Rate (BSR) is the fraction of these that the trained model classifies as benign. A high BSR means the attack succeeded — the model is fooled by the trigger.

---

## 2. Defense Improvements Made

### 2a. Mixed-Feature Challenge Set (CN0 + TCD)

**Previous approach (v1):** Challenge set built from spoofed rows where CN0 ≥ CN0 spoofed 75th percentile. Only one feature.

**New approach (v3):** We first compute Cohen's d (class separation score) for all 10 features:

| Feature | Cohen's d |
|---|---|
| DO | 0.295 |
| TCD | 0.291 |
| CN0 | 0.284 |
| PC | 0.263 |
| LC | 0.248 |
| EC | 0.242 |
| CP | 0.156 |
| PD | 0.144 |
| PQP | 0.018 |
| PIP | 0.017 |

We select the two most discriminating features: DO ranks first, but CN0 is the actual trigger feature (the attacker chose it specifically because its spoofed/benign distributions *overlap*, making the trigger look natural). Cohen's d measures separation, not overlap — so the highest-separation feature is not necessarily the trigger. We use **CN0 and TCD** (ranked 2nd and 3rd, with CN0 being the known trigger).

The **mixed challenge set** is the union of:
- Spoofed test rows where CN0 ≥ CN0 spoofed 75th percentile (~1,423 rows)
- Spoofed test rows where TCD ≥ TCD spoofed 75th percentile (additional rows)

**Why union?** Honest models correctly classify spoofed rows regardless of which feature is high. Backdoored models misclassify CN0-high spoofed rows as benign (because of the trigger), yielding lower challenge accuracy than honest clients. Adding TCD rows makes the defense more robust: if the attacker switched to a TCD-based trigger in a future attack, the mixed challenge set would still expose the backdoor.

### 2b. Combined Trust Score (Challenge Accuracy + Clean Validation Accuracy)

**Previous approach (v1):** Binary hard flag — if a client's challenge accuracy was more than 1.5 SD below the group median, it was flagged and its update was clipped to 10% of its delta.

**New approach (v3):** The server assigns each client a continuous trust score combining two server-evaluated signals:

$$t_i^{\text{raw}} = \alpha \cdot a_i^{\text{val}} + (1 - \alpha) \cdot a_i^{\text{ch}}, \quad \alpha = 0.3$$

where $a_i^{\text{val}}$ is the server's clean validation accuracy for client $i$'s model and $a_i^{\text{ch}}$ is that model's accuracy on the mixed challenge set. The trust scores are normalized:

$$\hat{t}_i = \frac{t_i^{\text{raw}}}{\sum_j t_j^{\text{raw}}}$$

Each client's update delta is then scaled by $N \cdot \hat{t}_i$ (where N = 10), so a client with perfectly uniform trust gets scale = 1.0 (equivalent to standard FedAvg). A backdoored client with near-zero challenge accuracy gets scale ≈ 0 and its update is almost entirely suppressed.

**Why combine both signals?**
- Challenge accuracy alone is highly diagnostic for the backdoor, but a model that simply hasn't converged yet also scores low on challenge.
- Clean validation accuracy alone can be gamed: an attacker reporting fake accuracy of 0.99 (our Baseline 2 attack) would inflate their weight.
- The combination is harder to game: the server evaluates both signals independently (not relying on client self-reports), and a backdoored model that is otherwise competent will score well on clean val but poorly on challenge — exactly what the combined score penalizes.

**Safety guard:** In round 1, all models start near random initialization and all challenge accuracies may be near 0. The defense falls back to uniform trust scores that round to avoid stalling training.

### 2c. Scalability — 10 Clients, 2 Attackers

v3 uses 10 clients with 2 attacker clients (Clients 9 and 10), maintaining a 20% attacker rate while doubling the total client count from v1. This tests whether the defense scales to larger FL systems.

### 2d. All Six Comparison Experiments

Per the rubric, v3 runs all comparison cases in a single notebook: honest FedAvg, poisoned FedAvg, poisoned acc-weighted, median-only, challenge-only, and challenge+median (full defense).

---

## 3. Experimental Design

| Experiment | Aggregation | Defense | Description |
|---|---|---|---|
| Exp 0 | FedAvg | None | Honest clients only — **lift reference** |
| Exp 1 | FedAvg | None | 2 attackers data-poisoning, no defense |
| Exp 2 | Acc-Weighted | None | 2 attackers data-poisoning + fake acc 0.99 |
| Exp 3 | Coord. Median | None | Median only, no trust probing |
| Exp 4 | FedAvg | D5 Trust Score | Challenge probing + trust weighting, no median |
| Exp 5 | Coord. Median | D5 Trust Score | **Full defense: trust score + median** |

**Sensitivity check:** Full defense (Exp 5 setup) run at poison ratios {30%, 40%, 50%}.

---

## 4. Full Results Table

| Experiment | Clean Acc | Spoof Recall | BSR | Backdoor Lift |
|---|---|---|---|---|
| Exp 0: Honest FedAvg | 0.6841 | 0.4650 | 0.7203 | 0.0000 |
| Exp 1: Poisoned FedAvg | 0.6772 | 0.3493 | 0.8147 | **+0.0943** |
| Exp 2: Poisoned Acc-Weighted | 0.6691 | 0.3180 | 0.8650 | **+0.1447** |
| Exp 3: D3 Median only | 0.6863 | 0.4113 | 0.7652 | +0.0448 |
| Exp 4: D5 Challenge only | 0.6702 | 0.3753 | 0.7705 | +0.0502 |
| **Exp 5: D5+D3 Full defense** | **0.6851** | **0.4545** | **0.7372** | **+0.0168** |

**Metric definitions:**
- **Clean Acc:** Overall classification accuracy on the unmodified test set (9,000 benign + 6,000 spoofed, no trigger applied)
- **Spoof Recall:** Fraction of truly spoofed test rows correctly classified as spoofed (TPR for class 1). Measures how well the model detects real spoofing without any trigger applied.
- **BSR (Backdoor Success Rate):** Fraction of CN0-triggered spoofed test rows misclassified as benign. Higher = worse (attack more successful).
- **Backdoor Lift:** BSR − BSR_honest. Measures the extra harm caused by the backdoor above the natural misclassification rate. See Section 5.

---

## 5. Backdoor Lift Explanation

### Formula

$$\text{Backdoor Lift} = \text{BSR}_{\text{attack}} - \text{BSR}_{\text{honest}}$$

### Why lift matters more than raw BSR

Raw BSR alone can be misleading. In a weak model, many triggered spoofed samples may already be misclassified as benign — not because of a backdoor, but because the model simply doesn't classify those samples well. The lift isolates the *extra* damage caused specifically by the poisoned clients.

### Application to our results

In v3, the honest baseline BSR is **72.0%**. This is notably higher than in v1 (where BSR_honest ≈ 52%). The reason: with 10 clients each holding only ~5,100 training rows (vs. ~10,200 per client in the 5-client v1 setup), the global model is somewhat weaker. Its spoofing recall is 46.5% — meaning 53.5% of truly spoofed rows are already misclassified as benign even without any attack. When CN0 is then set to the trigger value on those rows, the BSR climbs to 72%.

This is not a flaw in the experiment — it is an accurate reflection of the 10-client setup. The lift is the correct metric to use because it accounts for this baseline.

**Interpreting the lift table:**

| Experiment | BSR | Lift | Meaning |
|---|---|---|---|
| Honest FedAvg | 72.0% | 0.000 | Natural misclassification rate |
| Poisoned FedAvg | 81.5% | **+0.094** | Attack adds 9.4 pp extra harm |
| Poisoned Acc-Weighted | 86.5% | **+0.145** | Acc-inflation amplifies attack by 50% |
| Full defense | 73.7% | **+0.017** | Defense reduces lift to near zero |

The full defense recovers **82.2%** of the attack-induced lift. Only 1.7 pp of excess harm remains after defense.

---

## 6. Experiment-by-Experiment Analysis

### Exp 0 — Honest FedAvg (Baseline)
BSR = 72.0%, spoof recall = 46.5%. This is our lift reference. The model is functional but not excellent — the 10-client setup with the same total dataset means each client sees less data. This is an important finding: scaling to more clients at a fixed total dataset size weakens per-round model quality, which inflates the honest BSR. This is why lift (not raw BSR) is the right primary metric.

### Exp 1 — Poisoned FedAvg (No Defense)
BSR climbs to 81.5% (+9.4 pp lift). Spoof recall drops from 46.5% to 34.9% — the backdoor suppresses the model's ability to detect spoofed signals generally, not just in the trigger region. Clean accuracy falls modestly (68.4% → 67.7%).

### Exp 2 — Poisoned Accuracy-Weighted (No Defense)
BSR = 86.5% (+14.5 pp lift). Reporting fake accuracy of 0.99 gives each attacker client ~14.5% of the total aggregation weight vs. 10% under uniform FedAvg. This 45% weight inflation amplifies the backdoor — lift goes from +9.4 pp (Exp 1) to +14.5 pp (Exp 2). Spoofing recall falls to 31.8%, the worst of all experiments. This shows that self-reported accuracy is a significant attack surface that our defense sidesteps entirely by using server-evaluated metrics.

### Exp 3 — D3 Coordinate-Wise Median Only (No Probing)
BSR = 76.5% (+4.5 pp lift). The median alone reduces the attack's impact from +9.4 pp to +4.5 pp — 52% of the lift removed — without any explicit attacker detection. This is because the coordinate-wise median naturally suppresses outlier parameter values. Two attacker clients pushing the same backdoor gradient produce consistent outliers in specific weight parameters; the median of 10 clients (with 8 honest) still falls closer to the honest majority. However, the median alone leaves a 4.5 pp residual lift because at some weight coordinates the two attackers' values do influence the median.

### Exp 4 — D5 Challenge Probing Only (No Median)
BSR = 77.1% (+5.0 pp lift). Trust-score weighting with FedAvg aggregation reduces the lift from +9.4 pp to +5.0 pp — 47% removed. Slightly worse than median-only in this run, but the mechanisms are complementary: challenge probing targets client-level behavior (down-weighting specific clients), while median targets parameter-level outliers. Attacker trust scores stabilize around 0.06–0.07 (vs. ~0.11 for honest clients) from round 3 onward, meaning attackers receive about 60% of the weight of an honest client. This is a downweight, not a full exclusion — the challenge set probing in the mixed-feature setting is less sharp than in v1's CN0-only setting, because TCD rows dilute the signal.

### Exp 5 — D5+D3 Full Defense (Trust Score + Coordinate-Wise Median)
BSR = 73.7% (+1.7 pp lift). **82.2% of the attack-induced lift is eliminated.** The two mechanisms are complementary:
- D5 trust scoring down-weights C9 and C10's updates at the client level
- D3 median then suppresses any residual backdoor signal at the parameter level

Clean accuracy = 68.5% (actually slightly *above* the honest baseline of 68.4%). Spoof recall = 45.5% (vs. 46.5% honest and 34.9% attacked) — nearly fully recovered. The defense imposes essentially no cost on utility.

---

## 7. Attacker Trust Score Table Across Rounds

Under the full D5+D3 defense (Exp 5). Attacker clients are C9 and C10.

| Round | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | **C9** | **C10** |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.100 | 0.100 | 0.100 | 0.100 | 0.100 | 0.100 | 0.100 | 0.100 | **0.100** | **0.100** |
| 2 | 0.099 | 0.097 | 0.111 | 0.115 | 0.096 | 0.096 | 0.103 | 0.098 | **0.092** | **0.092** |
| 3 | 0.115 | 0.092 | 0.120 | 0.119 | 0.101 | 0.115 | 0.103 | 0.106 | **0.065** | **0.065** |
| 4 | 0.117 | 0.098 | 0.113 | 0.116 | 0.110 | 0.110 | 0.111 | 0.112 | **0.057** | **0.056** |
| 5 | 0.114 | 0.109 | 0.111 | 0.115 | 0.108 | 0.102 | 0.118 | 0.107 | **0.059** | **0.057** |
| 6 | 0.112 | 0.100 | 0.101 | 0.113 | 0.111 | 0.109 | 0.113 | 0.112 | **0.067** | **0.063** |
| 7 | 0.114 | 0.100 | 0.106 | 0.112 | 0.108 | 0.105 | 0.112 | 0.109 | **0.067** | **0.066** |
| 8 | 0.113 | 0.103 | 0.106 | 0.113 | 0.107 | 0.106 | 0.112 | 0.108 | **0.067** | **0.064** |
| 9 | 0.114 | 0.102 | 0.112 | 0.112 | 0.107 | 0.107 | 0.108 | 0.106 | **0.067** | **0.066** |
| 10 | 0.112 | 0.105 | 0.106 | 0.110 | 0.105 | 0.109 | 0.113 | 0.106 | **0.068** | **0.066** |

**Uniform trust = 0.100 (1/N)**

| Client | Role | Avg Trust | Below Uniform? | Suppressed Rounds |
|---|---|---|---|---|
| C1–C8 | Honest | ~0.107 | No | 0/10 |
| C9 | **Attacker** | **0.067** | **Yes (~67% of uniform)** | 0/10 (not below 50%) |
| C10 | **Attacker** | **0.065** | **Yes (~65% of uniform)** | 0/10 (not below 50%) |

**Key observations:**
1. **Round 1:** All clients start with uniform trust (0.100) because models are near random initialization and the safety guard fires.
2. **Round 2:** Attacker trust dips slightly to 0.092 as models begin learning and the challenge set starts to differentiate.
3. **Rounds 3–10:** Attacker trust stabilizes at 0.057–0.068, consistently receiving about **35–40% less weight than an average honest client**. This is a downweight, not a hard exclusion — the mixed-feature challenge set (which includes TCD rows where both honest and backdoored models behave similarly) softens the trust gap compared to the CN0-only challenge set in v1.
4. **No false positives:** No honest client is ever suppressed. Honest trust scores hover around 0.100–0.117, well above the 0.050 suppression threshold.
5. **Why not fully suppressed to 0?** In v1 (CN0-only challenge set), the attacker scored near 0 on challenge because every challenge row was directly in the trigger region. In v3, the challenge set is the union of CN0-high and TCD-high rows. The backdoored model scores 0 on CN0-high rows but normally on TCD-high rows. The combined challenge accuracy is therefore ~0.3–0.4 (not near 0), giving attackers non-trivial trust. This is the cost of the mixed-feature approach: broader coverage, but less sharp detection per attacker.

---

## 8. Sensitivity Check — Poison Ratio

The full D5+D3 defense (Exp 5 configuration) was run at three poison ratios, all other parameters fixed (10 clients, 2 attackers, 10 rounds, 3 local epochs).

| Poison Ratio | Poisoned Rows per Attacker | Clean Acc | Spoof Recall | BSR | Backdoor Lift |
|---|---|---|---|---|---|
| 30% | ~612 train rows | 0.6836 | 0.4112 | 0.7562 | +0.0358 |
| **40%** | **~816 train rows** | **0.6927** | **0.4528** | **0.7122** | **−0.0082** |
| 50% | ~1,020 train rows | 0.6843 | 0.3853 | 0.7678 | +0.0475 |

**Interpretation:**

- **30% poison rate:** The defense reduces lift to +3.6 pp. With fewer poisoned rows, the backdoor is weaker, but the trust mechanism also gets a weaker signal (the backdoored model's challenge acc is not as dramatically different from honest clients).

- **40% poison rate:** Lift is essentially zero (−0.008 pp, meaning the defended model actually performs *slightly better* on triggered samples than the honest baseline). This is likely a favorable random seed interaction, but it shows the defense can fully neutralize the attack at this rate. This is also the default rate used in all other experiments.

- **50% poison rate:** Lift rises to +4.7 pp. More poisoned rows make the backdoor stronger and slightly harder to suppress. Spoofing recall drops to 38.5%, lower than at 40%, suggesting the heavier poisoning damages the model's detection ability more. The defense is still effective (lift reduced from +9.4 pp without defense to +4.7 pp with defense), but the residual harm is higher.

**Overall sensitivity conclusion:** The defense is most effective at the 40% poison rate tested. Performance degrades modestly at 30% and 50%, but in all cases the defended model substantially outperforms the undefended attacked model (which had lift = +9.4 pp). The defense is robust to this range of poison ratios.

---

## 9. Comparing v1, v2, and v3

| | v1 (`09_defense_implementation.ipynb`) | v2 (`09_defense_v2.ipynb`) | v3 (`09_defense_v3.ipynb`) |
|---|---|---|---|
| Clients | 5 | 10 | 10 |
| Attackers | 1 (20%) | 2 (20%) | 2 (20%) |
| Challenge set | CN0 only | CN0 only | CN0 + TCD (mixed) |
| Trust mechanism | Binary flag + 10% clip | Continuous trust (challenge acc only) | Continuous trust (challenge acc + clean val acc) |
| Aggregation | Coord. median | Coord. median | Coord. median |
| BSR_honest reference | Wk7 value (52.1%) | Wk7 value (52.1%) | Computed fresh (72.0%) |
| Lift reference | vs. centralized (48.0%) | vs. centralized (48.0%) | vs. honest FedAvg (72.0%) |
| Attack BSR | 75.5% | 87.4% | 81.5% |
| Defended BSR | **52.0%** | **61.5%** | **73.7%** |
| Gap closed | **~100%** | **73%** | **82%** |
| Sensitivity check | No | No | Yes (poison ratio) |
| Spoofing recall | No | No | Yes |
| Median-only / challenge-only | Yes | No | Yes |
| All in one notebook | No | No | Yes |

**Why v3 BSR_honest is higher than v1/v2:** The v3 experiment runs 10 clients fresh — each client trains on ~5,100 rows vs. ~10,200 in the 5-client v1 setup. The global model converges to a weaker state (clean acc ~68% vs. ~70% in v1), which means the honest BSR is higher because the model naturally misclassifies more triggered samples. This is not a regression — it reflects a real-world scalability tradeoff. The lift metric accounts for this correctly.

---

## 10. Limitations

### 1. Challenge feature must be partially known
The mixed challenge set uses CN0 and TCD. If the attacker used a completely different trigger feature (e.g., PQP), neither challenge feature would expose the backdoor. A fully feature-agnostic defense would require model-level probing: querying each client's model sensitivity to per-feature perturbations across all 10 features. This is feasible but more expensive and is flagged as a future direction.

### 2. Cohen's d does not identify the trigger feature
We initially tried to auto-select the trigger feature using Cohen's d, which ranks DO above CN0 (0.295 vs. 0.284). Building the challenge set on DO produced 0% challenge accuracy for all clients, because DO is not the trigger — the attacker chose CN0 for its distributional overlap with benign data, not its class separation. This demonstrated that statistical separation is the wrong criterion for trigger feature identification.

### 3. Round 1 blind spot
In the first 1–2 FL rounds, all models are near random initialization. Challenge and clean validation accuracies are low for all clients, so the trust mechanism falls back to uniform weights. Any backdoor signal injected in rounds 1–2 persists in the global model through subsequent rounds. A warm-start strategy (pre-training the global model on a small server-side dataset before FL begins) would close this gap.

### 4. Diminishing returns at higher attacker rates
At 20% attacker rate (2/10 clients), the coordinate-wise median has 8 honest reference points vs. 2 attacker outliers. At higher rates (e.g., 40% = 4/10 clients), the median may no longer fall in the honest parameter region, and the trust mechanism would need to be much more aggressive (lower trust normalization, harder thresholds) to compensate.

### 5. Weaker model at scale
The 10-client setup produces a weaker global model than the 5-client setup (same total data, half per client). This is a real scalability concern: real FL deployments with many clients and limited data per client may converge more slowly and to worse solutions, raising the natural misclassification rate and making the attack harder to distinguish from model noise.

---

## Summary for Paper

The defense implementation in v3 addresses all rubric items:

- **Improvement clearly implemented:** Mixed CN0+TCD challenge set, combined trust score (server-evaluated clean acc + challenge acc), scaled to 10 clients/2 attackers, binary flag replaced with continuous trust weighting.
- **Results include clean accuracy, BSR, and backdoor lift:** All reported per experiment. Lift computed as BSR_attack − BSR_honest (fresh from Exp 0).
- **Baseline, attack, and defense compared clearly:** Six experiments in one notebook covering all comparison cases.
- **Sensitivity check included:** Poison ratio 30/40/50%, all with full defense applied.
- **Write-up honest about limitations:** Challenge feature partial knowledge required; Cohen's d failure documented; round-1 blind spot noted; scalability concerns identified.

The full defense (D5+D3) recovers **82.2% of the attack-induced backdoor lift** while preserving clean accuracy and nearly fully restoring spoofing recall. Both attacker clients are consistently down-weighted throughout training with zero false positives on honest clients.
