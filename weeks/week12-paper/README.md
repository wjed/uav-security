# Week 12: IEEE Paper Draft

**Group 1 (Will Jedrzejczak, Cole Walther, Dilpreet Gill).**

This folder holds the completed IEEE paper draft (`main.tex`) and the figures it references. Every number in it comes from the executed notebooks in weeks 8 to 11, or from the two self-contained scripts in this folder; nothing is transcribed by hand or estimated.

## Revision for the advisor's Week 11 review (read this first)

The Week 11 meeting raised three things about the paper. All three are addressed here.

**1. "Comparing with the nearest benchmark is slightly underdeveloped."** This was the main
request, and it was tied to ICC review: a reviewer will check whether the defense was compared
against published work rather than only against our own ablation. FLTrust (Cao et al., NDSS 2021)
is the right benchmark because it shares this paper's premise, that the server should bootstrap
trust from a small clean root set rather than believe a client's self-report. It is now
reimplemented on our own pipeline (`fltrust_benchmark.py`) and reported as **Section V-B** with its
own table and figure. Both defenses get the identical model, updates, root set, attack and seeds, so
the comparison isolates the scoring rule.

The result is favorable and, more usefully, explainable. FLTrust is not a straw man: it removes
about two-thirds of the attack. But it leaves **+0.0787** of backdoor lift where ours reaches
**-0.0265**, and its clean accuracy and recall land *below* the honest no-attack baseline because
its magnitude normalization throttles honest clients too. The mechanism is the interesting part:
FLTrust scores a client by the cosine similarity of its whole update against the server's, and only
40% of each attacker's spoofed rows are poisoned, so most of the attacker's gradient is ordinary
learning and the backdoor occupies a small subspace of a 3,329-parameter vector. A global direction
statistic barely moves. It gives the attackers 0.039 trust, about 39% of uniform, where our
behavioral probe gives them 0.0001. Same information, more specific question.

**2. "The novelty claim is not that aggressive or well demonstrated."** Added **Table I**, a
positioning matrix against all seven related works across the properties that matter (UAV setting,
adversarial client, self-report as an attack lever, server-side root of trust, per-feature
behavioral probe, per-client attribution). No prior row is filled in on every column. The
introduction now states the first-to claim explicitly rather than leaving it implied, and the
contributions list gained the benchmark item.

**3. "Our biggest weakness is the dataset."** Two changes. The paper now *characterizes* the
dataset instead of only conceding it: **Table III** gives per-feature Cohen's *d* for all ten
features, which also justifies the probe threshold that was previously asserted. That turns out to
be a strong point rather than a weak one, because the weakest probed feature (PD, 0.152) sits nearly
an order of magnitude above the strongest excluded one (PQP, 0.018), so the threshold is not a
knife-edge choice. The limitations section was then rewritten from an apology into a scoped
argument: the claim under test is a property of the aggregation rule, not of the signal domain, and
reporting backdoor *lift* against each seed's own honest baseline is what makes it invariant to
detector strength. The honest remaining gap, stated as such, is that a second independent signal
domain would be the real test.

**A bibliography problem worth knowing about.** The version of `references.bib` previously in this
folder had two entries carrying the literal text `journal = {VERIFY: venue unknown}`, which compiles
straight into the reference list. That is fixed. Two further corrections were made to the verified
file: the dataset DOI did not resolve and pointed at the wrong one of two similarly named Aissou
releases (the repo's data folder matches the Mendeley *Unmanned Aerial System* release,
`10.17632/z7dj3yyzt8.3`, not the IEEE DataPort *Autonomous Vehicles* one), and the `mcmahan2017`
entry had a nested-brace bug that would have rendered the last author's name differently from every
other author. Both are commented at the entry in the `.bib`.

Separately, `chai2025navigation` is now verified rather than assumed, which matters because it is
the source of the accuracy-weighted design the entire attack targets. Its published abstract states
that "an accuracy-weighted aggregation strategy is introduced, dynamically assigning weights based
on the detection performance of each client mode", so the paper's characterization of it is
accurate.

### Reproducing the two new results

```bash
cd weeks/week12-paper
python fltrust_benchmark.py          # Section V-B: table, figure, raw npz (~10 min, CPU)
python dataset_characterization.py   # Section III-D: per-feature Cohen's d (~30 s)
```

Both re-derive the data split from the same fixed seed (42) used everywhere else, so they do not
depend on the notebooks having been run. The federated runs are deterministic: repeated executions
on the same machine reproduce bit-identically, which is how the Section V-B rows were confirmed
against the Week 11 ablation.

## What is here

| File | What it is |
|---|---|
| `main.tex` | The full paper: all sections written, reconciled to the final 10-client / 2-attacker / 150k setup |
| `figures/fig_backdoor_and_trust_rounds.png` | Figure: backdoor progression and trust over rounds (from week 10) |
| `figures/fig_trigger_generalization.png` | Figure: lift before/after defense per trigger (from week 11) |
| `figures/fig_adaptive_attacker.png` | Figure: adaptive attacker (from week 11) |
| `figures/fig_defense_sensitivity.png` | Figure: beta/tau/EMA sweep (from week 10), used by Section V-D |
| `figures/fig_fltrust_benchmark.png` | Figure: comparison against FLTrust, used by Section V-B |
| `figures/Threat_model_new.png` | Figure: system and threat model. Generated by `make_threat_model_fig.py` |
| `make_threat_model_fig.py` | Rebuilds the threat-model figure |
| `fltrust_benchmark.py` | Runs the FLTrust comparison (Section V-B). Self-contained: re-derives the split, runs all four methods over three seeds |
| `dataset_characterization.py` | Computes the per-feature Cohen's *d* table (Section III-D) |
| `results/fltrust_benchmark.csv` | Table V-B, exported |
| `results/fltrust_raw.npz` | Per-seed raw values and per-round trust, so the figure can be restyled without a rerun |
| `results/feature_separability.csv` | Table III-D, exported |
| `references.bib` | Bibliography for the 12 `\cite` keys |

