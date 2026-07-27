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

- **Next / Back** — step through ten stages at your own pace. Arrow keys work too.
- **Dots** — jump straight to any stage.
- **Auto** — advances every five seconds if you would rather let it run.
- **Restart** — back to stage one.

The narrative runs: the fleet, local training, updates going up, merging, two drones revealed as
compromised, what those two actually do, the backdoor landing, the coordinator switching to its own
exam, the two liars failing it, and finally their influence going to zero.

## Colours and icons

Official JMU palette only, on the light gold `#F4EFE1` background: `#450084` purple, `#CBB677` gold
and `#AD9C65` dark gold, the secondary purples `#B599CE` / `#DACCE6`, the grays `#333333` /
`#595959` / `#D6D6D6`, `#5F791C` green and `#A4232B` red. No emoji: the drone and ground-station
glyphs are inline SVG `<symbol>` definitions and the controls use inline SVG paths, so the page
stays one self-contained file with no external requests.

## Layout

Two stage layouts. Above 760px the fleet sits in a 5 by 2 grid under the coordinator. Below that a
phone squeezes those drones to an unreadable size, so the stage switches to a 2 by 5 portrait
arrangement with a taller viewBox, the readouts become a compact row across the top, and the
headline shortens. The layout re-checks itself on every render as well as on resize, because some
embedded viewers change size without firing a resize event.

## QA

The demo was checked by driving all ten steps at 1280px, 390px and 360px and asserting, at each
step: no horizontal overflow, no page scroll, no overlap between the caption card and anything on
the stage, no overlap between the readouts and the stage, a caption card of constant height, no
lowercase on-stage labels, and no em dashes anywhere. Things that pass are not interesting; these
are the ones that did not, and what they turned out to be:

- The caption card shifted a couple of pixels between steps whose text wrapped to two lines. Fixed
  with a fixed minimum height and centred content.
- The annotation pills collided with the caption on two steps, and the readout panel overlapped the
  leftmost drone. Both were real overlaps, found by the automated check rather than by eye.
- The readouts and the annotation pills faded in through `requestAnimationFrame`, which is paused
  whenever the tab is not painting, leaving them stuck invisible. Both now render opaque.
- The headline could overflow on a narrow screen depending on which font the device substitutes, so
  small screens get a shorter headline that cannot overflow at all.

One caveat on the screenshots used during review: headless Chrome substitutes a wider fallback font
than the real system stack, so captures exaggerate text width and show clipping that a live browser
does not. Geometry was therefore verified by measuring elements in a real browser rather than by
trusting the images.

## What is measured and what is not

The three figures in the corner are **measured**, read from
`week11-paper-tables/results/ablation_table.csv` (mean over seeds 42, 7, 123). The per-drone
influence bars come from `week10-validation/results/client_flagging_table.csv`.

The **stage sequence is choreography, not data.** We did not export a per-round trace, so the ten
stages narrate the mechanism and reveal the measured end-of-training outcome at the two points where
it matters: stage 7 (undefended) and stage 10 (defended). No intermediate values are invented.

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
