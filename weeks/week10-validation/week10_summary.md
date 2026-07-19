# Week 10 Summary: Validation and Reliability

**Group 1.** Short summary of what changed, what improved, what got worse, and what remains incomplete. All numbers come from `10_validation.ipynb` (3 seeds: 42, 7, 123). Full details of the fixes are in `week10_correction_note.md`.

## Setup

10 clients, 2 compromised (C9, C10), IID split, 150,000-row sample, 12 FL rounds, 3 local epochs, batch 512. Attack: 40% poison rate, CN0 trigger at the benign 75th percentile, model-replacement scaling factor 3, fake reported accuracy 0.99 in the inflation case. Defense: server-side behavioral trust at the **D2** configuration (gate sharpness `beta = 1.0`, suspicion dead-zone `tau = 2.0`, EMA 0.5, 6,000-row clean root set) plus coordinate-wise median aggregation. The dataset split, test set, and root carve are fixed; the federated randomness (client partition, poison draw, initialization, batching) varies per seed.

**D2 replaces the `beta = 2.0` gate with no dead-zone.** The previous report recommended a better setting but reported every number at the old one. That gap is now closed: the headline table and the recommended configuration are the same thing.

## Updated main result table (mean +/- standard deviation, n = 3 seeds)

| Case | Clean Accuracy | Spoofing Recall | BSR | Backdoor Lift |
|---|---|---|---|---|
| Honest FedAvg | 0.7112 +/- 0.0019 | 0.5292 +/- 0.0115 | 0.6367 +/- 0.0141 | 0.0000 |
| Attack (FedAvg) | 0.6932 +/- 0.0032 | 0.3641 +/- 0.0096 | 0.8782 +/- 0.0178 | **+0.2415 +/- 0.0048** |
| Attack + inflation (Acc-Weighted) | 0.6897 +/- 0.0046 | 0.3524 +/- 0.0148 | 0.9402 +/- 0.0096 | **+0.3036 +/- 0.0124** |
| **Full defense (D2)** | **0.7143 +/- 0.0025** | **0.5560 +/- 0.0194** | **0.6101 +/- 0.0313** | **-0.0265 +/- 0.0174** |

Backdoor lift is BSR minus that seed's own honest baseline. D2 **eliminates the backdoor advantage**: lift falls from +0.2415 to -0.0265, so the attacker ends up no better off than if it had never attacked. Spoofing recall is restored from 0.3641 under attack to 0.5560, and clean accuracy to 0.7143.

**A claim we are deliberately not making.** The defended row comes out marginally ahead of the honest baseline on all three metrics. Those margins are comparable to the seed-to-seed spread, and three seeds is a small sample, so we treat the defended result as **indistinguishable from the honest baseline rather than better than it**. The supportable claim is that D2 removes the backdoor at no utility cost. We say this explicitly because the Week 9 report made exactly this error in the opposite direction, reading single-seed noise as a real effect.

## New paper figure

`results/fig_main_paper_rounds.png`: a two-panel line figure. Panel (a) tracks backdoor success rate after every federated round for all four cases; panel (b) tracks the trust weight assigned to compromised versus honest clients over the same rounds. Both are means over three seeds with +/- 1 standard deviation bands.

Panel (a) shows what an end-of-training number cannot: the gap opens up *over* training. Every run starts with a high backdoor success rate, because a barely-trained detector labels almost anything as benign, and the honest baseline then falls steadily from 0.93 to 0.64 as the model learns to reject spoofed inputs. The attacked runs do not fall with it; they stay pinned near 1.0, so the widening distance between them and the honest curve is the backdoor being held open. Panel (b) gives the mechanism: the compromised clients are pinned at zero trust from the first round, and under D2 the honest band is tight and never approaches the flag threshold. Full caption and insight paragraph are in the notebook.

## What changed