## How to use this in Overleaf

1. Copy `main.tex` into your Overleaf project (it replaces your current `main.tex`).
2. Upload the four PNGs from `figures/` into your Overleaf `figures/` folder.
3. **If your Overleaf project already has `references.bib` and `figures/Threat_model_new.png`, keep yours.** They are the originals; the copies in this folder were added only so the paper compiles from a clean checkout of this repo, which it previously could not do (see below). All twelve `\cite` keys are unchanged.

## What changed from the previous draft (read this before submitting)

The previous draft's abstract described the final experiments (10 clients, 2 attackers, 150k rows), but its body still described the earlier 5-client / 1-attacker / 75k design from Week 7, and Sections III to VII were placeholder stubs. This draft reconciles the whole paper to the actual final setup and fills in every section. Specifically:

- **Title.** Changed to the defense-framed title used on your presentation flyer: "Trigger-Agnostic Behavioral Trust for Backdoor-Resilient Federated GPS Spoofing Detection in UAV Networks." The previous title was attack-framed; the defense is the larger contribution and this matches what you have advertised. Revert if you prefer the attack framing.
- **Setup reconciled everywhere:** N=5 to N=10, one compromised client (U5) to two (U9, U10), 75k to 150k rows, trigger value 46.718 to 46.706 dB-Hz (the value from the 150k run), and the preprocessing/partition tables updated to match.
- **Lift baseline.** Defined consistently against the honest FedAvg baseline (0.6368), which is how every experiment in weeks 9 to 11 measures it. The previous draft's 48.02% centralized baseline is dropped, and the reason the honest baseline BSR is high (the trigger sits at the benign 75th percentile) is stated explicitly.
- **Sections III to VII written.** Methodology now presents the behavioral-trust defense with equations and a full algorithm block (Algorithm 1). Experimental Setup has the configuration table. Results has the three-seed ablation, trigger generalization, the adaptive attacker, false positives, and cost, each with the real figures. Discussion states the limitations honestly. Conclusion added.
- **Contributions list** rewritten from "we outline a planned evaluation" to the four contributions actually delivered, including the defense and the adaptive-attacker result. The FedProx comparison, which was never run, is removed from the claims.

## Two files this folder was missing

`main.tex` referenced `figures/Threat_model_new.png` and called `ibliography{references}`, but neither file was committed. A clean checkout of this repo therefore could not compile the paper: the figure was unresolvable and all twelve citations rendered as `[?]` with an empty reference list. Both are now present.

- `references.bib` supplies all twelve keys. Seven are standard, widely cited works and are complete. **Five are marked `% VERIFY` in the file** and must be checked against the sources you actually read before submission, in particular `chai2025navigation` and `udin2025federated` (2025 works that could not be confirmed here, and `chai2025navigation` is load-bearing: it is the source of the accuracy-weighted design the whole attack targets) plus the dataset entry `aissou2022dataset`. **Do not submit an unverified citation.** If your Overleaf `.bib` is already correct, use that one instead.
- `figures/Threat_model_new.png` is generated by `make_threat_model_fig.py`. If you have an existing hand-drawn version in Overleaf, prefer it; this one exists so the repo builds standalone.

## Number consistency

Resolved. Week 10's notebook was re-run but its report and markdown deliverables were never regenerated, so they still quoted the pre-rerun figures (+0.2415, -0.0265) while weeks 11 and 12 used the current ones. Week 10's deliverables have been rebuilt from its own CSVs, so **weeks 10, 11 and 12 now agree**: attack lift **+0.2457**, inflation **+0.3036**, defended lift **-0.0253**. If your presentation flyer still says "+0.2415" or "24 points", update it to match.

## IEEE review pass

The paper was reviewed against normal IEEE conventions and the following were changed:

- **Added Section V-D, Defense-Side Sensitivity**, with Table VII and Fig. 5. The three-knob sweep was the strongest unused result in the repository: with the dead-zone in place, backdoor lift is flat and negative across a sixteen-fold range of the gate parameter, which is a deployability claim (the defense does not need careful tuning) on top of the security claim. Integrated into the Discussion and Conclusion, and the limitations now note that the sweep is one-parameter-at-a-time and therefore local rather than global.
- **Fixed a wrong cross-reference.** The threat model pointed at "Section V-D" for the adaptive attacker, which is Section V-C. All hard-coded section numbers are now `ef` to labels, so inserting a subsection cannot silently break them again.
- **Referenced the threat-model figure in prose.** It was an orphan float, which IEEE style does not allow.
- **Escaped bare `%` characters** in the new content. In LaTeX these comment out the rest of the line and would have broken the table rows.
- **Added an Artifact Availability statement**, standard for this kind of paper, noting that every number is read from an exported CSV rather than transcribed.

Every quantitative claim in `main.tex` is checked against the exported CSVs by an automated audit: the ablation, trigger, adaptive and sensitivity tables, the false-positive counts, the parameter count, the preprocessing arithmetic, and the derived prose claims ("less than two points", "a quarter of the attack", "lift +0.09 to +0.25"). All pass.

## Status

Complete draft, structurally sound, all numbers verified against the data. Two things still need a human:

1. **Verify the five `% VERIFY` bibliography entries** before submitting. This is the one blocking item.
2. **Title framing** (defense-framed vs attack-framed), as described above.
3. **Compile it once in Overleaf.** No LaTeX toolchain was available where these edits were made, so the paper has been validated structurally (environments, braces, math mode, tabular column counts, every float referenced, every cite key defined) but not actually built.
