# Revision Note: Full Manuscript to IEEE Conference Paper

**Paper:** Receiver-Domain Behavioral Probing for Backdoor-Resilient Federated GPS Spoofing Detection
**Group 1:** Will Jedrzejczak, Cole Walther, Dilpreet Gill

This was a rebuild around one story, not a compression. Nothing was shrunk to fit; sections were
removed, merged or rewritten based on whether they advance the argument a reviewer has to be
convinced by.

**Result:** 15 pages, 12 tables/figures, 25 subsections becomes ~7 pages, 3 tables and 4 figures,
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
| **Table I** (10-row comparison, full width) | Proves the attack works, inflation makes it worse, median and FLTrust leave residual lift, Multi-Krum is competitive, and ours attributes per client |
| **Table II** (adaptive attacker) | Answers the first question a reviewer asks of any trust mechanism: what if the attacker knows about it |
| **Table III** (per-client attribution) | The evidence behind the attribution claim, and the honest-false-flag cost of it |
| **Fig. 2** (unknown attacker count) | The strongest differentiator: existing rules need f, we do not |
| **Fig. 3** (heterogeneity) | The honest boundary, and the empirical justification for keeping the median backstop |
| **Fig. 4** (trigger generalization) | Supports the scoped claim that the trigger feature need not be known |
| **Fig. 1** (system/threat model) | The authors' own diagram, showing the three attack steps and the inflated weight path |
| **Algorithm 1** | Shortened from 20 lines to 11; the method is the technical center |

## Removed from the main paper

All of this remains in the repository artifact and is summarized in one or two sentences where it
matters.

- **Positioning table against related work** -- replaced by two compact paragraphs, per instruction
- **Layer-ablation table** -- subsumed by Table I, which contains the same conditions
- **Hyperparameter sweep** table and figure -- two sentences in §V-G
- **Trust-degradation table** -- one clause; its decisive case is now Fig. 3
- **Centralized detector-ceiling table** -- one paragraph in the Discussion limitations, keeping
  the five numbers that matter (0.907 centralised vs 0.529 federated, 0.974 deeper, 0.993 boosted,
  0.224 logistic) and the argument that lift is unaffected by where the baseline sits
- **Cost scaling plots** and the two-denominator table -- two sentences in §V-G
- **Adaptive-attacker figure** -- the table is kept as Table II, the figure is not
- **Feature-separability table** (10 rows) -- replaced by two sentences giving the range (*d* =
  0.306 down to 0.152 probed, 0.018 and 0.001 excluded)
- **False-positive breakdown table** -- folded into the honest-false-flag column of Table I and the
  per-client rows of Table III
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
- **Results**: reorganised so each subsection maps to exactly one element. §V-A to §V-D carry the
  four elements above; §V-E to §V-G restore the adaptive attacker, per-client attribution and
  root-set stress as full subsections rather than the single compressed paragraph they had been
  reduced to.
- **Discussion and Conclusion**: merged into one section.

## Presentation pass

- Every table and figure label is in Title Case, and the cryptic column heads of the first draft
  ("Recall / BSR / Lift / Detect / ms/rd") became two-line headers that name the quantity
  ("Spoofing Recall", "Backdoor Lift", "Attacker Detection", "Server (ms/Round)").
- Table I moved to a full-width `table*`. It now carries clean accuracy, the standard deviation on
  lift, the honest false-flag rate, and the two rules that had been relegated to a sentence (Krum
  and trimmed mean), so nothing in it is "omitted for space" any more.
- The figures were rebuilt from scratch rather than patched; see **Figures** below.
- Every value in Tables I, II and III is checked against its exported CSV by a script, so a
  hand-typed table cannot drift from the run that produced it.

## References

12, down from 12 -- the count was already in range, but two were re-verified against source during
the previous revision and the dataset citation was corrected to the Mendeley *Unmanned Aerial
System* release (`10.17632/z7dj3yyzt8.3`), which matches the data actually used. The bibliography
is now inline (`thebibliography`) rather than BibTeX, so the paper compiles in one pass with no
`.bbl` step.

## Figures

Figures 2 to 4 rebuilt at publication quality and exported as **600 dpi PNG**, twice the 300 dpi
IEEE asks for line art. The first draft put all three at one column width, which crushed five
overlapping series into 3.4 in and stacked Fig. 3's two panels vertically. The rebuild:

- **Figs. 2 and 3 span the full text width.** They carry the two arguments a reviewer has to be
  convinced by, and they were the two that looked cramped. Fig. 3's panels now sit side by side.
- **Fig. 2 labels its five lines directly at the right** instead of carrying a legend. A legend
  with five entries is a second lookup for the reader and was eating a third of the plot height.
  Labels that would collide are pushed apart automatically and keep a leader line to their curve.
- **Fig. 3(b) uses twinned axes**: attacker detection on the left, attacker trust on the right,
  with the uniform share of 0.100 drawn in. The point of the panel is that one collapses exactly
  as the other rises, and that is now one picture rather than two numbers in a caption.
- **Fig. 4** marks the region at or below an honest fleet, so "defended lift is negative" is
  visible rather than something the reader has to work out from the axis.
- Nothing is set below 8 pt, grids are horizontal only and stop before the label gutter, markers
  carry a white edge so overlapping points stay separable, and legend handles are proxies without
  the error-bar caps that `errorbar()` puts in by default.
- **Each PNG is written at exactly the width it is placed at**, so LaTeX never rescales it. This
  was a real bug: `bbox_inches='tight'` crops the unused margin, so the files came out 6.01, 7.18
  and 3.21 in wide and were then stretched to `\textwidth`/`\columnwidth` by 1.19x, 1.00x and
  1.09x. The same 9.4 pt axis label was therefore reaching the page at 11.2, 9.4 and 10.2 pt in
  the three figures, and Fig. 2's was larger than the 10 pt body text. `save()` now measures the
  crop and re-saves until the width is exact.
- Table column gutters were opened up (`tabcolsep` 4 to 7 pt on Table I) after measuring each
  table's natural width in Times at 8 pt: Table I needs 475 pt of the 516 pt available, so the
  columns had no reason to be tight.
- Consistent colour role across figures: red = attack/undefended, green = proposed, purple =
  Multi-Krum and (in Fig. 3b) attacker trust, blue = FLTrust, grey = median. No colour means two
  different things inside one figure.

Figure 1 is the authors' own diagram rather than a generated one. It shows the three attack steps
and, importantly, the path by which the inflated self-reported accuracy drives the aggregation
weight toward its maximum, which is the specific vulnerability the paper targets.

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
| `figures/fig2..4_*.png` | Figs. 2-4 at 600 dpi. Figs. 2-3 are full text width, Fig. 4 one column; Fig. 1 is supplied by the authors |
| `build_figures.py` | Regenerates Figs. 2-4 from the CSVs |
| `14_conference_results.ipynb` | Executed notebook reproducing Tables I–III and Figs. 2–4 |
| `fl_common.py`, `fl_runner.py` | The shared harness (split, model, attack, 9 aggregation rules, metrics) |
| `exp_*.py`, `run_all.py` | The experiments behind the reported results |
| `results/*.csv` | Every reported value, exported |

Reproduce with `python run_all.py baselines attackers noniid` then `python build_figures.py`, or
set `RUN_EXPERIMENTS = True` in the notebook.
