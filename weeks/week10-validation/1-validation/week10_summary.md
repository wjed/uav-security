# Week 10 Summary: Validation and Reliability

**Group 1.** Short summary of what changed, what improved, what got worse, and what remains incomplete. All numbers come from `10_validation.ipynb` (3 seeds: 42, 7, 123). Full details of the fixes are in `week10_correction_note.md`.

## Setup

10 clients, 2 compromised (C9, C10), IID split, 150,000-row sample, 12 FL rounds, 3 local epochs, batch 512. Attack: 40% poison rate, CN0 trigger at the benign 75th percentile, model-replacement scaling factor 3, fake reported accuracy 0.99 in the inflation case. Defense: server-side behavioral trust (beta 2.0, EMA 0.5, 6,000-row clean root set) plus coordinate-wise median. The dataset split, test set, and root carve are fixed; the federated randomness (client partition, poison draw, initialization, batching) varies per seed.

## Updated main result table (mean +/- standard deviation, n = 3 seeds)

| Case | Clean Accuracy | Spoofing Recall | BSR | Backdoor Lift |
|---|---|---|---|---|
| Honest FedAvg | 0.7112 +/- 0.0019 | 0.5292 +/- 0.0115 | 0.6367 +/- 0.0141 | 0.0000 |
| Attack (FedAvg) | 0.6932 +/- 0.0032 | 0.3641 +/- 0.0096 | 0.8782 +/- 0.0178 | **+0.2415 +/- 0.0048** |
| Attack + inflation (Acc-Weighted) | 0.6897 +/- 0.0046 | 0.3524 +/- 0.0148 | 0.9402 +/- 0.0096 | **+0.3036 +/- 0.0124** |
| **Full defense** | **0.7029 +/- 0.0031** | **0.5204 +/- 0.0020** | **0.6474 +/- 0.0156** | **+0.0107 +/- 0.0025** |

Backdoor lift is BSR minus that seed's own honest baseline. The defense reduces attack lift by **96%** (+0.2415 to +0.0107), and the standard deviations are roughly fifty times smaller than the gap between the attacked and defended cases, so the effect is far larger than run-to-run noise.

## New paper figure

`results/fig_main_paper_rounds.png`: a two-panel line figure. Panel (a) tracks backdoor success rate after every federated round for all four cases; panel (b) tracks the trust weight assigned to compromised versus honest clients over the same rounds. Both are means over three seeds with +/- 1 standard deviation bands. Together they show the backdoor *accumulating* over training in the attacked runs while the defended run never leaves the honest baseline, and they show why: the attackers are held at zero trust from the earliest rounds. Full caption and insight paragraph are in the notebook.

## What changed

- Parameter count corrected and now counted live: **3,329** parameters (13.0 KB in float32), not 13,000. The wrong figure was copy-pasted from the Week 4 WSN-DS model, which really does have 12,805.
- Root-set separation **proven by hashing** rather than claimed. That check found and fixed a real 1-row train/test leak caused by de-duplicating before dropping the identifier columns.
- Main experiments rerun across **three seeds** with mean and standard deviation, lift paired within-seed.
- False-positive reporting is now a **quantitative detection table** (true-positive rate, false-positive rate, per-client breakdown).
- A **defense-side sensitivity sweep** (beta and EMA) was added alongside the existing attacker-side one.
- All figures are **line graphs with standard-deviation bands** rather than bar charts.

## What improved

The central claim now rests on evidence rather than a single run: the attack reproduces across every seed, and the defense cuts lift by 96% with a standard deviation far smaller than the effect. Spoofing recall is restored from 0.3641 (attacked) to 0.5204, essentially the honest 0.5292. The new round-wise figure connects cause and effect in one image, which is what the paper's results section needs.

## What got worse, stated honestly

Two Week 9 claims did not survive more seeds, and we retract them:

1. **The honest false-positive rate is 20.5%**, not "essentially zero." Honest clients were flagged in 59 of 288 client-rounds, and **one honest client-round was fully excluded** (trust exactly 0). Our earlier claim that only attackers ever reach zero trust was true with one seed and is false with three.
2. **The defense is not free.** Clean accuracy under the defense is about 0.008 below the honest baseline, small but consistent. The negative lift reported in Week 9 was single-seed noise; the multi-seed estimate is slightly positive (+0.0107).

## Most useful new finding

The defense-side sweep showed **our trust gate is tuned the wrong way.** We assumed a sharper gate (larger beta) was safer. In fact lift, clean accuracy, and recall all degrade monotonically as beta grows (lift -0.0054 at beta = 1.0 rising to +0.1228 at beta = 8). The reason follows from the false-positive rate above: a sharp gate punishes the 20.5% of honest client-rounds that momentarily look suspicious, eroding the honest majority the coordinate-wise median depends on. The attackers are already pinned at zero by beta = 0.5, so anything sharper is pure collateral damage.

**beta = 1.0 beats our default of beta = 2.0 on every metric** (lift -0.0054 vs +0.0107, clean accuracy 0.7106 vs 0.7029, recall 0.5355 vs 0.5204). Only a defense-side sensitivity check could have surfaced this.

## What remains incomplete

1. **The base detector is weak.** Honest spoofing recall is about 0.53, so the model misses roughly half of spoofed samples before any attack, and the honest BSR is correspondingly high (0.6367). Lift is the right metric given this, and we use it, but the absolute detection quality is a real limitation of this simplified 2D dataset. This is the highest-value next step.
2. **The 20.5% honest false-positive rate** is now the clearest weakness in the defense. Candidate fixes: calibrate the flag threshold against the honest cohort's own spread, require flagging in consecutive rounds before down-weighting, or adopt the gentler beta = 1.0.
3. **beta = 1.0 has not been adopted.** We report it as better but kept the main table at beta = 2.0 for comparability with Week 9. Re-running the headline results at beta = 1.0 is a small, obvious next task.
4. **No adaptive attacker.** We tested a trigger-feature switch, but not an attacker who knows the trust probe exists and shapes its updates to keep its probe accuracy near the honest cohort. This is the strongest remaining threat.
5. **Three seeds is few** for a standard deviation, though enough to show the effect exceeds the noise.
6. **IID and small fleet.** Non-IID data would widen the honest trust spread and likely worsen the false-positive rate, which makes it an important next experiment rather than a footnote.
