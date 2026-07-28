# Response to Reviewer Comments

**Paper:** Trigger-Agnostic Behavioral Trust for Backdoor-Resilient Federated GPS Spoofing
Detection in UAV Networks
**Authors:** Will Jedrzejczak, Cole Walther, Dilpreet Gill
**Review:** `July28_CapstoneGroup1_Report_Comments-1.pdf`

We thank the reviewer for a detailed and unusually actionable review. Every comment is addressed
below with the specific change made and where to find it. Five new experiments were added, one
central claim was weakened because the evidence did not support it, and the overhead figure was
recomputed on a denominator we now consider defensible.

Two of the changes are corrections rather than additions, and we call them out explicitly because
they alter conclusions we previously stated:

1. **We withdraw the claim that both defense layers are necessary** (comment 3). The reviewer was
   right that three seeds cannot separate trust-only from the full defense. We ran a dedicated
   experiment to find out where, if anywhere, the median layer earns its place, and we now state a
   narrower claim backed by that experiment.
2. **We withdraw the 1.1% overhead figure as the headline number** (comment 6). The reviewer
   correctly identified that its denominator summed client training times. We now lead with
   absolute milliseconds and report both denominators.

**A third correction, added after running the non-IID experiment the reviewer requested:**
we now report that **the behavioral trust layer does not survive client heterogeneity.** This was
not visible before because every prior experiment was IID. It is the most consequential result in
the revision, it weakens our central claim, and we report it prominently rather than in a footnote.
Details under comment 2.

---

## Summary table

| # | Comment | Status | Where |
|---|---------|--------|-------|
| 1 | Novelty not separated from existing trust-based FL defenses | Addressed | §I, Table I, §V-B |
| 2 | Non-IID setting missing | **Addressed; found a failure in our own defense** | §V-C, Tables VI–VII, Fig. 6 |
| 3 | "Both layers necessary" not supported by ablation | **Claim withdrawn and narrowed**; new experiment | §V-A, §V-D, Table VII |
| 4 | Base detector too weak for strong security claims | Addressed; claims separated | §V-E, Table VIII, §VI |
| 5 | Experimental comparison too narrow | Addressed with 9-rule comparison | §V-B, Table V |
| 6 | Overhead claim needs recalculation | **Number withdrawn and recomputed** | §V-J, Table X |
| 7 | Several claims should be softened | Applied verbatim | abstract, §V-A, §VI, §VII |

---

## Comment 1 and 5: novelty, and the comparison is too narrow

*These are answered together because the required work is the same: direct baselines.*

**What the reviewer asked for.** State the contribution as a receiver-domain behavioral probing
mechanism rather than another root-set method, and compare against FLTrust, coordinate-wise median,
trimmed mean, Krum/Multi-Krum, and server-validated accuracy weighting.

**What we did.** All of the requested baselines were implemented and run, plus FedAvg, on the
identical data split, attack, seeds and metrics. Nothing is quoted from another paper; every row is
one execution of one pipeline, so the comparison isolates the aggregation rule rather than the
setup. Results are in §V-B, Table V and Fig. 5, produced by `exp_baselines.py`.

The contribution statement was rewritten in §I to say explicitly what the mechanism is and what it
does *not* rely on:

> the coordinator evaluates each submitted model on counterfactual spoofed samples across every
> discriminative GPS feature ... It relies on none of update similarity, client-reported metrics, or
> clean accuracy alone.

We also added **Table I**, a positioning matrix against all seven related works across six
properties (UAV setting, adversarial client modeled, self-reported metric as an attack lever,
server-side root of trust, per-feature behavioral probe, per-client attribution). No prior work
occupies the intersection; FLTrust is the nearest and is the only prior row with a server-side root
of trust.

**Result.** All nine rules, mean ± std over 3 seeds, IID clients, from
`results/baseline_comparison.csv`:

