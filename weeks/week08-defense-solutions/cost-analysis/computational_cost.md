# Computational Cost Analysis: Week 8 Final Defense

All numbers below were measured by `cost_analysis.py` on the exact pipeline in `final/08_defense_final.ipynb` (10 clients, 2 attackers, 150k-row sample, 12 FL rounds, 3 local epochs, batch 512). Re-run `python cost_analysis.py` from this folder to regenerate.

## 1. Environment

| Item | Value |
|---|---|
| OS | Windows-11-10.0.26200-SP0 |
| CPU | Intel64 Family 6 Model 158 Stepping 13, GenuineIntel |
| Logical cores | 16 |
| Torch threads | 8 |
| Python | 3.12.4 |
| PyTorch | 2.12.0+cpu |
| Device | CPU |
| RAM (total) | 34.3 GB |

## 2. Model and communication cost

Federated learning ships model weights, not data, so the model size *is* the per-message communication cost.

| Metric | Value |
|---|---|
| Trainable parameters | 3,329 |
| Model size (float32) | 13.0 KB |
| Forward FLOPs per sample (approx) | 6,658 |
| Messages per round | 20 (10 downloads + 10 uploads) |
| Communication per round | 0.27 MB |
| Communication per full run (12 rounds) | 3.20 MB |

The defense changes none of these: it adds no extra messages and does not change the model, so the communication cost of the defended system is identical to plain FedAvg.

## 3. Wall-clock timing (measured)

Per-round and per-client figures are derived from the two real 12-round runs, so they are consistent with the totals (they are not separate warmup-biased measurements).

| Phase | Time |
|---|---|
| Dataset load + preprocess (one time) | 54.0 s |
| Local training, per client per round | 328.5 ms |
| One FL round (10 clients + aggregation) | 3285.8 ms |
| Full experiment, undefended (12 rounds) | 39.4 s |
| Full experiment, full defense (12 rounds) | 40.0 s |

Local client training dominates the round. The two full runs land within run-to-run timing noise of each other, so the defense's added time is not even distinguishable at the full-run level; Section 4 isolates it directly. The whole notebook runs ~14 such experiments plus the data load, which is why end-to-end it lands in the low tens of minutes on a laptop CPU.

## 4. Where the defense cost goes (server side only)

The defense runs entirely on the aggregator. Every client does the exact same local training whether or not the defense is on, so **the defense adds zero computational cost to the UAVs**. The only extra work is on the server, per round:

| Server-side step | Time per round |
|---|---|
| Plain FedAvg aggregation (baseline) | 1.1 ms |
| Coordinate-wise median aggregation | 0.8 ms |
| Behavioral-trust probing | 37.3 ms |
| Trust probing + update scaling | 37.6 ms |
| **Server-side overhead added by the defense (vs FedAvg)** | **37.4 ms** |

The defense adds about **37.4 ms** of server work per round on top of plain aggregation (probing + update scaling + median, minus FedAvg). Against a ~3285.8 ms round that is about **1.1% of round time**. This is measured in isolation with repeated timing; differencing the two full 12-round runs (Section 3) gives a number smaller than run-to-run noise, which is consistent with an overhead this small. The probing is cheap because it is forward-pass only, on a tiny model, against a small server-held root set.

## 5. Memory

| Metric | Value |
|---|---|
| Total process footprint (RSS) | 544 MB |
| Per-round allocation churn (models + buffers, tracemalloc) | 1.0 MB |

The process footprint is dominated by the in-memory dataset, not the defense: a full defended round allocates only about 1.0 MB of transient model/buffer memory. It fits comfortably on a student laptop.

## 6. Algorithmic complexity

Let N = clients, P = model parameters, F = probe features, R = root-set size, E = local epochs, |D_i| = client i data size.

| Component | Per-round cost | Changed by defense? |
|---|---|---|
| Client local training | O(E x |D_i| x P) | No (identical with or without defense) |
| Server: FedAvg | O(N x P) | baseline |
| Server: coordinate median | O(N log N x P) | added |
| Server: behavioral-trust probing | O(N x (R + F x R) x P) forward-only | added |
| Communication | O(N x P) | No |

The added server terms scale linearly in the number of clients and features and only involve cheap forward passes, so the defense stays practical as the fleet grows. The dominant cost everywhere is client training, which the defense never touches.

## 7. Takeaways

- **Tiny model, tiny messages.** 3,329 parameters = 13.0 KB per update; 3.20 MB of total communication for a full 12-round run.
- **The defense is free on the drones.** It is entirely server-side; clients do identical work either way.
- **The server overhead is small.** About 37.4 ms extra per round (~1.1% of round time, below run-to-run noise at the full-run level), because probing is forward-only on a small model.
- **It scales gracefully.** Added cost is linear in clients and features; client training remains the bottleneck.

*Absolute times depend on the CPU in Section 1; the ratios (defense overhead vs training, communication per round) are the portable numbers.*