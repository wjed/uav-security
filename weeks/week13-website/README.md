# Week 13: Live Demo

**Group 1 (Will Jedrzejczak, Cole Walther, Dilpreet Gill).**

A one-screen animation of the attack and the defense. Press play and watch twelve federated rounds:
drones train, updates fly up to the coordinator, and either the backdoor lands or the coordinator's
exam catches the two liars and pins them at zero influence.

The deck explains the work. This just shows it. No scrolling, three controls, about twenty seconds
to watch.

Built page: **`index.html` at the repository root**, served by GitHub Pages.

## What is here

| File | What it is |
|---|---|
| `template.html` | The demo: markup, styles, SVG stage and animation, with a `/*__DATA__*/null` placeholder |
| `build_site.py` | Reads the result CSVs, injects them as JSON, writes `index.html` at the repo root |
| `cn0_distribution.json` | CN0 histogram, precomputed from the raw dataset (kept for reuse; the current demo does not draw it) |

## Rebuilding

```bash
python weeks/week13-website/build_site.py
```

Run it after any experiment rerun. The outcome figures come from the exported CSVs, so the demo
cannot drift from the results.

The builder refuses to emit a broken page. It fails on a missing data placeholder, on any duplicate
element `id`, and on any `id` the script reaches for that does not exist. Those guards exist because
a duplicated `id="fleet"` on both a `<section>` and the grid inside it silently destroyed a whole
section during development: `querySelector` returned the section, and writing into it wiped the
heading, controls and metrics with no console error.

## Controls

- **Play / Pause / Restart** — steps through twelve rounds, four phases each.
- **Attack Off / On** — whether drones 9 and 10 are compromised.
- **Coordinator defense Off / On** — whether the behavioral-trust exam runs before merging.

Watch for: with the defense **off**, the red packets merge straight in and the backdoor lands. With
it **on**, the coordinator pulses gold while probing, both liars flash red, and their influence bars
collapse to nothing in the first round.

## What is measured and what is not

The three figures in the corner are **measured**, read from
`week11-paper-tables/results/ablation_table.csv` (mean over seeds 42, 7, 123). The per-drone
influence bars come from `week10-validation/results/client_flagging_table.csv`.

The **round-by-round timing is choreography, not data.** We did not export a per-round trace, so the
animation paces the twelve rounds evenly and shows the measured end-of-training outcome. The header
says so on the page rather than leaving it implied.

Two honesty details are built into the display:

- The raw "triggered signals waved through" rate is shown next to **an honest model's own rate
  (63.7%)**. Without that, 61% under the defense looks alarming, when in fact it is the unattacked
  baseline: the trigger value sits inside the ordinary safe range by design, so even a clean model
  misses many of these. The attacker's *gain* is the meaningful number, which is why it is the
  largest one on screen.
- Trust bars show an equal 0.100 share whenever the trust layer is inactive, because that is what
  plain averaging actually does, rather than implying the coordinator scored anyone.

## Publishing

`index.html` sits at the repository root. Enable GitHub Pages (Settings → Pages → Source: deploy
from branch, `main`, `/root`). `README.md` still renders on the repository landing page; the two do
not conflict.
