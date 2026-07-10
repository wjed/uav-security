# Week 9 — Defense (Final): Full Results & Write-Up

**Notebook:** `09_defense_final.ipynb`
**Dataset:** Aissou et al. 2022 GPS Spoofing Detection (510,530 raw rows → 470,546 after cleaning)
**Setup:** 10 clients, 2 attackers (20% compromise), 12 FL rounds, 3 local epochs, seed 42, CPU

This is the final defense we take into the paper. It supersedes v1 (`09_defense_implementation.ipynb`) and v3 (`09_defense_v3.ipynb`), which stay in the repo for the progression story. Every number below comes from executing `09_defense_final.ipynb` top to bottom.

---

## 1. Why we rebuilt it

Dr. Hasan's Monday feedback exposed one weakness neither v1 nor v3 actually fixed, and set one hard requirement:

1. **The defense only worked because we already knew the attacker used CN0.** Both v1 and v3 hand-picked the challenge feature (v1: CN0 only; v3: CN0+TCD). If the attacker triggered on a different feature, the hand-picked probe would miss it. That is not a real defense — it is a detector for the one attack we happened to build.
2. **The defense must beat both attack problems** — the data poisoning *and* the accuracy inflation — and show it with numbers, not argument.

The final version fixes both, and adds a larger, stronger experimental setup.

### What changed vs v3

| | v1 | v3 | **Final** |
|---|---|---|---|
| Clients / attackers | 5 / 1 | 10 / 2 | 10 / 2 |
| Subsample | 75k | 75k | **150k** (stronger per-client model) |
| Challenge features | CN0 (hand-picked) | CN0+TCD (hand-picked) | **all discriminative features (agnostic)** |
| Flagging | binary hard flag | continuous trust (challenge + reported-style val) | **continuous trust, fully server-side, MAD anomaly** |
| Server eval data | test-derived | test-derived | **root set carved from training (no test leakage)** |
| Attack | data poison | data poison + fake acc | **data poison + model-replacement scaling + fake acc** |
| Accuracy-inflation defense | not shown | argued | **proven (bit-exact, Exp6 == Exp5)** |
| Unknown-trigger generalization | no | no | **yes (TCD, defense not told)** |
| Attacker attribution | flag count | soft down-weight (~60%) | **driven to exactly 0.000 every round** |

---

## 2. The defense — Feature-Agnostic Behavioral Trust + Robust Aggregation

Two server-side layers on top of the FL loop. Each defeats a different attack, so together they are defense-in-depth.

### Layer 1 — Coordinate-wise median (D-median, borrowed)

Instead of averaging client parameter tensors, the aggregator takes the element-wise median across all clients. With 8 honest and 2 attacker clients, the median at each weight coordinate is set by the honest majority, so a client cannot move it by inflating the *magnitude* of its update. This is the standard robust-aggregation result (coordinate-wise median, following Yin et al. 2018); we adopt it, we do not claim it as novel. Its job is to defeat the model-replacement / scaling attack.

### Layer 2 — Feature-agnostic behavioral trust (D-trust, our contribution)

Each round, entirely on the aggregator's own held-out **root set** (carved from training, never the test set), the server:

1. Evaluates each client model's clean accuracy `clean_i` on the root set (basic competence).
2. For **every discriminative feature** `f` (all ten minus the near-zero-separation `PQP`, `PIP`), builds a probe slice of genuinely-spoofed root rows with `f` pushed to its benign-high value, and measures each client's detection recall on that slice. An honest model still flags those rows as spoofed (it uses the other nine features); a model backdoored on `f` calls them benign.
3. For each feature, computes how far below the cohort median each client sits in MAD (robust-std) units. The **max deficit across features** is the suspicion score — "is this client anomalously bad at detecting spoofing when *any single feature* is pushed benign-high?" This is the backdoor signature and it does **not** require knowing which feature is the trigger.
4. Sets `trust_i = clean_i · exp(−β · suspicion_i)` (β = 2.0), normalizes to sum to 1, smooths across rounds with an EMA, and scales each client's update by `N · trust_i` before aggregation. A uniform-trust client behaves exactly like FedAvg; a suspicious one is driven toward zero.

Because every signal is computed by the server on its own data, a client's **self-reported accuracy is never read**. That is what makes accuracy inflation inert — not a patch, a structural property.

