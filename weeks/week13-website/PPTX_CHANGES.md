# Slide-deck change list after the July 28 paper revision

**Deck:** `IT-445_ Trigger-Agnostic Behavioral Trust... _ Gill Jedrzejczak Walther.pptx` (30 slides)
**Why this exists:** the revision ran five new experiments, corrected two earlier claims and found a
real failure in the defense. The deck predates all of it. Three statements currently on the slides
are now contradicted by our own data, so this is not only a numbers refresh.

Changes are tiered. **Tier 1 must happen** or we will say something on stage that our own paper
disproves. Tier 2 is mechanical. Tier 3 is the new headline finding. Tier 4 is optional.

---

## TIER 1 -- Statements that are now FALSE. Fix these first.

### 1.1 Slide 16 title, and slide 12 bottom line
**Currently:** "Neither Layer Is Enough Alone. Together They Close It." and "Neither alone was
enough. Together they close it."

**Problem:** the reviewer explicitly told us to stop saying this, and our own numbers do not support
it. Trust-only reaches +0.0039 and the full defense −0.0265; at three seeds that difference is
inside the seed spread. We formally withdrew the claim in the paper.

**Replace slide 16 title with:** "Behavioral Trust Does Most of the Work. The Median Is a Backstop."

**Replace the slide 12 line with:** "Behavioral trust provides most of the measured protection.
Coordinate-wise median is retained as a robust backstop, and Section V-D shows where it earns that."

---

### 1.2 Backup slide (30), first bullet
**Currently:** "The base detector is weak... catches only about 53% of spoofed signals, **largely a
ceiling of this public dataset**."

**Problem:** we tested this and it is wrong. Trained centrally on the same features, our *own*
MLP reaches **0.907** recall and gradient boosting reaches **0.993**, against **0.529** federated.
The features are separable; our federated configuration underfits. Saying "dataset ceiling" on
stage is a claim a faculty member could disprove from our own appendix.

**Replace with:** "The base detector is weak: with no attack it catches only about 53% of spoofed
signals. We traced this and it is **our federated configuration, not the dataset**. The same
architecture trained centrally reaches 0.907 recall and gradient boosting reaches 0.993. Twelve
rounds of three local epochs on a small MLP underfits. Fixing it is the top next step."

---

### 1.3 Slide 24 -- "The Protection Is Essentially Free"
**Currently:** "37.4 ms", "1.1% of total round time", title "essentially free".

**Problem:** the 1.1% used a denominator that sums every client's training time. Real clients train
in parallel, so a round costs about the slowest client. On that denominator it is **3.40%**. Worse,
server cost is linear in fleet size while a parallel round is not, so the fraction climbs to
**34.9% at 40 clients**. We withdrew the scalability claim in the paper.

**Replace the four stat blocks with:**
- `13.0 KB` sent per drone per round (unchanged)
- `34.0 ms` added per round on the coordinator
- `3.40%` of a parallel round (and `0.98%` of a sequential simulation)
- `0` extra work on the client drones (unchanged)

**Change the title to:** "The Cost, on the Denominator That Actually Matters"

**Add a fourth bullet:** "Honest caveat: server cost grows with the fleet while a parallel round does
not, so the fraction rises from 5.6% at five drones to 34.9% at forty. We do not claim large-fleet
scalability, because we measured it and it does not hold."

**Speaker note to add:** "We reported 1.1% before. That divided by the sum of every drone's training
time, which is what a simulation does, not what a fleet does. Corrected, it is 3.4%, and it gets
worse as the fleet grows. We would rather say that than be asked it."

---

### 1.4 Slide 27 -- "In One Sentence"
**Currently:** "...and the attacker's advantage disappears." with `+0.246 → −0.025`, `1.1%`.

**Replace the sentence with:** "Two compromised drones out of ten can hide a blind spot in a shared
GPS spoofing detector while overall accuracy barely moves. We built a defense that judges each drone
on what its model does rather than what it claims, and **under evenly distributed data** the
attacker's advantage is reduced to a level statistically indistinguishable from an honest fleet."

**Update the three stat blocks:** `+0.242 → −0.027`, `100% / 0.3%` (unchanged), `3.4% added round
time, none of it on the drones`.

