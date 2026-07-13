# False Positives in the Defense: Why the Score Matters, and How We Handle It

A false-positive score is something our evaluation should speak to directly, because in a security system it is half the story. This note explains what a false positive means in our setting, why reporting it (in the right form) is good, why we do not report a plain binary false-positive rate, and what we report instead.

## 1. Two different "false positives" in this project

They are easy to confuse, so we separate them:

- **Defense-level false positive:** the trust mechanism wrongly distrusts an *honest* UAV, treating a good client as if it were compromised and down-weighting or excluding its update.
- **Detector-level false positive (false alarm):** the trained model labels an *authentic* GPS signal as spoofed.

Both matter, but for different reasons, and they are measured differently.

## 2. Why having a false-positive score is good (the case for)

1. **Recall alone is misleading.** "We catch the attackers" or "we catch the spoofing" is only useful if we are not also punishing honest nodes or raising constant false alarms. A system with perfect recall and terrible precision is useless in practice. The false-positive score is how we prove we did not buy detection at the cost of wrecking normal operation.

2. **It answers the question an evaluator actually asks.** For the *defense*, the key worry is "does your trust mechanism harm honest UAVs?" A false-positive number is the direct answer. Without it, the defense's benefit is unquantified on the cost side.

3. **The operational cost is real in the UAV scenario.** A detector false alarm is not free: it triggers a mitigation action (rerouting traffic, switching coordinator, dropping a link). A defense false positive is not free either: wrongly distrusting an honest UAV throws away a legitimate, useful data source and can slow or degrade the shared model. Quantifying false positives quantifies the cost of deploying the system.

4. **It makes our claims auditable.** "No honest client is ever suppressed" is a crisp, checkable statement. A false-positive score turns a qualitative reassurance into a number a reviewer can verify.

5. **It is expected at a security venue.** Reviewers look for precision, specificity, or a false-positive rate (often as a confusion matrix). Not reporting it invites the criticism that the result is one-sided.

## 3. Why we do not report a plain binary false-positive rate (the case against, given our design)

Our earlier notebooks (v1, v3) used a **binary hard flag**: each round a client was either flagged or not, and a flagged client's update was clipped. In that design a false positive is clean and countable ("honest client flagged": yes or no), and we reported zero of them.

The final defense deliberately replaced the hard flag with a **continuous trust score** (every client gets a weight between 0 and 1). That changes the picture:

1. **A binary false-positive rate presupposes a hard accept/reject decision, which we no longer make.** Nobody is ever hard-rejected, so forcing a binary rate would require inventing an artificial threshold that the design specifically avoids. The metric would be measuring a decision the system does not take.

2. **A continuous scheme bounds the cost of a mistake.** If an honest client looks slightly off for one round, it is only mildly down-weighted, not excluded. The "damage" of a soft false positive is a small, temporary weight reduction, not a thrown-away client. Reporting a binary "false positive" would make a gentle, recoverable down-weight look like a hard false accusation, which misrepresents the mechanism.

3. **The full trust distribution is more informative than one number.** Showing every client's trust weight per round shows two things at once: that attackers are driven down, and that honest clients are not. A single false-positive percentage collapses that and hides the margin.

## 4. What we report instead, and what it shows

Under the full defense, per round:

- Both attackers are driven to **exactly 0.000** trust every round.
- Honest clients average about **0.125** (uniform trust is 1/N = 0.10).
- The lowest honest client sits around **0.01**, persistently below its peers but **never zeroed**.

Read as a false-positive statement, this says: **no honest client is ever excluded** (the defense-level false-positive count is effectively zero), and the separation between the worst honest client (about 0.01) and an attacker (exactly 0.000) is unambiguous. We are honest about one wrinkle: a single honest client is consistently down-weighted more than the others. It is never suppressed to zero and it does not hurt clean accuracy or recall, but it is a mild false-positive *tendency* rather than a perfectly clean separation, and we list it in the limitations.

## 5. Recommendation

Keep the continuous trust design, but report two explicit numbers so the false-positive question is answered outright rather than left implicit:

1. **Defense-level (honest suppression) rate.** State it directly, for example "honest clients ever suppressed below half of uniform trust: 0 of 8, across all rounds and both trigger cases." This is the continuous-design equivalent of a false-positive rate and it is already true in our runs; it just needs to be printed, not inferred from the trust table.

2. **Detector-level false-alarm rate (specificity).** On the clean test set, report the fraction of authentic signals wrongly labeled spoofed. This is the operationally meaningful number for the mitigation side, because it maps to how often the system would trigger an unnecessary response. We currently report clean accuracy and spoofing recall but not this rate; it is a one-line addition.

We should **not** retrofit a binary flag onto the final defense just to produce a false-positive rate, because that would misrepresent how the mechanism actually works. Define the false-positive-equivalent in trust-weight terms instead.

## 6. One-line summary

A false-positive score is worth having because a defense that also punishes honest UAVs (or a detector that cries wolf) is not deployable; we do not use a binary false-positive rate because our defense uses continuous trust rather than hard flags, so we instead report that no honest client is ever suppressed (defense-level) and recommend adding a false-alarm rate on the clean test set (detector-level) as the operationally meaningful companion number.
