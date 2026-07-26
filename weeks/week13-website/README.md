# Week 13: Interactive Visualization Site

**Group 1 (Will Jedrzejczak, Cole Walther, Dilpreet Gill).**

A single-page site that lets someone *operate* the experiment instead of reading about it. The
presentation deck explains the solution; this shows it. Every control switches the whole system into
a configuration we actually ran, and the numbers that appear are read from the exported CSVs.

The built page lives at **`index.html` in the repository root**, so GitHub Pages serves it directly.

## What is here

| File | What it is |
|---|---|
| `template.html` | The page itself: markup, styles, and interaction code, with a `/*__DATA__*/null` placeholder |
| `build_site.py` | Reads the result CSVs, injects them as JSON, writes `index.html` at the repo root |
| `cn0_distribution.json` | Precomputed CN0 histogram for the "why nobody notices" panel |

## Rebuilding

```bash
python weeks/week13-website/build_site.py
```

Run it after any experiment rerun. The site cannot drift from the results for the same reason the
paper and the weekly reports cannot: nothing is typed in by hand.

The builder refuses to write a broken page. It fails loudly on a missing data placeholder, on any
duplicate element `id`, and on any `id` the script reaches for that does not exist in the markup.
That last pair of checks exists because a duplicated `id="fleet"` (on both the `<section>` and the
drone grid inside it) silently wiped out an entire section during development: `querySelector`
returned the section, and writing into it destroyed the heading, the controls and the metrics.

## The five panels

1. **The fleet.** Toggle the attack, the accuracy lie, and four defense configurations. Ten drone
   cards show the influence the coordinator granted each one, and four metrics update. All seven
   reachable combinations map to a measured row of the three-seed ablation, named underneath so a
   viewer can check it. Switching to *Both (ours)* with the lie on produces numbers identical to the
   lie off, which is the accuracy-inflation result made tangible.
2. **Why nobody notices.** The real CN0 distribution for authentic and spoofed readings, with the
   trigger value marked. 25% of genuinely authentic readings sit at or above it, so there is no
   outlier to find.
3. **The mechanism.** Pick which feature the attacker hid the trigger in; watch the coordinator's
   eight probes, seven of which the backdoored model passes and one of which it fails. The mixed
   CN0+TCD trigger correctly fails two.
4. **Deployability.** Sliders for the penalty strength and the grace margin. The first is flat across
   a sixteen-fold range; the second has a visible knee.
5. **The adaptive attacker.** A slider from "not hiding" to "hiding hard", showing its influence
   climbing while its backdoor collapses, even undefended.

## Data provenance

Everything comes from files the notebooks wrote:

- `week11-paper-tables/results/ablation_table.csv` — the seven fleet states
- `week11-paper-tables/results/trigger_comparison.csv` and
  `week10-validation/results/trigger_generalization.csv` — the six trigger settings
- `week10-validation/results/sensitivity_{beta,tau,ema}.csv` — the sliders
- `week11-paper-tables/results/adaptive_attacker.csv` — the adaptive panel
- `week10-validation/results/client_flagging_table.csv` — per-drone trust weights
- `week11-paper-tables/results/parameter_table.csv` — which features are probed

Two honest notes are built into the page rather than hidden in a caption. The footer states that the
defended result is **indistinguishable from an unattacked model, not better than one**, and that the
base detector catches only about 53% of spoofed signals before any attack. The trigger panel says
"not recorded" rather than inventing a false-positive rate for the two settings where that column was
not logged.

## Publishing

`index.html` sits at the repository root. To serve it, enable GitHub Pages on the repository
(Settings → Pages → Source: deploy from branch, `main`, `/root`). `README.md` still renders normally
on the repository landing page; the two do not conflict.