---

### 1.5 Slide 9 -- "The Obvious Defenses Each Miss Something"
**Problem:** we now know one obvious defense does *not* miss. Multi-Krum reaches +0.0061, which is
statistically indistinguishable from our behavioral trust at +0.0039, and it is 27x cheaper.
Presenting "the obvious defenses all fall short" is no longer accurate.

**Rewrite the third bullet as:** "Byzantine-robust rules like Krum and Multi-Krum work well here,
and we say so. But they must be told **how many** drones are compromised, and a real coordinator
does not know that. They also produce a selection, not a per-drone judgment, so they cannot tell you
*which* aircraft to ground."

---

## TIER 2 -- Number refresh (mechanical)

Every result is now produced by one shared harness, so the whole table moved slightly. **Slide 16
table, replace all seven rows:**

| Method | Clean accuracy | Spoofing caught | Attack success | Backdoor lift |
|---|---|---|---|---|
| Honest, no attack | 0.7112 | 0.5292 | 0.6367 | +0.0000 |
| Attack | 0.6932 | 0.3641 | 0.8782 | **+0.2415** |
| Attack, plus lying | 0.6897 | 0.3524 | 0.9402 | **+0.3036** |
| Median only | 0.7101 | 0.5008 | 0.7013 | +0.0646 |
| Trust only | 0.7112 | 0.5307 | 0.6406 | +0.0039 |
| Full defense | 0.7143 | 0.5560 | 0.6101 | **−0.0265** |
| Full defense, vs lying | 0.7143 | 0.5560 | 0.6101 | −0.0265 |

**Global find-and-replace across all slides and speaker notes:**

| Find | Replace |
|---|---|
| `+0.2457` / `+0.246` | `+0.2415` / `+0.242` |
| `−0.0253` / `−0.025` | `−0.0265` / `−0.027` |
| `0.7109` | `0.7112` |
| `0.5287` | `0.5292` |
| `0.6368` | `0.6367` |
| `0.8825` | `0.8782` |
| `0.0641` | `0.0646` |
| `0.0037` | `0.0039` |
| `0.7142` | `0.7143` |
| `0.5546` | `0.5560` |
| `0.6114` | `0.6101` |
| `37.4 ms` | `34.0 ms` |
| `1.1%` (round time) | `3.40%` |

**Slide 7** ("Why It Hides"): `0.7109 → 0.6928` becomes `0.7112 → 0.6932`; `0.6368 → 0.8825` becomes
`0.6367 → 0.8782`; "down 1.81 points" becomes "down 1.80 points".

**Slide 18** ("The Lie Has Nothing to Act On"): `+0.2457 → +0.3036` becomes `+0.2415 → +0.3036`.
The four "identical to the digit" values become `0.7143, 0.5560, 0.6101, −0.0265`. The point of the
slide is unchanged and still correct.

**Slide 22** (benchmark): FLTrust `+0.079` is still correct. `−0.027` replaces `−0.027`... (already
right). Add the cost line: "FLTrust also costs 168 ms per round against our 34, because it trains a
server model every round."

---

## TIER 3 -- The new headline finding. This needs a new slide.

The revision's most important result is **not** in the deck at all, and it is the one a reviewer
would ask about. Add **one new slide after slide 21 (False Alarms)**.

### New slide: "Where It Breaks: Uneven Data Across the Fleet"

**Body:**

> Every result so far assumes each drone sees a similar mix of signals. A real fleet does not.
> We tested what happens when drones hold different proportions of spoofed data.

| | Evenly split | Mild skew | Moderate skew |
|---|---|---|---|
| Attacker trust (fair share = 0.100) | **0.0001** | 0.0950 | 0.1025 |
| Compromised drones caught | **100%** | 0% | 0% |
| Backdoor lift, trust only | +0.0039 | **+0.2374** | **+0.2482** |
| Backdoor lift, full defense | −0.0265 | +0.0647 | +0.1002 |

**Three bullets:**
1. **The exam stops working.** Under skew the compromised drones get a normal share of trust and the
   detection rate falls to zero.
2. **Why.** Suspicion is measured against how much the fleet normally disagrees. When honest drones
   legitimately disagree more, the attacker's odd answer no longer stands out. It hides inside the
   fleet's own variation.
