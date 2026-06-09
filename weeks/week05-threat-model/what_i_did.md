# Week 5 — What I Did and What I Learned
**Will Jedrzejczak — Threat Model Revision**

---

## What I Did

Revised and formalized the UAV threat model into a specific, technically grounded document (`threat_model.md`). The key shift from the prior version: instead of saying "FL detects attacks," the model now specifies *exactly* which attack, *exactly* which attacker, *exactly* how the attack interacts with the FL process, and *exactly* why it's hard to solve.

---

## The Threat Model in One Paragraph

A sophisticated adversary compromises one or two cluster head UAVs in a multi-UAV relay network. The compromised nodes execute a Grayhole attack — selectively dropping 30–60% of sensor data payloads to the ground base station while forwarding all control messages to avoid link-failure detection. Concurrently, they submit adversarially crafted FL model updates designed to suppress the global model's sensitivity to the Grayhole attack signature. The detection system (FL-based) is simultaneously the defense mechanism and the attack surface. The non-IID data distribution across UAV positions means honest clients far from the attacker have limited knowledge of the Grayhole pattern, which weakens the global model's coverage of that class even without poisoning.

---

## Why This Specific Threat Model

Dr. Hasan asked for something specific, practical, and challenging. The Grayhole + FL poisoning combination satisfies that because:

1. **Grayhole is genuinely hard to detect with thresholds alone** — partial packet dropping looks like congestion. Only behavioral feature modeling catches it.
2. **The non-IID FL setting makes it worse** — clients who don't see the attack can't help the global model learn it.
3. **Simultaneous attack + evasion hasn't been fully addressed in prior work** — most FL-IDS papers assume IID and don't model poisoning concurrent with the physical-layer attack.
4. **It directly maps to our existing code** — the DNN we built, the non-IID Dirichlet partitioning from the EDA, and the FedProx rationale all connect directly to this threat model.

---

## Connection to Prior Work

- **FedProx (Li et al., 2020):** We're already using this. The proximal term constrains client drift — this matters here because non-IID honest clients might pull the global model away from Grayhole sensitivity.
- **Grinsztajn et al. (2022):** Explains why RF > DNN on tabular data — relevant for the week 4 analysis and for understanding why we need the DNN specifically for FL (not because it's better, but because it can be federated).
- **Byzantine FL literature (Blanchard et al., 2017 — Krum; Yin et al., 2018 — median):** Byzantine-robust aggregation methods exist. The challenge is applying them when the "Byzantine" behavior is indistinguishable from legitimate non-IID updates.

---

## Dataset Limitation Acknowledged

WSN-DS is a proxy. The main gaps relative to this threat model: LEACH features don't map to UAV protocols, fixed topology doesn't model UAV mobility, and there's no FL poisoning component in the data. Plan: continue with WSN-DS for the detection task, generate synthetic poisoned updates in the FL simulation.