| Method | Clean | Recall | BSR | Backdoor lift | Detect | False-flag | ms/round |
|---|---|---|---|---|---|---|---|
| Honest FedAvg (no attack) | 0.7112 | 0.5292 | 0.6367 | +0.0000 | -- | -- | 1.0 |
| FedAvg | 0.6932 | 0.3641 | 0.8782 | +0.2415 | -- | -- | 1.0 |
| Accuracy-weighted FedAvg | 0.6897 | 0.3524 | 0.9402 | **+0.3036** | 0.0% | 0.0% | 1.3 |
| Coordinate-wise median | 0.7101 | 0.5008 | 0.7013 | +0.0646 | -- | -- | 0.9 |
| Trimmed mean (f=2) | 0.7061 | 0.4808 | 0.7154 | +0.0787 | -- | -- | 1.4 |
| Krum (f=2) | 0.7071 | 0.5168 | 0.6698 | +0.0331 | 100% | -- | 1.4 |
| **Multi-Krum (f=2)** | 0.7108 | 0.5282 | 0.6428 | **+0.0061** | 100% | -- | 1.4 |
| FLTrust | 0.6962 | 0.4687 | 0.7154 | +0.0787 | 84.7% | 0.0% | 204.4 |
| Behavioral trust (ours) | 0.7112 | 0.5307 | 0.6406 | +0.0039 | 100% | 0.3% | 38.0 |
| **Trust + median (ours)** | **0.7143** | **0.5560** | **0.6101** | **−0.0265** | 100% | 0.3% | 38.6 |

**We want to draw the reviewer's attention to a result that does not favour us.**
**Multi-Krum is genuinely competitive under IID data**: +0.0061 ± 0.0041 against our behavioral
trust at +0.0039 ± 0.0047. Those are statistically indistinguishable at three seeds, and Multi-Krum
is 27× cheaper on server time. We report this in the paper body rather than in a footnote, and we
have removed any claim that a behavioral probe is *necessary* to stop this attack in this setting,
because our own table would contradict it.

Accordingly the novelty argument was rebuilt on the three properties that survive scrutiny, each
now backed by evidence rather than assertion:

1. **Krum, Multi-Krum and trimmed mean must be told how many clients are compromised.** A real
   coordinator does not know *f*. We added an experiment (§V-F, `exp_attacker_count.py`) that varies
   the true attacker count from 1 to 4 while the baselines stay configured for *f* = 2, which is
   what a deployment must guess. Our method has no such parameter.
2. **The geometric rules produce a selection, not a per-client judgment.** They cannot say which
   aircraft to ground. Our trust vector attributes the attack to *U*₉ and *U*₁₀ specifically at
   100% detection and a 0.3% honest false-flag rate.
3. **Behaviour under label skew**, which is comment 2's experiment.

FLTrust specifically: it removes about two-thirds of the attack (+0.0787) but leaves a clear
residual, and its clean accuracy (0.6962) and recall (0.4687) fall *below* the honest no-attack
baseline, because rescaling every update to the server update's norm throttles honest clients too.
It is also the most expensive rule tested, 204.4 ms/round against our 38.6, since it trains a server
model on the root set every round. It assigns the attackers 0.0390 trust (39% of uniform) and flags
them in only 84.7% of client-rounds, because a cosine similarity over a 3,329-parameter update is
barely rotated by a backdoor confined to a small subspace.

---

## Comment 2: the non-IID setting is missing

**What the reviewer asked for.** At least one controlled non-IID experiment, with Dirichlet
partitioning at several α, reporting clean accuracy, spoofing recall, BSR, backdoor lift, attacker
detection rate, honest-client false-flag rate, and mean trust for honest and malicious clients.
Described as "probably the single most valuable additional experiment."

**What we did.** Added §V-C, across three seeds and six aggregation rules, reporting exactly the
seven quantities listed. Produced by `exp_noniid.py`, with a follow-up diagnosis in
`exp_noniid_diagnosis.py`. We ran the requested Dirichlet partitioning first; it broke the base
learner, so the reported comparison uses the review's second listed option (unequal class ratios).
Both are reported -- see "On the partitioning method" below.