3. **The median backstop is what saves it.** Trust alone leaves the attack fully standing; the full
   defense holds it to +0.065. That is the layer we could not previously justify, earning its place.

**Speaker note:** "This is the result we least wanted and the one we are most glad we ran. Our
advisor asked for it specifically. Under evenly split data our exam is perfect. Under realistic
uneven data it stops firing entirely, because it judges each drone against how much the fleet
normally disagrees, and uneven data makes the fleet disagree more. We tested whether lowering the
threshold fixes it: it recovers part of the detection but never gets back to where it was, and it
starts flagging honest drones. So this is a real limitation, we know exactly why it happens, and
the fix is a per-drone measure instead of a fleet-wide one. That is our clearest next step."

### Also update slide 30 (backup) fourth bullet
**Currently:** "Ten drones, evenly split data, one receiver. Real fleets see different conditions
per aircraft, **which would stress the false-alarm behaviour most**."

**Replace with:** "Ten drones, one receiver. We tested uneven data directly and the trust layer stops
firing, so this is now a measured limitation rather than a suspected one. See the skew slide."

---

## TIER 4 -- Optional, if there is room

### 4.1 Strengthen slide 22 into a real comparison
We now have nine aggregation rules on one pipeline, not just FLTrust. If the slide can hold a small
table, it is a much stronger answer to "why is your method needed":

| Method | Backdoor lift | Server ms |
|---|---|---|
| FedAvg | +0.2415 | 1.0 |
| Accuracy-weighted FedAvg | +0.3036 | 1.3 |
| Coordinate-wise median | +0.0646 | 0.9 |
| Trimmed mean | +0.0787 | 1.4 |
| Krum | +0.0331 | 1.4 |
| Multi-Krum | +0.0061 | 1.4 |
| FLTrust | +0.0787 | 204.4 |
| **Trust + median (ours)** | **−0.0265** | 38.6 |

### 4.2 New optional slide: "When You Do Not Know How Many Are Compromised"
This is our strongest remaining differentiator and it is currently nowhere in the deck.

| True compromised drones | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Multi-Krum (told 2) | +0.0005 | +0.0061 | +0.1609 | **+0.2837** |
| Trimmed mean (told 2) | +0.0380 | +0.0787 | +0.2114 | **+0.2992** |
| **Ours (no such setting)** | −0.0142 | −0.0265 | −0.0172 | **+0.0114** |

**One line:** "Multi-Krum matches us only when it is told the right number of attackers. At four it
is back to no defense at all. Ours has no such setting to get wrong."

---

## What NOT to change

These slides are still correct and should be left alone: 1-6 (problem setup), 8, 10, 11 (mechanism),
13 (dead-zone, the 20.5% → 0.3% story is unchanged), 14, 15 (metrics), 17, 19 (trigger
generalization), 20 (adaptive attacker), 21 (false alarms), 23 (deployability), 25, 26, 28, 29.

Slide 20's "the attacker defeats itself" framing is good and survives; just change "survives a
defense-aware attacker" to "remains effective against the evasion objective we tested" if that
phrasing appears in the notes.

---

## Honest framing advice for the talk

The deck currently tells a clean success story. The revised paper tells a more careful one, and the
talk should match, because Dr. Hasan has read the revision and a faculty member may have too.

The strongest version of this talk is not "we built a defense that works." It is: **"we built a
defense, we tested it against eight published alternatives, and we found both where it wins and
where it breaks."** That is a harder story to tell in twenty minutes but it is far more defensible
under questioning, and finding your own weakness before a reviewer does is exactly what the review
was pushing for.

Three questions to be ready for:
- *"Isn't Multi-Krum just as good?"* Under evenly split data, yes, and we say so on the slide. It has
  to be told how many attackers there are; we do not, and at four attackers it fails while we hold.
- *"So it fails on realistic data?"* Under uneven data the trust layer stops firing and the median
  backstop carries it. We know the mechanism and the fix. That is why the skew slide is in the deck
  rather than left out.
- *"Your detector only catches half the spoofing."* Correct, and that is our federated setup, not
  the data. Centrally the same model gets 0.907. It is the top next step.
