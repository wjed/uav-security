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

## Round 2: reported issues, branding, and motion

Three things reported after the first QA pass, plus one nice-to-have.

- **The caption card could shift.** It used `min-height`, a guess that happened
  to cover every caption at the widths first tested. At other widths a longer
  sentence can wrap to a third line and the box grows past its floor: a real,
  if narrow, bug. Replaced the guess with a measurement: an offscreen probe
  carrying the same `.cap` class (so it inherits the exact width and
  breakpoint rules) is laid out with every step's text, the tallest result
  becomes a true fixed height, and it is remeasured on resize. Verified
  constant across all ten steps at 1280, 1000, 900, 770, and 390px.
- **The readouts popped in instead of fading.** They were toggled with
  `display:none -> flex`, which is instant by definition. Replaced with a
  CSS opacity and transform transition. (An earlier round had deliberately
  avoided this because a *JS-driven* rAF fade stalled under the tool used to
  QA the page, i.e. a hidden or virtual-time-budget browser pane does not
  composite frames; a plain CSS transition does not have that dependency and
  was confirmed to fade in smoothly under real wall-clock conditions.)
- **Branding.** The header now carries a "JMU Capstone" tag, the paper's full
  title, and all three names (Will Jedrzejczak, Cole Walther, Dilpreet Gill).
  Mobile drops the long formal title and keeps the tag and names.
- **Restrained motion.** Each drone idles with a small desynced vertical
  float (a few px, staggered per drone so the fleet does not bob in
  lockstep); the sending drone gets a brief pulse when its packet launches;
  the coordinator carries a soft breathing halo while it is actively running
  its exam. All of it is skipped under `prefers-reduced-motion: reduce`.

### A layout bug the fixes exposed

Adding the branding row made the header taller, which shrank `main`'s
available height. At one specific window size (1000x640) that was enough to
close a 2px gap between the bottom drone row and the caption card that had
never been a problem before. Fixed by shifting the whole landscape fleet
layout up inside the viewBox, which buys back clearance regardless of
exactly how the SVG ends up scaled, and reverified across the full width
range.

### A second collision, found only by sweeping the width range methodically

At intermediate window widths (roughly 761 to 1080px) the SVG stage renders
at a scale where the landscape fleet's left column can sit close enough to
the left edge to collide with the spacious left-column HUD; the HUD is fixed
CSS pixels while the stage scales continuously with width, so a single
breakpoint could not keep them apart everywhere. Fixed by giving the HUD its
own, wider breakpoint (1080px) for switching to the same compact top-row
style already used on phones, independent of the fleet's own portrait or
landscape breakpoint (760px). Confirmed clear at 1280, 1120, 1000, 900, 770,
and 390px.

### A tooling lesson worth recording

Headless Chrome's `--virtual-time-budget` and this tool's hidden preview pane
both freeze CSS transition and animation timelines at their starting value,
which made the HUD fade look permanently broken in-tool even though the CSS
was correct. Confirmed the CSS was right (inline `style="opacity:1"` was
also being ignored, and `getAnimations()` showed the transition stuck at
`playState: "running"` without progressing) and re-verified with a small
script that drives a real, persistent headless Chrome over the DevTools
protocol and waits in true wall-clock time before capturing: the fade
completes normally. Screenshots taken through a frozen timeline cannot be
trusted to show whether an animation finishes; only a live, composited
session can.

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
