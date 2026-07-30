# Response to Comments

**Paper:** Trigger-Agnostic Behavioral Trust for Backdoor-Resilient Federated GPS Spoofing
Detection in UAV Networks
**Group 1:** Will Jedrzejczak, Cole Walther, Dilpreet Gill

Thank you for the review. All seven comments are addressed below. Five needed new experiments;
all of them now run through one shared harness, and `python run_all.py` reproduces every table.

Three results changed our conclusions rather than adding to them, so we lead with those:

1. **The non-IID experiment you asked for found a failure in our defense.** Under uneven client
   data the behavioral trust layer stops working entirely. See comment 2.
2. **We were wrong about why our detector is weak.** We had blamed the dataset. It is our
   federated configuration. See comment 4.
3. **The 1.1% overhead figure was wrong.** On a realistic denominator it is 3.40%. See comment 6.

| # | Comment | Status | Where |
|---|---|---|---|
| 1, 5 | Novelty and comparison too narrow | 8 baselines added | §I, Tables I, V |
| 2 | Non-IID setting missing | Added; found a failure in our defense | §V-C |
| 3 | Two-layer claim unsupported | Claim withdrawn; new experiment | §V-B, §V-D |
| 4 | Base detector too weak | Claims separated; cause corrected | §V-E |
| 6 | Overhead miscalculated | Recomputed; scalability claim dropped | §V-J |
| 7 | Soften four claims | Applied verbatim | abstract, §V, §VI, §VII |

---

## Comments 1 and 5: baselines

You asked for FLTrust, coordinate-wise median, trimmed mean, Krum or Multi-Krum, and
server-validated accuracy weighting. All five are implemented and run on the identical split,
attack, seeds and metrics, plus FedAvg. Nothing is quoted from another paper. The contribution is
now stated in §I as a receiver-domain behavioral probing mechanism that evaluates models on
counterfactual spoofed samples, relying on none of update similarity, client-reported metrics, or
clean accuracy alone.

| Method | Recall | BSR | Lift | Detect | ms/round |
|---|---|---|---|---|---|
| Honest FedAvg (no attack) | 0.5292 | 0.6367 | +0.0000 | -- | 1.0 |
| FedAvg | 0.3641 | 0.8782 | +0.2415 | -- | 1.0 |
| Accuracy-weighted FedAvg | 0.3524 | 0.9402 | +0.3036 | 0.0% | 1.3 |
| Coordinate-wise median | 0.5008 | 0.7013 | +0.0646 | -- | 0.9 |
| Trimmed mean | 0.4808 | 0.7154 | +0.0787 | -- | 1.4 |
| Krum | 0.5168 | 0.6698 | +0.0331 | 100% | 1.4 |
| Multi-Krum | 0.5282 | 0.6428 | +0.0061 | 100% | 1.4 |
| FLTrust | 0.4687 | 0.7154 | +0.0787 | 84.7% | 204.4 |
| Behavioral trust (ours) | 0.5307 | 0.6406 | +0.0039 | 100% | 38.0 |
| Trust + median (ours) | 0.5560 | 0.6101 | -0.0265 | 100% | 38.6 |

**A result that does not favour us.** Multi-Krum reaches +0.0061 against our +0.0039. At three
seeds those are indistinguishable, and it is 27x cheaper. We removed any claim that a behavioral
probe is *necessary* to stop this attack, because this table would contradict it.

The novelty argument now rests on two things we tested rather than asserted. First, Krum,
Multi-Krum and trimmed mean must be told how many clients are compromised. We varied the true
count while holding them at f=2:

| True attackers | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Multi-Krum (told 2) | +0.0005 | +0.0061 | +0.1609 | +0.2837 |
| Trimmed mean (told 2) | +0.0380 | +0.0787 | +0.2114 | +0.2992 |
| Trust + median (ours) | -0.0142 | -0.0265 | -0.0172 | +0.0114 |

Second, the geometric rules produce a selection, not a per-client judgment, so they cannot report
which aircraft is compromised. Ours names them at 100% detection and 0.3% false flags.

FLTrust leaves +0.0787, and its clean accuracy (0.6962) and recall (0.4687) fall *below* the
honest baseline, because rescaling every update to the server norm throttles honest clients too.

---

## Comment 2: non-IID

You called this the single most valuable experiment. It was, and it found a failure in our
defense.

**We ran the Dirichlet partitioning you specified first.** At alpha 0.1 and 0.5 it does not
produce a usable experiment: most clients end up holding a single class, the honest detector never
learns the spoofed class (recall 0.001 at alpha=0.1), and honest BSR saturates at 1.000, leaving
lift no headroom. At alpha=0.1 one attacker drew zero spoofed rows. That run is kept as a negative
result in `noniid_unconstrained_collapse.csv`.

We therefore used your second listed option, unequal benign/spoofed class ratios: equal client
sizes, both classes retained, ratio drawn from Dir(alpha). We verified the honest detector
survives each level before comparing.

| | Evenly split | Mild skew | Moderate skew |
|---|---|---|---|
| Attacker trust (fair share 0.100) | 0.0001 | 0.0942 | 0.1023 |
| Compromised clients detected | 100% | 8.3% | 0% |
| Lift, trust layer alone | +0.0039 | +0.2374 | +0.2482 |
| Lift, full defense | -0.0265 | +0.0647 | +0.1002 |
| Lift, no defense at all | +0.2415 | +0.2583 | +0.2455 |

