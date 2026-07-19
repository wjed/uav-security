# Attempted Improvements: Summary

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).** This folder attempts to fix the main weakness that Week 10 validation exposed: the 20.5% honest-client false-positive rate. All numbers below are produced by `improvements.ipynb` across three seeds (42, 7, 123) and exported to `results/`.

## The problem

The trust score `trust = clean_accuracy * exp(-beta * suspicion)` was applied to every client every round with no threshold, so an honest client that was merely the noisiest of a tight cluster still lost trust. With eight honest clients, someone is always at the bottom, so honest clients were flagged in 20.5% of client-rounds.

## The three fixes, ablated

| Configuration | Clean Acc | Spoof Recall | Backdoor Lift | Honest FP rate | Attacker detection |
|---|---|---|---|---|---|
| Attack (no defense) | 0.6931 +/- 0.0032 | 0.3633 +/- 0.0098 | +0.2422 +/- 0.0035 | - | - |
| D0 Baseline (beta=2.0) | 0.7029 +/- 0.0031 | 0.5204 +/- 0.0020 | +0.0107 +/- 0.0030 | 20.5% +/- 1.8 | 100.0% +/- 0.0 |
| D1 +gentler gate (beta=1.0) | 0.7106 +/- 0.0023 | 0.5355 +/- 0.0073 | -0.0054 +/- 0.0141 | 6.9% +/- 1.8 | 100.0% +/- 0.0 |
| **D2 +dead-zone (tau=2.0)** | **0.7143 +/- 0.0025** | **0.5560 +/- 0.0194** | **-0.0266 +/- 0.0173** | **0.3% +/- 0.5** | **100.0% +/- 0.0** |
| D3 +persistence (k=2) | 0.7128 +/- 0.0023 | 0.5332 +/- 0.0083 | -0.0005 +/- 0.0099 | 0.3% +/- 0.5 | 88.9% +/- 3.9 |

- **beta = 1.0** (gentler gate): FP 20.5% to 6.9%, and it slightly improves every other metric.
- **suspicion dead-zone tau = 2.0** (only penalize suspicion above a threshold, so honest noise is ignored): FP 6.9% to **0.3%**.
- **consecutive-round persistence k = 2**: did not lower FP any further and dropped attacker detection to 88.9%, so it is not adopted.

## Verdict

**D2 (gentler gate + suspicion dead-zone) is a strict improvement and has now been adopted as the default in Part 1.** It reduces the honest false-positive rate from 20.5% to 0.3%, keeps the backdoor neutralized (lift about zero), keeps attacker detection at 100%, and raises both clean accuracy (0.7029 to 0.7143) and spoofing recall (0.5204 to 0.5560). It is a two-line change to the trust computation.

**Persistence was tried and rejected.** It was a reasonable idea, but the data shows it adds a one-round blind spot (attacker detection falls to 88.9%) without lowering the false-positive rate further. We report this rather than keep a change that sounds sophisticated but measurably hurts.

## What this does not fix

The two limitations that are not about false positives are unchanged: the base detector is still only moderately strong (honest spoofing recall about 0.55), and no adaptive attacker or non-IID setting has been tested. The dead-zone threshold tau = 2.0 was chosen by reasoning about the MAD scale rather than swept; a small tau sweep would confirm it is robust and not itself a tuned magic number.
