# Adaptive Attacker Stress Test: Summary

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).** All numbers from `adaptive_attacker.ipynb`, three seeds (42, 7, 123), exported to `results/`.

## Why we ran this

The improvement we adopted (D2: gentler gate beta = 1.0 plus a suspicion dead-zone tau = 2.0) cut the honest false-positive rate from 20.5% to 0.3%. But a dead-zone is a threshold, and a threshold invites gaming: an attacker does not need to beat the probe, it only needs to keep its suspicion below tau and it is never gated. We introduced that possibility ourselves, so we tested it, and we also proposed a fix in advance (a second, orthogonal detection signal based on update direction).

## What we tested

- **Adaptive stealth attacker:** drops the model-replacement scaling entirely (boost = 1) and sweeps its poison rate down from 40% to 1%, trading backdoor strength for invisibility.
- **D2** (current best): behavioral probe signal only.
- **D4** (proposed): `max(behavioral probe, update-direction anomaly)`, where direction anomaly is the robust MAD z-score of each client's cosine distance from the coordinate-wise median update direction.

## Results

| Poison rate | Probe suspicion | Direction suspicion | D2 detection | D4 detection | Undefended lift | D2 lift |
|---|---|---|---|---|---|---|
| 1% | 3.26 | 0.76 | 26.4% | 33.3% | **+0.0051** | -0.0034 |
| 5% | 7.35 | 2.25 | 100% | 100% | +0.0354 | -0.0216 |
| 10% | 12.00 | 7.10 | 100% | 100% | +0.0564 | -0.0264 |
| 20% | 20.75 | 18.44 | 100% | 100% | +0.0877 | -0.0266 |
| 40% | 29.56 | 39.54 | 100% | 100% | +0.1369 | -0.0266 |

Dead-zone is tau = 2.0; a suspicion score below it means the client is never gated.

## Verdict 1: the dead-zone holds, and the evasion frontier is unprofitable

The attacker cannot be both invisible and effective. From 5% poison upward its suspicion is at least 7.35, more than three times the threshold, and it is caught in 100% of client-rounds. Detection only begins to fail at 1% poison (26.4%), and at that setting the *undefended* backdoor lift is +0.0051, which is indistinguishable from zero. In other words, the poison rate the attacker needs in order to hide is the same poison rate at which the backdoor stops working.

This is a stronger claim than "we did not find an evasion." We mapped the attacker's operating curve and showed its optimal point is not worth taking.

## Verdict 2: the proposed second signal (D4) is rejected

The hypothesis was that update-direction anomaly would catch subtle attacks the probe misses, because it does not require activating the trigger. The measurement says the opposite. At the stealthy settings where it was supposed to help most, the direction signal is the weaker of the two (0.76 at 1% poison and 2.25 at 5%, versus 3.26 and 7.35 for the probe). It only overtakes the probe at 40%, where the probe already catches everything. It also roughly doubles the honest false-positive rate at 1% poison (6.9% versus 3.5%) and adds cost and complexity for no gain in backdoor lift.

In hindsight the reason is clear: the probe measures the thing we care about directly, by activating the backdoor behavior, whereas update direction is a proxy. At low poison rates the backdoor is a small part of the client's objective, so its update still points roughly where the honest updates point. The proxy degrades faster than the direct measurement.

**We are not adopting D4.** It is kept here as a documented, measured negative result.

## What this does not establish

This tests the natural adaptive strategy: poison less and stop scaling. It does **not** test a stronger adaptive attacker that explicitly optimizes against the defense, for example by adding a penalty for probe-slice error to its local loss, or by solving a constrained problem that maximizes backdoor effect subject to keeping suspicion under tau. That attacker is the real remaining frontier and is the most valuable next experiment. We are not claiming general adaptive-attacker robustness on the strength of this result.

Also unchanged: the base detector is still only moderately strong (honest spoofing recall about 0.55), and the setting is still IID with ten clients and two attackers.