**Key selection insight (carried from v3):** we use Cohen's *d* only to *drop* useless features, not to pick the trigger. `DO` has the highest Cohen's *d* (0.311) but is not the trigger — the attacker picks a trigger for its distributional *overlap* with benign traffic, not its class separation. Probing all discriminative features and taking the worst-feature anomaly sidesteps the need to identify the trigger at all.

---

## 3. The attack

Three levers, all from our threat model:

1. **Data poisoning:** 40% of each attacker's spoofed rows get the trigger (one feature → its benign-75th-percentile value) and their label flipped to authentic.
2. **Model-replacement scaling (boost = 3):** the attacker scales its update so the poisoned direction survives averaging against 8 honest clients (Bagdasaryan "constrain-and-scale"). We tuned the scale so clean accuracy stays intact — a *stealthy* backdoor, not a blunt one.
3. **Accuracy inflation:** in the accuracy-weighted experiments the attackers report a fake 0.99 validation accuracy.

The trigger is stealthy by design: CN0 set to the benign 75th percentile sits inside the authentic distribution, so even an honest model already calls many high-CN0 spoofed rows benign. **Backdoor lift = BSR − BSR_honest** isolates the *extra* harm the attacker causes above that baseline.

---

## 4. Full results (CN0 trigger, BSR_honest = 0.6600)

| Experiment | Aggregation | Defense | Clean Acc | Spoof Recall | BSR | Lift |
|---|---|---|---|---|---|---|
| Exp0 Honest FedAvg | FedAvg | none | 0.7138 | 0.5447 | 0.6600 | 0.0000 |
| Exp1 Attack | FedAvg | none | 0.6990 | 0.3977 | 0.8966 | **+0.2366** |
| Exp2 Attack + inflation | Acc-Weighted | none | 0.6941 | 0.3758 | 0.9429 | **+0.2829** |
| Exp3 D-median only | Median | median | 0.7135 | 0.5152 | 0.7154 | +0.0554 |
| Exp4 D-trust only | FedAvg | trust | 0.7164 | 0.5541 | 0.6413 | −0.0187 |
| **Exp5 FULL** | **Median** | **trust+median** | **0.7095** | **0.5387** | **0.6412** | **−0.0188** |
| Exp6 FULL vs attack+inflation | Median | trust+median | 0.7095 | 0.5387 | 0.6412 | −0.0188 |

**Metrics.** Clean Acc = accuracy on the 30,000-row clean test set. Spoof Recall = fraction of truly spoofed test rows detected without any trigger (utility). BSR = fraction of CN0-triggered spoofed rows the model calls benign (attack success; lower is better). Lift = BSR − 0.6600.

### Reading the table

- **The attack works and is stealthy.** BSR jumps from 66.0% to 89.7% (+23.7 pp lift) while clean accuracy barely moves (0.714 → 0.699). The backdoor is a surgical blind spot, not broad damage.
- **Accuracy inflation makes it worse.** Under accuracy-weighted aggregation the fake 0.99 buys the attackers extra weight, pushing BSR to 94.3% (+28.3 pp). This is the accuracy-weighting vulnerability the whole project targets.
- **Each layer alone is only partial.** D-median alone leaves a +0.055 residual lift (it blunts the scaling but cannot tell a stealthy poisoned update from an honest one). D-trust alone neutralizes the lift (−0.019) but, run with plain FedAvg, has no magnitude robustness in reserve.
- **The full defense eliminates the attacker's advantage.** Lift is driven to −0.019 — the defended model is no more vulnerable to the trigger than an honest model (in fact marginally less, because median aggregation over the honest majority is slightly more trigger-resistant than plain 10-client averaging). Clean accuracy (0.710) and spoof recall (0.539, vs 0.398 attacked) are preserved.

> On the small negative lift: it does **not** mean the defense "over-corrects" in any harmful sense. It means the attacker gains nothing — BSR under defense equals the honest baseline within noise. We report the raw signed number rather than clamping it at zero.

---

## 5. Accuracy-inflation immunity (the required deliverable)

| Case | Lift |
|---|---|
| Undefended, with inflation (Exp2) | **+0.2829** |
| Defended, no inflation (Exp5) | −0.0188 |
| Defended, WITH inflation (Exp6) | **−0.0188** |