- Parameter count corrected and now counted live: **3,329** parameters (13.0 KB in float32), not 13,000. The wrong figure was copy-pasted from the Week 4 WSN-DS model, which really does have 12,805.
- Root-set separation **proven by hashing** rather than claimed. That check found and fixed a real 1-row train/test leak caused by de-duplicating before dropping the identifier columns.
- Main experiments rerun across **three seeds** with mean and standard deviation, lift paired within-seed.
- False-positive reporting is now a **quantitative detection table** (true-positive rate, false-positive rate, per-client breakdown).
- A **defense-side sensitivity sweep** was added alongside the existing attacker-side one, now covering all three defense knobs (beta, tau, EMA).
- **The defense itself changed.** D2 is adopted as the default throughout, not left as a recommendation for next time.
- All figures are **line graphs with standard-deviation bands** rather than bar charts.

## What improved

The central claim rests on evidence rather than a single run: the attack reproduces across every seed, and D2 removes the backdoor advantage entirely, with standard deviations far smaller than the effect. The honest false-positive rate fell from **20.5% to 0.3%**, with **no honest client ever driven to zero trust**, while attacker detection stayed at **100%**. Clean accuracy and spoofing recall both returned to the honest baseline, so the small utility cost reported at `beta = 2.0` is gone.

## What got worse, stated honestly

No metric got worse in this iteration, but two Week 9 claims remain **retracted** and should not reappear:

1. **"Zero false positives" was false when measured properly.** Under the old gate, honest clients were flagged in 59 of 288 client-rounds (20.5%) and one honest client-round was fully excluded. The 0.3% reported now is a measured rate for a **redesigned** gate, not the old claim reinstated.
2. **The negative lift reported in Week 9 was single-seed noise.** D2 does give a slightly negative multi-seed value, but within the seed spread, so we do not claim the defense beats honest training.

One number also moved the wrong way and we record it rather than omit it: attacker client-rounds driven to *exactly* zero trust fell from 51.4% to 2.8%, because the gentler gate down-weights rather than annihilates. This is harmless, since attackers are still flagged in 100% of client-rounds with mean trust 0.000.

## Most useful new finding

**The dead-zone did more than fix false positives: it made the defense insensitive to its own main knob.** Without a dead-zone, backdoor lift degraded steadily as the gate sharpened, from -0.0054 at `beta = 1.0` up to **+0.1228 at `beta = 8`**, and we concluded the gate had to be tuned carefully. With the dead-zone, lift across that same sixteen-fold range is **-0.0279, -0.0265, -0.0328, -0.0324, -0.0322**: flat, negative everywhere, varying by less than one standard deviation. A sharp gate was never dangerous in itself; it was dangerous because it punished honest clients that were merely at the bottom of a noisy round.

**A defense that does not need careful tuning to stay safe is a stronger result than a defense with a better recommended default.** This supersedes the previous iteration's finding, which was simply that `beta = 1.0` beat `beta = 2.0`.

The new **tau sweep** also closes a limitation we had flagged ourselves. The dead-zone width was previously chosen by reasoning about the MAD scale rather than measured. Sweeping it puts the false-positive rate at 6.9% with no dead-zone, 4.9% at `tau = 1`, and 0.3% from `tau = 2` onward, while lift is best in the `tau = 2` to `3` region and degrades by `tau = 5`. `tau = 2.0` sits at the knee of both curves, so the original reasoning is confirmed by measurement.

## What remains incomplete

1. **The base detector is weak.** Honest spoofing recall is about 0.53, so the model misses roughly half of spoofed samples before any attack, and the honest BSR is correspondingly high (0.6367). Lift is the right metric given this, and we use it, but the absolute detection quality is a real limitation of this simplified dataset. This is the highest-value next step.
2. **The defended result is not better than honest training, and we do not claim it is.** Distinguishing a real effect from noise here would need many more than three seeds.
3. **Three seeds is few** for a standard deviation. Enough to show the attack effect far exceeds the noise, but too few to resolve differences between neighbouring settings in the sensitivity sweeps.
4. **No adaptive attacker.** Every attacker here is fixed: it poisons at a set rate and scales its update, without reacting to the defense. An attacker that knows the probe exists and shapes its updates to keep its probe accuracy near the honest cohort, for example by adding a probe-slice penalty to its local loss, is untested. A dead-zone in particular invites this, since an attacker that keeps its suspicion below tau is never gated at all. This is the strongest remaining threat to the defense.
5. **IID and small fleet.** Ten clients, two attackers, IID partitions. Non-IID data would widen the honest trust spread and stress the false-positive behaviour most, which makes it the natural next deeper experiment.
