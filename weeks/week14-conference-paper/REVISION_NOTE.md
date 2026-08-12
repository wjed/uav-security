# Revision Note: Final Six-Page Version

**Paper:** Receiver-Domain Behavioral Probing for Backdoor-Resilient Federated GPS Spoofing
Detection in UAV Networks
**Authors:** Will Jedrzejczak, Cole Walther, Dilpreet Gill, Khalid Hasan

Seven pages to six by selection, not compression. Margins, font sizes and reference formatting are
unchanged.

## Technical corrections

1. **Chai et al. [4] verified against the source.** Their Section IV specifies that each client
   computes its accuracy on its own local validation set, forms the weight itself, and transmits
   it to the server, which applies it with no verification. Their Eqs. (18)-(20) are our Eq. (1),
   lambda and Eq. (2). Section II-A now says this and cites their equation numbers. (Their abstract
   says "standardized validation set," contradicting their own Section IV; we follow Section IV.)
2. **Trigger wording.** "In-distribution" removed. The modified feature lies within its own benign
   marginal range; we add that we do not claim the row is jointly in-distribution.
3. **Probe explanation corrected.** The paper no longer implies honest models label every probe row
   spoofed. Honest recall on a slice is well below one; the mechanism reads a feature-specific
   deficit relative to the cohort.
4. **Adaptive attacker softened** to the evasion objective actually tested, with an explicit note
   that we do not claim it holds for every defense-aware adversary.
5. **Attacker count** is now "no exact attacker count, assuming an honest majority" throughout.
6. **Krum terminology separated.** Table I daggers Krum and Multi-Krum as exclusion from the
   selected set; all other entries are client flagging. Section II-C defines both.
7. **One overhead figure**, 38.6 ms from Table I. The separate 34.0 ms timing run is removed.
8. **Weak detector.** Paired lift controls for baseline performance within the evaluated
   configuration; transfer to a better-converged detector is future work. The causal claim about
   the federated configuration is withdrawn, since its supporting numbers were cut.

An overclaim sweep of the compiled text (guarantee, prove, eliminate, always,
never, cannot, every defense) left only factual statements and two disclaimers.

## Cuts

| Section | Before | After |
|---|---|---|
| Experimental setup | preprocessing commentary | parameters only |
| Per-client attribution | one subsection | three sentences |
| Adaptive attacker, root set, parameters, cost | four paragraphs | one paragraph |
| Discussion and Conclusion | three paragraphs | **Conclusion**, 178 words |

No figure or table removed. Fig. 2 redrawn at one column keeping all five series. Fig. 1 is regenerated: the previous diagram set its labels smaller than the 8 pt caption beneath it and
wrote w and L where the equations use omega and f. It is now produced by `build_figures.py`
at the same type size as Figs. 2-4, with notation from Eqs. (1)-(7).

## Style

One pass over the manuscript removing tutorial framing, including "The message is not that...",
"Read from the inside out...", "Why two layers.", "This is the lever the paper is about." and
"We are deliberate about scope."

## Consistency and reproducibility

Every number in Table I and in the prose is checked against its exported CSV by script. Attack
parameters, seeds and defense settings appear once, in Section IV. 15 references, all cited,
markers [1]-[15] contiguous. All four figures are written at exactly the width they are placed at,
so LaTeX applies no rescaling. `14_conference_results.ipynb` executes with no errors and reproduces
Table I and Figs. 2-4 from the CSVs; `build_figures.py` regenerates all four figures. Abstract,
contributions, results and conclusion carry the same scoped claims.

**Not done:** the optional rerun with a better-converged detector. **To check before submission:**
volume and page ranges for the three references added this round, [8] Yin, [14] Kang, [15] Kairouz.
