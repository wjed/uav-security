# Revision Note: Final Six-Page Version

**Paper:** Receiver-Domain Behavioral Probing for Backdoor-Resilient Federated GPS Spoofing
Detection in UAV Networks
**Authors:** Will Jedrzejczak, Cole Walther, Dilpreet Gill, Khalid Hasan

Seven pages to six, by selection rather than compression. Margins, font sizes and reference
formatting are unchanged.

---

## 1. Technical corrections

**Chai et al. [4] verified against the source.** Their Section IV specifies that each client
computes its accuracy **on its own local validation set**, forms the normalized weight
$\lambda_n$ itself, and transmits $\lambda_n$ to the server, which applies it with no verification
step. Their Eqs. (18), (19) and (20) are our Eq. (1), $\lambda_i$ and Eq. (2). Section II-A now
states this and cites their equation numbers. The attack motivation is confirmed. One caveat worth
knowing: their abstract says "standardized validation set," which reads as a shared set and
contradicts their own Section IV; we follow Section IV, the concrete specification.

**Trigger wording.** "In-distribution" is gone. The paper now says the modified feature lies within
its own benign marginal range, and adds explicitly that we do not claim the row is jointly
in-distribution, since a sufficiently powerful joint density model could still separate it.

**Probe explanation corrected.** The paper no longer implies an honest model labels every probe row
spoofed. It states that recall on a slice is well below one even for honest clients, and that the
mechanism reads a feature-specific recall deficit *relative to the cohort*.

**Adaptive attacker softened.** Reported as a tradeoff for the evasion objective actually tested,
with an explicit statement that we do not claim it holds for every defense-aware adversary and that
formulations targeting the cohort statistics are untested.

**Attacker count.** "No exact attacker count, assuming an honest majority" in the abstract,
introduction, requirement R3, results and conclusion.

**Krum terminology separated.** Table I marks Krum and Multi-Krum with a dagger defined as
*exclusion from the selected set*; every other entry is *client flagging*. Section II-C defines both
and states they are not interchangeable.

**One overhead figure.** 38.6 ms from Table I, used everywhere. The separate 34.0 ms timing run and
the percentages derived from it are removed.

**Weak detector.** Paired lift controls for baseline performance within the evaluated
configuration; transfer to a better-converged detector is future work. The causal claim that the
weakness comes from the federated configuration is **withdrawn**, since the numbers supporting it
were cut.

**Overclaim sweep.** The compiled text was searched for absolute claims (*guarantee, prove,
eliminate, always, never, cannot, ensures, every defense*). All remaining instances are factual
statements about the protocol or setup; the two "every defense" occurrences are disclaimers.

## 2. Cuts to six pages

| Section | Before | After |
|---|---|---|
| Experimental setup | preprocessing commentary | parameters only |
| Per-client attribution | one subsection | three sentences |
| Adaptive attacker, root set, parameters, cost | four paragraphs | one paragraph |
| Discussion and Conclusion | 3 paragraphs | **Conclusion**, 178 words |

No figure or table was removed. Fig. 2 was redrawn at one column keeping all five series.
Fig. 1 was **regenerated** rather than shrunk: the previous diagram set its labels smaller than the
8 pt caption beneath it and wrote $w$ and $\mathcal{L}$ where the equations use $\omega$ and $f$.
The replacement is produced by `build_figures.py` at the same type size as Figs. 2-4 and takes its
notation from Eqs. (1)-(7).

## 3. Writing style

One pass over the whole manuscript. Removed "The message is not that...", "Read from the inside
out...", "Why two layers.", "This is the lever the paper is about." and "We are deliberate about
scope.", together with the surrounding tutorial framing.

## 4. Consistency and reproducibility

- Every number in Table I and in the running prose is checked against its exported CSV by script.
- Attack parameters, seeds and defense settings appear once, in Section IV.
- 15 references, all cited, markers [1]-[15] contiguous.
- All four figures are written at exactly the width they are placed at, so LaTeX applies no
  rescaling and the point sizes in the source are the ones that print.
- `14_conference_results.ipynb` executes end to end with no errors and reproduces Table I and
  Figs. 2-4 from the exported CSVs; `build_figures.py` regenerates all four figures.
- Abstract, contributions, results and conclusion carry the same scoped claims.

**Not done:** the optional rerun of the core benchmark with a better-converged federated detector.
**To verify before submission:** the bibliographic details (volume and page ranges) of the three
references added this round, [8] Yin et al., [14] Kang et al. and [15] Kairouz et al.