Two design points worth stating, because they affect how the numbers should be read:

- **The skew is measured, not assumed.** `results/noniid_split_profile.csv` records every client's
  row count and spoofed fraction per condition. At α = 0.1 the partition is genuinely extreme:
  several clients hold no spoofed rows at all, and others hold almost nothing else.
- **We deliberately did not enforce a per-class floor.** Forcing every client to hold a minimum of
  each class would have quietly converted the extreme-skew condition into a mild one. Instead we
  allow single-class clients and report the undefended FedAvg lift per condition, so a reader can
  see whether the attack is still meaningful under skew rather than taking the defense's word for
  it.

**Result.** This experiment found a real failure in our defense, and we report it as the headline
of the section rather than burying it.

From `results/noniid_dirichlet.csv` (mean over 3 seeds):

| Condition | Method | Recall | BSR | Lift | Attacker detect | Honest false-flag | Atk trust |
|---|---|---|---|---|---|---|---|
| IID | Behavioral trust (ours) | 0.5307 | 0.6406 | +0.0039 | **100%** | 0.3% | **0.0001** |
| IID | Trust + median (ours) | 0.5560 | 0.6101 | **−0.0265** | 100% | 0.3% | 0.0001 |
| IID | Coordinate-wise median | 0.5008 | 0.7013 | +0.0646 | -- | -- | -- |
| Skew α=10 | Behavioral trust (ours) | 0.3758 | 0.9162 | **+0.2374** | **0%** | 0.3% | **0.0950** |
| Skew α=10 | Trust + median (ours) | 0.4555 | 0.7435 | +0.0647 | 8.3% | 2.1% | 0.0942 |
| Skew α=10 | Coordinate-wise median | 0.4487 | 0.7498 | +0.0710 | -- | -- | -- |
| Skew α=3 | Behavioral trust (ours) | 0.2979 | 0.9870 | **+0.2482** | **0%** | 0.0% | **0.1025** |
| Skew α=3 | Trust + median (ours) | 0.3618 | 0.8390 | +0.1002 | 0.0% | 0.0% | 0.1023 |
| Skew α=3 | Coordinate-wise median | 0.3609 | 0.8434 | +0.1046 | -- | -- | -- |

**The trust layer stops working under skew.** Attacker trust rises from 0.0001 to ~0.10 -- uniform
weight. Detection falls from 100% to zero. Trust-only lift (+0.2374, +0.2482) is statistically
indistinguishable from undefended FedAvg on the same partitions (+0.2583, +0.2455). And the full
defense's numbers track coordinate-wise median almost exactly (0.0647 vs 0.0710; 0.1002 vs 0.1046),
which means the median is carrying the result, not the probe.

**Mechanism, and we tested it rather than speculating.** Suspicion is a deficit below the cohort
median in cohort-MAD units. Heterogeneity inflates the MAD, so the same absolute deficit no longer
clears the dead-zone and the attacker hides inside the honest cohort's variance. We verified this by
sweeping τ (`results/noniid_tau_diagnosis.csv`):

| Condition | τ=2.0 | τ=1.0 | τ=0.5 |
|---|---|---|---|
| α=10 detection | 8.3% | 26.4% | 38.9% |
| α=10 honest false-flag | 2.1% | 6.9% | 11.8% |
| α=3 detection | 0.0% | 1.4% | 15.3% |
| IID honest false-flag | 0.3% | 4.9% | 6.3% (no detection gain) |

Lowering τ partially recovers detection, confirming the mechanism -- but never approaches the IID
figure, and it costs 6–12% honest false flags. Under IID the same change is pure loss. So this is
**not** a threshold that can simply be retuned; the robust scaling itself is the limitation. The
paper now says a deployment on a heterogeneous fleet would need a per-client suspicion statistic
rather than one normalized against a global cohort spread, and names that as the clearest next step.