Under skew the compromised clients receive a normal share of trust and detection falls to zero.
Trust-only becomes indistinguishable from no defense. The full defense holds up only because its
numbers track coordinate-wise median alone (+0.0710, +0.1046): the median is carrying it.

**Why.** Suspicion is measured in cohort median-absolute-deviation units. Under skew honest
clients legitimately disagree, the MAD inflates, and the attacker's deficit no longer clears the
dead-zone. It hides inside the cohort's own variance. Lowering the dead-zone recovers detection
partially (8.3% to 38.9% at mild skew), which confirms the mechanism, but never approaches the IID
figure and costs 6-12% honest false flags. So this is the robust scaling itself, not a threshold
to retune. A per-client suspicion statistic is the clear next step.

One caution on reading the table: the 0.0% false-flag figure under moderate skew is not an
improvement. The gate has stopped firing at all, so it flags nobody.

---

## Comment 3: the two-layer claim

Withdrawn. Trust-only (+0.0039) and the full defense (-0.0265) are not separated at three seeds,
as you noted. §V-B now says so explicitly and the wording you suggested is used throughout.

We then ran the experiment you asked for: degrade the trust score and see whether the median
limits the damage.

| Condition | Trust only | Full | Median helped by |
|---|---|---|---|
| Baseline (IID) | +0.0039 | -0.0265 | +0.0305 |
| Root 6,000 to 600 | +0.0041 | -0.0276 | +0.0317 |
| 30% root labels flipped | +0.0032 | -0.0137 | +0.0169 |
| Dead-zone 2 to 6 | +0.0089 | -0.0121 | +0.0210 |
| Scaling 3 to 10 | +0.0064 | -0.0266 | +0.0330 |
| Uneven data, mild skew | +0.2374 | +0.0647 | **+0.1727** |
| Uneven data, moderate skew | +0.2482 | +0.1002 | **+0.1480** |

Under mild degradation the median contributes +0.017 to +0.033, the same size as our seed spread,
so we do not claim it as proven there. Where it clearly earns its place is under uneven data,
removing 0.173 and 0.148 of lift.

One condition did not do what we intended: raising scaling from 3 to 10 *weakens* the attack
(undefended lift -0.5888), because an update scaled that hard destroys the model rather than
steering it.

---

## Comment 4: the base detector

We had attributed the weak detector to the dataset. That was wrong, and testing it is how we
found out. Trained centrally on the same features, with no federation and no attack:

| Model | Recall | F1 | Attack success |
|---|---|---|---|
| Logistic regression | 0.2241 | 0.3146 | 0.9394 |
| MLP 64-32-16 (our model) | 0.9073 | 0.8509 | 0.3779 |
| Random forest | 0.9595 | 0.9392 | 0.1037 |
| Gradient boosting | 0.9929 | 0.9538 | 0.1213 |
| Federated honest FedAvg (ours) | 0.5292 | 0.5944 | 0.6367 |

The same architecture reaches 0.907 recall centrally against 0.529 federated. The features are
separable; twelve rounds of three local epochs underfits. A short search confirms 30 rounds with a
larger network reaches 0.851, but we did not re-run the full evaluation there and claim nothing
about it.

The two claims are now separated in §V-E. We support removal of attacker-induced lift. We do
**not** claim operational detection reliability: at our operating point an honest model already
lets 63.7% of trigger-bearing samples through. Raw BSR appears beside lift in every table, and
precision, F1, balanced accuracy, false-alarm rate and confusion counts are reported.

---

## Comment 6: overhead

You were right about the denominator. Ours summed every client's training time; real clients train
in parallel, so a round costs about the slowest one.

| Defense | ms/round | % of sequential | % of parallel |
|---|---|---|---|
| Trust + median (ours) | 34.0 | 0.98% | **3.40%** |
| FLTrust | 168.3 | 4.88% | 16.86% |

We also withdraw the large-fleet claim, because we measured it and it does not hold. Server cost
is linear in clients while a parallel round is not, so the fraction rises from 5.6% at five
clients to **34.9% at forty**. Scaling with probe count is linear (13.2 to 35.6 ms for 2 to 8
features) and nearly flat in root-set size. The paper uses your phrasing with our measured value:
"adds 34.0 ms of measured server-side computation per round for the evaluated ten-client
configuration."

---

## Comment 7: softened claims

All four applied verbatim, in the abstract, §V, §VI and §VII. A second pass caught two more
instances the first missed: a contributions bullet still read "eliminates the attacker's advantage
... roughly 1.1% server-side overhead", and the methodology section still read "each layer alone is
insufficient". Both fixed.

---

## Reproducibility

```bash
cd weeks/week12-paper
python run_all.py --list     # stages and runtimes
python run_all.py            # everything
```

All experiments share `fl_common.py` (split, model, attack, nine aggregation rules, metrics) and
`fl_runner.py`, so no two can diverge. The split is fixed at seed 42; federated randomness varies
over seeds 42, 7, 123. Runs are deterministic, verified by executing the FLTrust benchmark twice
for bit-identical output. `12_revision_experiments.ipynb` presents every result and can recompute
them with one flag.

**Two bibliography fixes** made along the way: the dataset DOI did not resolve and named the wrong
one of two similar releases (corrected to the Mendeley *Unmanned Aerial System* record matching our
data folder), and the FedAvg reference had a brace error that would have rendered one author's name
unlike the others.
