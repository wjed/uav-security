# Week 14: IEEE Conference Paper (6-7 pages)

**Group 1 (Will Jedrzejczak, Cole Walther, Dilpreet Gill).**

The full manuscript rebuilt as a conference submission: **15 pages and 12 tables/figures becomes
~7 pages, 3 tables and 4 figures.** This was a rebuild around one research story, not a
compression; nothing was shrunk to fit.

**Paper title changed** to lead with the mechanism rather than the property:
*Receiver-Domain Behavioral Probing for Backdoor-Resilient Federated GPS Spoofing Detection.*

## Submit these

| Deliverable | File |
|---|---|
| Conference paper | `main.tex` (compile in Overleaf; IEEEtran `conference`) |
| Revision note | `week14_revision_note.pdf` |
| Figures | `figures/fig2..4_*.png` (600 dpi). Fig. 1 is your own diagram, in Overleaf |
| Code / notebook | `14_conference_results.ipynb` + the scripts below |
| Individual contribution statement | **Not written.** Every commit in this repo is under one name, so authorship cannot be reconstructed from history. The three of you need to write it. |

## The story the paper tells

Self-reported performance is an exploitable attack lever in federated UAV spoofing detection. We
propose receiver-domain behavioral probing, which lets the coordinator judge client models on
evidence it generates itself. Four result elements carry the argument, in order:

**attack validity → competitive comparison → key differentiator → limitation and generalization**

- **Table I** -- 10 methods, one pipeline, full width. Attack works (+0.2415), inflation makes it worse
  (+0.3036), median leaves +0.0646, FLTrust leaves +0.0787, **Multi-Krum is competitive**
  (+0.0061), ours reaches −0.0265 and attributes per client.
- **Fig. 2** -- true attacker count varies while Byzantine-robust rules stay at *f*=2. Multi-Krum
  degrades +0.0061 → +0.2837; ours has no such parameter and stays flat. This is the strongest
  differentiator.
- **Fig. 3** -- client class-ratio skew. The trust layer stops firing (detection 100% → 0%,
  attacker trust 0.0001 → 0.1023) and the median backstop carries the protection. The honest
  boundary, reported rather than hidden.
- **Fig. 4** -- four trigger settings, one fixed configuration, never retuned.

Three supporting subsections follow the four elements:

- **Table II** -- a defense-aware attacker. Evasion raises attacker trust toward the uniform share
  but destroys the backdoor doing it: undefended lift falls from +0.2457 to -0.4782.
- **Table III** -- per-client attribution. Attackers flagged 72/72 client-rounds at 0.000 trust,
  honest clients 1/288, and no honest client-round is ever driven to zero.
- **Root set, parameters, cost** -- a 10x smaller root set costs almost nothing; a 30%-corrupted
  one drops detection to 83.3%.

The paper explicitly does **not** claim dominance over every baseline, because Table I would
contradict it. That fairness is treated as a strength and used to motivate the real
differentiators.

## Reproducing

```bash
python run_all.py --list                        # stages and runtimes
python run_all.py baselines attackers noniid    # the reported experiments
python build_figures.py                         # regenerate the four figures
```

Or open `14_conference_results.ipynb` and set `RUN_EXPERIMENTS = True`.

The data split is fixed at seed 42 so the evaluation target never moves; federated randomness
varies over seeds 42, 7, 123. Runs are deterministic on a given machine.

## Files

| File | What it is |
|---|---|
| `main.tex` | The paper. Inline `thebibliography`, so it compiles in one pass with no BibTeX step |
| `build_figures.py` | Builds Figs. 2-4 as 600 dpi PNGs from `results/*.csv` |
| `build_notebook.py` | Generates the notebook, so its cells cannot drift from the scripts |
| `build_revision_note_pdf.py` | Renders `REVISION_NOTE.md` to PDF |
| `fl_common.py` | Shared harness: split, probes, model, attack, 9 aggregation rules, metrics |
| `fl_runner.py` | One federated run under any rule; separates true attacker count from assumed *f* |
| `exp_baselines.py` | Table I |
| `exp_attacker_count.py` | Fig. 2 |
| `exp_noniid.py`, `exp_noniid_diagnosis.py` | Fig. 3 and the dead-zone diagnosis |
| `results/*.csv` | Every reported value |

## Before submitting

1. **Compile `main.tex` in Overleaf** and check the page count. The estimate is ~7 pages; the
   assignment allows 6–7. If it spills onto an 8th page, delete the parameter-sensitivity
   paragraph in §V-G (the one about β and τ); it is the least load-bearing paragraph in the
   results and costs about a third of a column.
2. Upload the three PNGs from `figures/`. They are 600 dpi, well above the 300 dpi IEEE asks
   for line art.
3. **Rename your threat-model diagram to `fig1_threat_model.png`.** The uploaded name
   ("IT 445 Diagrams - Final Threat Model .png") has spaces and a space before the extension,
   which `graphicx` handles inconsistently. The paper references the clean name.
4. Write the individual contribution statement.

Studies the paper only summarises in prose (hyperparameter sweep, cost scaling, detector ceiling,
trust degradation, the failed Dirichlet partitioning) remain in
`weeks/week12-paper/` and are unchanged.