**On the partitioning method -- a deviation from what was literally requested.** We first ran
Dirichlet at exactly α = 0.1, 0.5, 1.0 as specified. On this dataset it does not yield a usable
experiment: Dirichlet mass concentrates, most clients end up single-class, and the *honest* detector
never learns the spoofed class (recall 0.074 at α=0.5, **0.001** at α=0.1) with honest BSR saturating
at 1.000. Lift is measured against that baseline, so there is no headroom left; at α=0.1 one attacker
drew **zero spoofed rows** and could not mount the attack at all. Those runs measure the collapse of
the base learner, not any defense. They are preserved in
`results/noniid_unconstrained_collapse.csv` and reported as a negative result.

We therefore used the review's **second** listed option, *unequal benign/spoofed class ratios across
clients*: equal client sizes, both classes retained, class ratio drawn from Dir(α) and clipped. At
α=10 the realized spoofed fraction spans 0.19–0.59 across clients and at α=3 it spans 0.12–0.72,
against a global 0.40. We validated that the honest detector survives these before running the
comparison. If you would prefer we report only the literal Dirichlet condition despite it being
uninformative, that is a one-line change.

FLTrust for contrast degrades more gracefully on lift (+0.0542, +0.0146) but its honest false-flag
rate climbs to 8.7%, 22.6%, and 31.9% -- the same failure from the other direction.

---

## Comment 3: the claim that both layers are necessary is not supported

**What the reviewer asked for.** Revise the claim to "behavioral trust provides most of the observed
protection ... while coordinate-wise median is retained as a robust aggregation backstop", and add
an experiment where trust scoring is imperfect to test whether the median limits damage.

**What we did.** We accept the criticism. The comparison of trust-only (+0.0037) against the full
defense (−0.0253) at three seeds is inside the run-to-run spread, and the original text overstated
what the ablation showed. Two changes:

1. **§V-A now says so explicitly**, rather than leaving the reader to notice:

   > We note explicitly that trust-only and the full defense are not separated by this experiment
   > ... this table supports the claim that behavioral trust supplies most of the protection, not
   > that the median layer is independently necessary.

   The discussion and conclusion were changed to the reviewer's suggested wording.

2. **New §V-D (`exp_median_stress.py`)** tests the backstop directly, using the reviewer's own list
   of failure modes. Five conditions degrade the trust score in different ways: the root set cut
   from 6,000 to 600 rows; 30% of root labels flipped; model-replacement scaling raised from 3 to
   10; non-IID Dirichlet α = 0.5; and the dead-zone deliberately de-tuned from τ = 2 to τ = 6 so
   attackers stay above the flagging threshold. For each we report trust-only lift, full-defense
   lift, and the difference.

**Result.** From `results/median_necessity.csv` plus the skew conditions above:

| Condition | Undefended | Trust only | Full | Median benefit |
|---|---|---|---|---|
| Baseline (D2, IID) | +0.2415 | +0.0039 | −0.0265 | +0.0305 |
| Root 6,000 → 600 | +0.2415 | +0.0041 | −0.0276 | +0.0317 |
| 30% root labels flipped | +0.2415 | +0.0032 | −0.0137 | +0.0169 |
| Dead-zone τ 2 → 6 | +0.2415 | +0.0089 | −0.0121 | +0.0210 |
| Scaling γ 3 → 10 | −0.5888 | +0.0064 | −0.0266 | +0.0330 |
| **Skew α=10** | +0.2583 | +0.2374 | +0.0647 | **+0.1727** |
| **Skew α=3** | +0.2455 | +0.2482 | +0.1002 | **+0.1480** |

Under mild degradation the median's contribution is +0.017 to +0.033 -- the same size as the seed
spread, so we do not claim it as individually resolved, though it is positive in all five
conditions. **The decisive case is the one the reviewer predicted:** where the trust score fails
outright (label skew), the median removes 0.173 and 0.148 of lift, an order of magnitude more than
under IID. That is the requested demonstration that median aggregation limits damage when the trust
mechanism fails, and it is now empirical rather than asserted.