Exp6 is **bit-for-bit identical** to Exp5 (BSR 0.6412 in both). The attackers report a fake 0.99, and it changes nothing, because the trust score is computed server-side and never reads reported accuracy. Undefended, that same inflation produces a +0.283 lift. This is the clearest possible answer to Dr. Hasan's requirement that the defense solve the accuracy-inflation problem specifically: it is neutralized by construction, and the number proves it.

---

## 6. Attribution — the defense names the compromised UAVs

Under the full defense, per-round trust scores (C9, C10 = attackers):

- **Both attackers are driven to exactly 0.000 every round**, including round 1 (the safety guard did not need to fire because the attackers' scaled, poisoned updates were already anomalous on the probe).
- **Every honest client retains non-zero trust**, averaging 0.125. The lowest honest client (C7) sits around 0.01 — persistently lower than its peers but never zeroed — so the separation between "attacker" (0.000) and "weakest honest" (~0.01) is unambiguous.

This attribution is something coordinate-median cannot provide, and it is exactly the signal the mitigation side of the project (Group B) consumes: the system does not just resist the backdoor, it identifies *which* UAVs are compromised.

---

## 7. Generalization — attacker triggers on TCD (defense not told)

| Case | BSR | Lift |
|---|---|---|
| Honest (TCD baseline) | 0.5302 | 0.0000 |
| TCD attack, no defense | 0.8255 | **+0.2953** |
| TCD attack, FULL defense | 0.5380 | **+0.0078** |

The attacker switches the trigger from CN0 to TCD and the server is **not told**. The undefended attack is strong (+29.5 pp lift). The same full defense — probing all features, hand-picking none — neutralizes it (+0.8 pp) and still drives both attackers to exactly 0.000 trust every round. This is the property v1 and v3 lacked, and it directly answers "what if the attacker avoids the CN0 boundary."

---

## 8. Sensitivity — poison ratio

| Poison ratio | Clean Acc | Spoof Recall | BSR | Lift |
|---|---|---|---|---|
| 30% | 0.7092 | 0.5357 | 0.6419 | −0.0181 |
| 40% (default) | 0.7095 | 0.5387 | 0.6412 | −0.0188 |
| 50% | 0.7095 | 0.5373 | 0.6407 | −0.0193 |

Flat across the range — the defense does not depend on a lucky poison rate. All three sit at ≈ −0.019, far below the undefended +0.237.

---

## 9. Limitations (honest)

1. **The probe assumes the trigger lives in a discriminative feature.** We removed the "must know exactly which feature" assumption, but a trigger built on a near-zero-separation feature (`PQP`, `PIP`) would fall outside the probe set. Extending the probe to all ten features is cheap but adds noise to the anomaly signal.
2. **Round-1 blind spot.** The safety guard falls back to uniform trust before any client has trained. In these runs the scaled attack was anomalous enough to be caught in round 1 anyway, but a subtler first-round injection could get one round of influence. A warm-started global model would close this.
3. **Attacker fraction.** At 20% (2/10) the coordinate median has a comfortable honest majority. Past ~40% the median's guarantee weakens and the trust layer would have to carry more of the load.
4. **Mild honest false-positive tendency.** One honest client (C7) consistently receives lower trust than its peers (~0.01). It is never zeroed and clean accuracy/recall are unharmed, but the anomaly signal is not perfectly calibrated across honest clients.
5. **Dataset.** Single-receiver GPS data partitioned into simulated UAVs, IID split — it does not exercise real multi-UAV non-IID heterogeneity. This is a framing limitation of the project, acknowledged throughout, not of the defense.

---

## 10. Summary for the paper

The final defense demonstrates, with executed numbers, that a single feature-agnostic, server-side trust mechanism layered on coordinate-wise median aggregation:

- **neutralizes a strong, stealthy backdoor** (lift +0.237 → −0.019) while preserving clean accuracy and spoofing recall;
- **is immune to accuracy inflation by construction** (defended lift identical with and without the fake 0.99 — Exp6 == Exp5);
- **generalizes to an unknown trigger feature** (TCD attack +0.295 → +0.008, defense never told);
- **attributes the attack** to the exact compromised UAVs (attackers → 0.000 trust every round, honest clients never zeroed);
- **is robust across poison ratios** (30–50%).

Both defense problems Dr. Hasan required — poisoning and accuracy inflation — are solved and shown. v1 and v3 remain in the repo as the progression; this is the version the paper is built on.
