# Revision Note: Full Manuscript to Six-Page Conference Paper

**Paper:** Receiver-Domain Behavioral Probing for Backdoor-Resilient Federated GPS Spoofing Detection
**Group 1:** Will Jedrzejczak, Cole Walther, Dilpreet Gill

This was a rebuild around one story, not a compression. Nothing was shrunk to fit; sections were
removed, merged or rewritten based on whether they advance the argument a reviewer has to be
convinced by.

**Result:** 15 pages, 12 tables/figures, 25 subsections becomes ~6 pages, 1 table and 4 figures,
12 references. The title changed to lead with the mechanism rather than the property, since the
mechanism is the contribution.

---

## The story the paper now tells

Self-reported performance is an exploitable attack lever in federated UAV spoofing detection. We
propose receiver-domain behavioral probing, which lets the coordinator judge client models on
evidence it generates itself. Four result elements carry the whole argument, in order:

**attack validity → competitive comparison → key differentiator → limitation and generalization**

Everything that did not serve that chain was cut.

---

## Retained, and why

| Element | Why it stays |
|---|---|
| **Table I** (8-row comparison) | Proves the attack works, inflation makes it worse, median and FLTrust leave residual lift, Multi-Krum is competitive, and ours attributes per client |
| **Fig. 2** (unknown attacker count) | The strongest differentiator: existing rules need f, we do not |
| **Fig. 3** (heterogeneity) | The honest boundary, and the empirical justification for keeping the median backstop |
| **Fig. 4** (trigger generalization) | Supports the scoped claim that the trigger feature need not be known |
| **Fig. 1** (system/threat model) | Redrawn; carries the three attack steps compactly |
| **Algorithm 1** | Shortened from 20 lines to 11; the method is the technical center |

## Removed from the main paper

All of this remains in the repository artifact and is summarized in one or two sentences where it
matters.

- **Positioning table against related work** -- replaced by two compact paragraphs, per instruction
- **Layer-ablation table** -- subsumed by Table I, which contains the same conditions
- **Hyperparameter sweep** table and figure -- one sentence in §V-E
- **Trust-degradation table** -- one clause; its decisive case is now Fig. 3
- **Centralized detector-ceiling table** -- two clauses in the Discussion limitations
- **Cost scaling plots** and the two-denominator table -- two sentences in §V-E
- **Adaptive-attacker table and figure** -- three sentences in §V-E
- **Feature-separability table** (10 rows) -- replaced by the phrase "eight satisfy *d* ≥ 0.05"
- **False-positive breakdown table** -- folded into the 0.3% figure in Table I and §V-A
- **Failed Dirichlet experiment** -- cut entirely; the working partition is described in one sentence
- **Preprocessing table** and per-step row counts -- reduced to two sentences
- **Round-progression, sensitivity and FLTrust-only figures** -- the tables carry the same numbers

## Rewritten rather than trimmed

- **Abstract**: 340 → 192 words. Problem, attack, idea, one attack number, one defense number, one
  differentiator, one scope sentence. Multi-Krum stays because it frames the differentiator; the
  adaptive attacker, cost, trigger sweep and false-positive rate are all out.
- **Introduction**: ~1,900 → 617 words. Related work compressed from four paragraphs of per-paper
  summary into one gap paragraph and one FLTrust-positioning paragraph. Contributions cut from five
  bullets to three.
- **System and threat model**: the three attack steps are now labeled A1–A3 and expressed with
  symbols, with one equation each where it earns one.
- **Results**: reorganised so each subsection maps to exactly one of the four elements.
- **Discussion and Conclusion**: merged into one section.

## References

12, down from 12 -- the count was already in range, but two were re-verified against source during
the previous revision and the dataset citation was corrected to the Mendeley *Unmanned Aerial
System* release (`10.17632/z7dj3yyzt8.3`), which matches the data actually used. The bibliography
is now inline (`thebibliography`) rather than BibTeX, so the paper compiles in one pass with no
`.bbl` step.

## Figures

All four rebuilt at publication quality and re-exported as **vector PDF** rather than PNG:

- single IEEE column width (3.4 in) so none needs a full-width float
- 6.5–8.5 pt type, legible at print size
- consistent colour role across figures (red = attack/undefended, green = proposed, purple =
  Multi-Krum, blue = FLTrust, grey = median)
- Fig. 1 redrawn from scratch: the previous version had annotations colliding with the uplink
  arrows and text overflowing its panel. The diagram, threat model and defense now occupy reserved
  bands that cannot overlap.

## One thing we did not do

The paper does **not** claim the proposed method dominates every baseline, because our own Table I
would contradict it. Multi-Krum is statistically indistinguishable from behavioral trust alone
under the nominal IID setting and costs far less server time. That result is stated plainly in the
abstract, in §V-A and in the Conclusion, and is then used to motivate the two properties that do
distinguish the method: no attacker-count parameter, and per-client attribution.

## Deliverables in this folder

| File | What it is |
|---|---|
| `main.tex` | The paper, IEEEtran `conference` class, inline bibliography |
| `figures/fig1..4_*.pdf` | The four figures, vector, publication quality |
| `build_figures.py` | Regenerates all four from the CSVs |
| `14_conference_results.ipynb` | Executed notebook reproducing Table I and Figs. 2–4 |
| `fl_common.py`, `fl_runner.py` | The shared harness (split, model, attack, 9 aggregation rules, metrics) |
| `exp_*.py`, `run_all.py` | The experiments behind the reported results |
| `results/*.csv` | Every reported value, exported |

Reproduce with `python run_all.py baselines attackers noniid` then `python build_figures.py`, or
set `RUN_EXPERIMENTS = True` in the notebook.