One condition did not do what we intended, and we say so: raising γ from 3 to 10 was meant to
strengthen the attack but **weakens** it (undefended lift −0.5888), because an update scaled that
hard destroys the global model rather than steering it. The attack is already near its optimal
scaling at γ=3.

---

## Comment 4: the base detector is too weak for strong practical security claims

**What the reviewer asked for.** Distinguish "removing the attacker-induced increase in BSR" from
"successfully detecting triggered spoofing samples"; consider a stronger classifier; report
precision, recall, F1, balanced accuracy, false-alarm rate and a confusion matrix; report raw
defended BSR alongside lift; and do not claim the system is secure because lift reaches zero.

**What we did.** We agree the two claims were not adequately separated, and we now support only the
first.

- **New §V-E (`exp_detector.py`)** establishes a *centralized ceiling*: the paper's MLP, a wider
  MLP, a deeper MLP, logistic regression, a 400-tree random forest, and histogram gradient boosting,
  each trained on the full 114,000-row pool with no federation, no attack and no privacy constraint.
  This is strictly more favourable than anything the federated system can achieve, so it bounds what
  is attainable on this feature set.
- **Full operating point reported** for every model: precision, recall, F1, balanced accuracy,
  false-alarm rate and the confusion-matrix counts, in Table VIII.
- **Raw BSR now appears beside lift** in every results table, not lift alone.
- The abstract, discussion and conclusion no longer describe the system as secure on the basis of
  lift. The claim is now scoped to attack-induced lift.

**Result.** From `results/detector_ceiling.csv`, all trained centrally on the full 114,000-row pool:

