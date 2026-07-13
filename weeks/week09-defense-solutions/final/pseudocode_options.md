# Pseudocode Options for the Methodology Section

The advisor wants the methodology represented with pseudocode and equations, in the style of an IEEE conference paper, so it reads as technical rather than as plain prose. This note gives a few options drawn directly from `09_defense_final.ipynb`, written in a form that maps cleanly to a LaTeX `algorithm` / `algorithmic` block. Pick the ones that fit the page budget; the recommendation is at the end.

## Notation (shared)

- $N$ clients $U_1,\dots,U_N$; the last two are compromised. $w$ is the global model.
- $T$ FL rounds, $E$ local epochs. $\mathcal{D}_i$ is client $i$'s local data.
- $\mathcal{D}_{\text{root}}$ is the server's small clean root set (carved from training).
- $F$ features; $F_{\text{probe}}$ is the discriminative subset used for probing.
- $v_f$ is the benign-high value of feature $f$ (its authentic 75th percentile).
- $S_f$ is a probe slice: spoofed root rows with feature $f$ overwritten to $v_f$.
- $a_i$ clean accuracy, $d_{i,f}$ per-feature detection recall, $s_i$ suspicion, $t_i$ trust.
- $\beta$ trust sharpness, $\rho$ trust EMA factor, $\gamma$ attacker boost, $p$ poison rate.

Key equations to display alongside the pseudocode:

$$s_i = \max_{f \in F_{\text{probe}}} \max\!\left(0, \frac{m_f - d_{i,f}}{\text{MAD}_f + \epsilon}\right), \qquad m_f = \operatorname{median}_i d_{i,f}$$

$$t_i = \frac{a_i \, e^{-\beta s_i}}{\sum_{j} a_j \, e^{-\beta s_j}}, \qquad w \leftarrow \operatorname{median}_i\big(w + N t_i (w_i - w)\big)$$

---

## Option A (recommended): the full defended round

This is the headline algorithm. It shows local training, the server-side behavioral trust, and robust aggregation in one place.

```
Algorithm 1  One federated round with the behavioral-trust defense
Input : global model w; clients 1..N; root set (X_root, y_root);
        probe features F_probe with benign-high values {v_f};
        sharpness beta; EMA rho; previous trust t_prev
Output: updated global model w

# clients (identical work whether or not the defense is on)
for each client i = 1..N do
    w_i <- LocalTrain(w, D_i, E)
    submit w_i to the server
end for

# server: score every client on its own held-out data
for i = 1..N do
    a_i <- Accuracy(w_i, X_root, y_root)
    for each f in F_probe do
        d_{i,f} <- Recall(w_i, S_f)          # S_f = spoofed root rows, feature f -> v_f
    end for
end for
for each f in F_probe do
    m_f   <- median_i d_{i,f}
    MAD_f <- median_i | d_{i,f} - m_f |
end for
for i = 1..N do
    s_i <- max_f  max(0, (m_f - d_{i,f}) / (MAD_f + eps))     # worst-feature anomaly
    t_i <- a_i * exp(-beta * s_i)
end for
t <- Normalize(t)
t <- rho * t + (1 - rho) * t_prev                            # smooth across rounds
if first round (all models near random) then t <- uniform    # safety guard

# robust aggregation of trust-scaled updates
w <- CoordinateWiseMedian_i ( w + N * t_i * (w_i - w) )
return w, t
```

## Option B: the behavioral-trust score on its own

If Option A is too dense, split the novel part into its own algorithm and let Option A call it as `t <- ServerTrust(...)`.

```
Algorithm 2  ServerTrust: feature-agnostic behavioral trust
Input : client models w_1..w_N; root set; F_probe with {v_f}; beta
Output: trust weights t_1..t_N

for i = 1..N do
    a_i <- Accuracy(w_i, X_root, y_root)
    for each f in F_probe do
        d_{i,f} <- Recall(w_i, S_f)
    end for
end for
for each f in F_probe do
    m_f <- median_i d_{i,f};   MAD_f <- median_i | d_{i,f} - m_f |
end for
for i = 1..N do
    s_i <- max_f max(0, (m_f - d_{i,f}) / (MAD_f + eps))
    t_i <- a_i * exp(-beta * s_i)
end for
return Normalize(t)
```

This is the block to emphasize as the contribution: it never reads a client-reported value, and it needs no knowledge of which feature is the trigger.

## Option C: the adversary (threat model as an algorithm)

Useful in the threat-model section to make the attack concrete and to justify why both defense layers exist.

```
Algorithm 3  Compromised client local step
Input : global model w; local data D_m; trigger feature f*; benign-high value v_{f*};
        poison rate p; boost gamma
Output: submitted update and reported accuracy

D' <- copy(D_m)
choose a p-fraction of the spoofed rows in D'
for each chosen row: set feature f* <- v_{f*};  set label <- authentic   # data poisoning
w_m <- LocalTrain(w, D', E)
w_m <- w + gamma * (w_m - w)                                             # model-replacement scaling
acc_report <- 0.99                                                       # accuracy inflation
submit (w_m, acc_report)
```

Pairing this with Option A makes the point cleanly: the scaling in line "w_m <- w + gamma(...)" is what the coordinate median defeats, and the mislabeled trigger rows are what the behavioral trust catches.

## Option D: probe-set construction (small helper)

Only worth a separate block if the reviewers ask how $F_{\text{probe}}$ and $\{v_f\}$ are built; otherwise fold two lines into Algorithm 2.

```
Procedure  BuildProbes
Input : root set (X_root, y_root); features F; separation threshold tau
Output: F_probe, benign-high values {v_f}, slices {S_f}

for each feature f in F do
    compute Cohen's d between authentic and spoofed on the training pool
end for
F_probe <- { f : Cohen_d(f) >= tau }          # drop near-zero-separation features only
for each f in F_probe do
    v_f <- 75th percentile of feature f among authentic rows
    S_f <- spoofed root rows with feature f overwritten to v_f
end for
return F_probe, {v_f}, {S_f}
```

## Recommendation

- For a 6-page conference version: include **Option A** (the full round) as the one methodology algorithm, and display the two key equations above next to it. That is the most technical-looking single block and it contains the novelty.
- If there is room for two algorithms: use **Option A + Option C** (defense and attack side by side), which reads very cleanly and motivates both defense layers.
- Keep **Option B** and **Option D** in reserve for a longer journal version, or fold them into A as sub-steps.
- Do not present any of this in plain prose only; the equations plus one boxed algorithm are what make the methodology look like a research contribution rather than a description.
