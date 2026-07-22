# Week 12: IEEE Paper Draft

**Group 1 (Will Jedrzejczak, Cole Walther, Dilpreet Gill).**

This folder holds the completed IEEE paper draft (`main.tex`) and the figures it references. Every number in it comes from the executed notebooks in weeks 8 to 11; nothing is transcribed by hand or estimated.

## What is here

| File | What it is |
|---|---|
| `main.tex` | The full paper: all sections written, reconciled to the final 10-client / 2-attacker / 150k setup |
| `figures/fig_backdoor_and_trust_rounds.png` | Figure: backdoor progression and trust over rounds (from week 10) |
| `figures/fig_trigger_generalization.png` | Figure: lift before/after defense per trigger (from week 11) |
| `figures/fig_adaptive_attacker.png` | Figure: adaptive attacker (from week 11) |
| `figures/fig_defense_sensitivity.png` | Optional extra figure: beta/tau/EMA sweep (from week 10), not currently referenced |

## How to use this in Overleaf

1. Copy `main.tex` into your Overleaf project (it replaces your current `main.tex`).
2. Upload the four PNGs from `figures/` into your Overleaf `figures/` folder.
3. Keep your existing `references.bib` and your existing `figures/Threat_model_new.png`; the paper still uses both. All twelve `\cite` keys are the same ones your draft already used, so no bibliography changes are needed.

## What changed from the previous draft (read this before submitting)

The previous draft's abstract described the final experiments (10 clients, 2 attackers, 150k rows), but its body still described the earlier 5-client / 1-attacker / 75k design from Week 7, and Sections III to VII were placeholder stubs. This draft reconciles the whole paper to the actual final setup and fills in every section. Specifically:

- **Title.** Changed to the defense-framed title used on your presentation flyer: "Trigger-Agnostic Behavioral Trust for Backdoor-Resilient Federated GPS Spoofing Detection in UAV Networks." The previous title was attack-framed; the defense is the larger contribution and this matches what you have advertised. Revert if you prefer the attack framing.
- **Setup reconciled everywhere:** N=5 to N=10, one compromised client (U5) to two (U9, U10), 75k to 150k rows, trigger value 46.718 to 46.706 dB-Hz (the value from the 150k run), and the preprocessing/partition tables updated to match.
- **Lift baseline.** Defined consistently against the honest FedAvg baseline (0.6368), which is how every experiment in weeks 9 to 11 measures it. The previous draft's 48.02% centralized baseline is dropped, and the reason the honest baseline BSR is high (the trigger sits at the benign 75th percentile) is stated explicitly.
- **Sections III to VII written.** Methodology now presents the behavioral-trust defense with equations and a full algorithm block (Algorithm 1). Experimental Setup has the configuration table. Results has the three-seed ablation, trigger generalization, the adaptive attacker, false positives, and cost, each with the real figures. Discussion states the limitations honestly. Conclusion added.
- **Contributions list** rewritten from "we outline a planned evaluation" to the four contributions actually delivered, including the defense and the adaptive-attacker result. The FedProx comparison, which was never run, is removed from the claims.

## One number-consistency note

The paper uses the Week 11 re-execution numbers throughout for internal consistency: attack lift **+0.2457**, inflation **+0.3036**, defended lift **-0.0253**. Your presentation flyer and the previous abstract used the Week 10 numbers (+0.2415 and -0.0265). These are the same experiment run in two environments and agree within the standard-deviation bands; at the precision the flyer states them ("about 24 points, near the honest baseline") they are identical. If you want the flyer and paper to match to the last digit, update the flyer to 24.57, or tell me and I will switch the paper back to the Week 10 numbers. Either is defensible; they just need to be consistent in whatever you submit.

## Status

Complete draft, ready for your review and a compile in Overleaf. The one thing only you can confirm is the title-framing choice above.
