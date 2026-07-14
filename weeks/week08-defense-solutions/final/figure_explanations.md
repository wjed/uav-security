# Figure and Table Explanations: Final Defense

What each figure and table in `08_defense_final.ipynb` shows, the one-line takeaway, and why it earns a place in the paper. Figures are saved in `results/`. This is a candidate set; some overlap, and the overlap notes at the end say which are safe to cut.

## Figures

### 1. `trust_across_rounds_final.png` (attribution)
**What it is.** Trust weight assigned to each client on every FL round under the full defense. The eight honest clients are thin blue lines, the two attackers (C9, C10) are the bold red lines, and the dashed gray line marks uniform trust (1/N = 0.10).

**Takeaway.** Both attackers are driven to zero trust and stay there from the first round; honest clients hover at or above uniform. The defense does not just resist the attack, it identifies which clients are compromised.

**Why we have it.** This is the visual proof of attribution, which is the property coordinate-median alone cannot give. It is the figure that most directly shows the mechanism working, and it feeds the mitigation side of the project (knowing which UAV to act on).

### 2. `bsr_by_experiment_final.png` (headline result)
**What it is.** Backdoor Success Rate for all seven experiments (honest, attack, attack + inflation, median only, trust only, full defense, full defense vs inflation), with a dashed line at the honest baseline (0.66). Lower bars are better.

**Takeaway.** The attack pushes BSR well above the baseline; the full defense brings it back down to the baseline line, and the inflation variant lands in the same place.

**Why we have it.** It is the single figure that tells the whole attack-and-defense story at a glance, and it makes the accuracy-inflation immunity visible (the last two green bars are identical).

### 3. `lift_generalization_final.png` (generalization)
**What it is.** Backdoor lift for the CN0 trigger and the TCD trigger, each shown with no defense (red) versus full defense (green).

**Takeaway.** For both triggers the no-defense lift is large and the full-defense lift is near zero, even though the defense was never told the trigger switched to TCD.

**Why we have it.** This is the figure that answers the "what if the attacker avoids CN0" question. It is the strongest evidence that the defense is feature-agnostic, which is the main advance over v1 and v3.

### 4. `confusion_matrix_final.png` (utility check)
**What it is.** A 2x2 confusion matrix (authentic vs spoofed, true vs predicted) for the defended model on the clean test set, Blues colormap with counts.

**Takeaway.** The defended model still classifies normal traffic sensibly; it is not trading away clean performance to resist the attack.

**Why we have it.** It grounds the clean-accuracy and false-alarm claims in a concrete breakdown, and it is a standard, expected figure in a detection paper. It also pairs with the false-alarm discussion (the top-right cell is the false alarms).

### 5. `lift_by_experiment_final.png` (ablation)
**What it is.** Backdoor lift for the six non-baseline experiments, so each defense configuration is compared on the metric that matters (extra harm above honest).

**Takeaway.** Median-only leaves a small positive lift, trust-only removes it, and the full defense removes it while staying robust; inflation does not change the defended result.

**Why we have it.** It is the ablation figure: it shows that each layer contributes and that the combination is what you want. Lift is the honest metric, so this is arguably the most rigorous single comparison.

### 6. `sensitivity_poison_final.png` (robustness)
**What it is.** Backdoor lift under the full defense as the attacker's poison ratio varies across 30, 40, and 50 percent, with a dashed line at zero.

**Takeaway.** The defended lift stays flat and near zero across the whole range, so the result is not a lucky artifact of one poison setting.

**Why we have it.** It answers the "is this just tuned to one number" objection. It is a small figure but it buys a lot of credibility for little space.

## Tables (printed in the notebook)

- **Summary table** (clean accuracy, spoof recall, false alarm, BSR, lift per experiment): the numeric backbone of the whole results section. Everything else is a view of this.
- **False-alarm table** (honest vs attack vs full defense): supports the false-positive discussion; shows the defense does not inflate false alarms.
- **Trust-per-round table**: the numeric version of Figure 1, useful if a reviewer wants exact values.

## Overlap notes (to help trim)

- Figures 2 (BSR by experiment) and 5 (lift by experiment) tell the same story on two scales. If space is tight, keep **lift** (Figure 5) as the rigorous version and drop the raw-BSR bar, or keep the BSR bar for intuition and move lift into the table. Do not need both as full figures.
- Figure 3 (generalization lift) and Figure 5 (lift by experiment) both use lift bars; they are not redundant because Figure 3 is specifically the CN0-vs-TCD comparison, which is the generalization claim. Keep it.
- The strongest four if forced to choose: **1 (attribution), 3 (generalization), 5 (ablation lift), 6 (sensitivity)**, plus the summary table. Figure 2 and Figure 4 are nice-to-have intuition and utility checks.