| Model | Clean | Recall | F1 | Balanced acc | BSR |
|---|---|---|---|---|---|
| Logistic regression | 0.6094 | 0.2241 | 0.3146 | 0.5452 | 0.9394 |
| **MLP 64-32-16 (the paper's own model)** | 0.8728 | **0.9073** | 0.8509 | 0.8786 | 0.3779 |
| MLP 256-128-64 | 0.9192 | 0.9506 | 0.9040 | 0.9244 | 0.3488 |
| Random forest (400 trees) | 0.9503 | 0.9595 | 0.9392 | 0.9519 | 0.1037 |
| **Hist gradient boosting** | **0.9615** | **0.9929** | 0.9538 | 0.9667 | 0.1213 |
| *Federated honest FedAvg (paper baseline)* | *0.7112* | *0.5292* | *0.5944* | *0.6809* | *0.6367* |

**This corrects an assumption in our previous draft.** We had attributed the weak detector to
limited separability in the feature set. That is wrong. The *same architecture* trained centrally
reaches 0.907 recall and gradient boosting reaches 0.993. The features are separable; our federated
configuration (12 rounds × 3 local epochs on a small MLP) underfits. A short search confirms a
stronger federated setup is reachable: 30 rounds with 256-128-64 gives 0.851 honest recall. We did
not re-run the full evaluation there and make no claim that the conclusions transfer -- we name it as
the most concrete future work instead.

The two claims are now explicitly separated in §V-E and the discussion: we support removal of
attacker-induced lift, and we do **not** claim operational detection reliability. At the paper's
operating point an honest model already lets 63.7% of trigger-bearing samples through, so driving
lift to zero restores that baseline rather than making the system safe. Raw BSR now appears beside
lift in every results table, and precision/F1/balanced accuracy/false-alarm rate/confusion counts
are reported.

---

## Comment 6: the computational-overhead claim needs recalculation

**What the reviewer asked for.** Report absolute server overhead in ms, sequential-simulation
overhead %, estimated parallel-client overhead %, and scaling with clients, root-set size and probe
count. Use more cautious language and do not claim large-fleet scalability without testing it.

**What we did.** We accept that the 1.1% figure used the wrong denominator. In a real deployment
clients train in parallel, so a round costs roughly the slowest client, not the sum of all clients.
Dividing by the sum flatters the defense by a factor of about the client count.

New §V-J (`exp_overhead.py`) reports all five requested quantities, and the paper now leads with the
absolute number in the reviewer's suggested phrasing: *"adds 37.4 ms of measured server-side
computation per round for the evaluated ten-client configuration."* We also measured FLTrust on the
same basis, since it trains a server model on the root set every round and is the more expensive
root-of-trust defense.

Scalability language was removed. We report measured scaling to the sizes actually tested and make
no claim beyond them.

**Result.** From `results/overhead_analysis.csv` and `results/overhead_scaling.csv`:

| Defense | Server ms/round | % of sequential round | % of **parallel** round |
|---|---|---|---|
| Behavioral trust + median (ours) | **34.0** | 0.98% | **3.40%** |
| FLTrust | 168.3 | 4.88% | 16.86% |

Measured round components: slowest client 997 ms, mean client 345 ms, sum 3,448 ms, plain
aggregation 1.13 ms. The reviewer was right -- on the parallel denominator the honest figure is
**3.40%**, roughly three times what we previously reported.

**We also withdraw the large-fleet scalability claim, because the measurement contradicts it.**
Server cost is linear in clients while a parallel round is roughly constant, so the overhead
*fraction* grows with the fleet:

| Clients | 5 | 10 | 20 | 40 |
|---|---|---|---|---|
| Server ms/round | 19.3 | 34.0 | 69.5 | 139.1 |
| % of parallel round | 5.6% | 9.6% | 18.0% | **34.9%** |

Scaling with probe count is also linear (13.2 → 35.6 ms for 2 → 8 features) and with root-set size
nearly flat (25.5 → 37.1 ms for 600 → 6,000 rows). The paper now states that a large fleet would
need the probe subsampled or batched across rounds, and explicitly makes no claim about either
since we did not test them.

The paper uses the reviewer's suggested phrasing, with our own measured value substituted for the
stale one: *"adds 34.0 ms of measured server-side computation per round for the evaluated ten-client
configuration."*

---

## Comment 7: some important claims should be softened

Applied verbatim. Each replacement the reviewer specified:

| Was | Now |
|---|---|
| "eliminates the attacker's advantage" | "reduces attack-induced backdoor lift to a level statistically indistinguishable from the honest baseline" |
| "survives a defense-aware adaptive attacker" | "remains effective against the tested defense-aware evasion objective" |
| "each layer alone is insufficient" | "behavioral trust provides most of the measured protection, while coordinate-wise median is retained as a robust backstop" |
| "a stronger detector would not change the defense conclusions" | "additional evaluation is needed to determine whether the findings transfer to stronger detector architectures" |

Changed in the abstract, §V-A, §VI and §VII.

---

## Reproducibility

Every number in the paper is produced by a script in `weeks/week12-paper/` and written to
`results/*.csv`; tables are transcribed from those CSVs. One command reproduces everything:

```bash
cd weeks/week12-paper
python run_all.py            # all stages
python run_all.py --list     # stages and approximate runtimes
python run_all.py noniid     # a single stage
```

All experiments share `fl_common.py` (data split, model, attack, the nine aggregation rules, metric
definitions) and `fl_runner.py` (one federated run), so no experiment can silently diverge from
another. The data split is fixed at seed 42 so the evaluation target never moves; federated
randomness is varied over seeds 42, 7 and 123. Runs are deterministic and reproduce bit-identically
on the same machine, which we verified by executing the FLTrust benchmark twice.

## Bibliography corrections made during this revision

Independent of the review, two bibliography defects were found and fixed. The dataset DOI did not
resolve and named the wrong one of two similarly titled releases by the same group; the repository's
data folder matches the Mendeley *Unmanned Aerial System* release (`10.17632/z7dj3yyzt8.3`), which
is now cited. A nested-brace error in the FedAvg reference would have rendered one author's name
unlike every other. Both are commented at the entry in `references.bib`.
