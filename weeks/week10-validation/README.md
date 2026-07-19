# Week 10: Validation, Reliability, and Paper-Quality Results

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

## Submit this

**`week10_final_report.pdf`** (5 pages). Plain-English summary and the adopted configuration on page 1, the correction note on page 2, the multi-seed table and client-flagging rates on page 3, the new paper figure on page 4, the defense-side sensitivity sweep and remaining limitations on page 5.

If the notebook is wanted as well, it is **`10_validation.ipynb`**. Everything in the report comes from that one notebook.

## Files

| File | What it is |
|---|---|
| `week10_final_report.pdf` | The submission |
| `10_validation.ipynb` | The notebook that produces every number and figure |
| `week10_correction_note.md` | Correction note (a listed deliverable) |
| `week10_summary.md` | Written summary of what changed (a listed deliverable) |
| `build_final_report_pdf.py` | Rebuilds the PDF from `results/` |
| `results/` | Exported CSVs and PNGs, written by the notebook |

## What this week did

Responds to the review on three fronts:

1. **Corrections.** Parameter count fixed (**3,329**, not 13,000, counted live). Root-set separation proven by hashing rather than asserted, which **found and fixed a real 1-row train/test leak**. Four overstated claims retracted.
2. **Reliability.** All main experiments rerun across **three seeds** (42, 7, 123) with mean and standard deviation, lift paired within-seed.
3. **A new paper figure and improved tables**, all line graphs with standard-deviation bands.

It also changed the defense. Measuring false positives properly showed the old gate flagged honest clients in **20.5%** of client-rounds, so a suspicion dead-zone was added. That configuration (**D2**: `beta = 1.0`, `tau = 2.0`) is now the default throughout, so the headline table and the recommended setting are the same thing.

## Headline numbers

| | Value |
|---|---|
| Attack backdoor lift | **+0.2415 +/- 0.0048** |
| With accuracy inflation | **+0.3036 +/- 0.0124** |
| Under the defense (D2) | **-0.0265 +/- 0.0174** (advantage eliminated) |
| Honest false-positive rate | **0.3%**, none driven to zero trust |
| Attacker detection | **100%** |

The strongest finding is that the dead-zone made the defense **insensitive to its own gate sharpness**: backdoor lift is flat and negative across a sixteen-fold range of `beta`, where without the dead-zone the same range degraded to **+0.1228**. The defense no longer needs careful tuning to stay safe.

**One claim deliberately not made.** D2 comes out marginally ahead of the honest baseline on all three metrics, but within the seed spread, so it is reported as indistinguishable from honest training rather than better than it.

## Reproducing

```
python -c "import nbformat"        # notebook runs top to bottom, no manual steps
python build_final_report_pdf.py   # rebuilds the PDF from results/
```

The notebook writes every table and figure into `results/`; the build script reads those files and embeds the saved figures, so the report cannot drift from the experiment.

## What is still open

1. **The base detector is weak** (honest spoofing recall about 0.53), partly a ceiling of this simplified dataset. Highest-value next improvement.
2. **No adaptive attacker.** Every attacker here is fixed. One that shapes its updates to stay under the dead-zone is untested and is the strongest remaining threat.
3. **Three seeds is few** for a standard deviation, and too few to resolve neighbouring settings in the sweeps.
4. **IID and small fleet** (ten clients, two attackers). Non-IID would stress the false-positive behaviour most.
