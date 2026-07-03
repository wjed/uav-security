# Week 8 -- Defense Solutions Proposal

**Will, Cole, Dilpreet**

Based on our Week 7 results and the Thursday meeting with Dr. Hasan.

---

## The Threat We Need to Defend Against

Our Week 7 experiment demonstrated a **two-part attack**:

1. **Data poisoning** -- Client 5 trained on CN0-triggered data, so its model weights carry a backdoor. Even under uniform FedAvg (where no fake accuracy is reported), the global model's backdoor success rate jumped from 48% to 74% -- a +26% lift.

2. **Accuracy inflation** -- Client 5 reports a fake validation accuracy of 0.99 to the aggregator (honest clients report ~0.61). Under accuracy-weighted aggregation, this bumps Client 5's weight from the uniform 0.200 to ~0.288, pushing the backdoor success rate to 76% -- a further +2% on top of the poisoning alone.

These two parts are distinguishable and can be defended against somewhat independently. Dr. Hasan noted in the Thursday meeting that accuracy inflation is the easier one to handle; the data poisoning part is the harder and more interesting problem.

---

## Defense Directions Considered

### 1. Aggregator-Side Validation Set (Server Holds Clean Data)

**What it does:** The server keeps a small held-out clean dataset. After each round, before committing the updated global model, it evaluates the candidate global model on this set. If global accuracy drops below a threshold, the round is rolled back or clipped.

**Why it helps with accuracy inflation:** If Client 5 is inflating its reported val accuracy, the server can independently verify model quality instead of trusting client reports. A suspicious gap between what a client claims and what the server measures flags that client.

**Why it does not fully solve the problem:** By the time the server evaluates, the poisoned weights have already been averaged in. The server would catch the degradation but not necessarily identify which client caused it. Also, the server having clean labeled data is an assumption that may not hold in real federated settings (which is exactly why federated learning exists -- the server does not have data).

**Fit for our project:** Medium. This is relatively straightforward and addresses the accuracy inflation threat directly. It was mentioned in the assignment brief and by Dr. Hasan. As a standalone defense it is not novel enough for a substantial contribution, but it could be the foundation layer on top of which something more interesting is added.

---

### 2. Verified Accuracy-Weighted Aggregation

**What it does:** The aggregator replaces client-reported accuracy with server-verified accuracy. Instead of taking Client 5's word that it got 0.99, the server evaluates each client's submitted model on the server-side validation set and uses that as the weight.

**Why it helps:** Directly kills the accuracy inflation attack. Client 5 cannot boost its own weight by lying, because its weight is computed from independent server evaluation.

**Limitation:** Still does not address the underlying data poisoning. Client 5's backdoor model weights still get averaged in at its honest (server-verified) weight. The BDR would drop somewhat (no more extra weight boost) but the backdoor would still be there. Also assumes the server has clean validation data.

**Fit for our project:** Good starting point, but not sufficient alone and not novel enough on its own.

---

### 3. Robust Aggregation (Coordinate-wise Median / Trimmed Mean / Krum)

**What it does:** Instead of averaging all client updates uniformly, the aggregator uses a statistic that is resistant to outliers.

- **Coordinate-wise median:** For each model weight, take the median across all clients' submitted values for that weight. An outlier client (Client 5) cannot drag the average far because the median is unaffected by extreme values.
- **Trimmed mean:** Drop the top and bottom k% of submissions per coordinate before averaging.
- **Krum / Multi-Krum:** Select the subset of client updates that are most similar to each other and discard outliers. Assumes the majority of clients are honest.

**Why it helps with data poisoning:** Client 5's backdoor updates are likely to be statistical outliers in certain weight dimensions (specifically the weights connected to CN0 inputs). Median or trimmed mean would suppress those outlier weights even without knowing which client is compromised.

**Published baseline concern:** Median and trimmed mean are well-studied defenses (Yin et al. 2018, Blanchard et al. 2017). Implementing them as-is would be a replication, not a novel contribution. Dr. Hasan specifically said the defense needs some degree of novelty and should be a substantial contribution.

**Fit for our project:** Robust aggregation is a strong candidate for the core mechanism, but we need to either (a) apply it in a domain-specific way tied to GPS spoofing, (b) combine it with something else in a novel way, or (c) analyze why standard robust aggregation may or may not work given our specific backdoor trigger design.

---

### 4. Gradient / Update Anomaly Detection

**What it does:** Before aggregation, compare each client's submitted weight update (delta from global model) to the other clients' updates. Flag updates that are statistically anomalous in magnitude or direction.

- Simple version: cosine similarity between Client 5's update and the mean of honest updates. A backdoor update that is trying to shift CN0-related weights will be directionally different.
- More sophisticated: compute L2 norm of each client's update, clip updates above a threshold (norm clipping), then aggregate.

**Why it helps:** The backdoor attack works by shifting specific weights. If Client 5's weight delta is much larger in magnitude or different in direction than the other four clients, that is a detectable signal.

**Limitation:** With 5 clients and 1 compromised, detection is feasible but tight. If the attacker is aware of the defense, they can make the poisoned update more subtle (lower learning rate, fewer local epochs) at the cost of a weaker backdoor. Arms-race dynamic.

**Fit for our project:** Good novelty potential, especially if combined with GPS domain knowledge (e.g., monitoring which input weights are shifting and whether they correspond to CN0, the known trigger feature).

---

### 5. Intermittent Probing / Challenge-Response (Will's Idea from the Meeting)

**What it does:** The server periodically sends clients a small challenge dataset -- a set of labeled samples the server has verified -- and asks the client to evaluate its local model on this challenge set and return the accuracy. The server checks whether the returned accuracy is consistent with what an honest model trained on clean data would achieve on that challenge set.

**Why this is interesting:** A compromised client's model will fail on a challenge set that contains backdoor-trigger samples (because the model has learned to classify trigger samples as benign, but the server knows their true label is spoofed). This can expose the backdoor even without the server knowing what the trigger looks like in advance.

**Novelty angle:** Standard probing approaches assume the server knows something about the attack. If the server's challenge set is constructed adversarially (e.g., samples with CN0 values near the boundary between benign and spoofed distributions), an honest model and a backdoored model will disagree on some fraction of those samples. The gap in challenge accuracy between honest clients and Client 5 would be a detectable signal.

**Limitation:** The challenge set needs to cover the trigger region. If the server does not know the trigger feature or value, constructing an effective challenge set is harder. In our case, CN0 is the trigger, and the server could construct challenges by sampling from the CN0 boundary region.

**Fit for our project:** High potential novelty. This is closely related to the aggregator validation set idea but reframed as a probing mechanism targeted at trigger regions. Dr. Hasan was interested in the validation set idea; this is a more targeted version of that.

---

### 6. Temporal / Round-to-Round Comparison

**What it does:** Track how each client's reported accuracy and submitted weights change round-to-round. A compromised client that is consistently inflating its accuracy or consistently pushing weights in the same direction across rounds will stand out over time.

**Why it helps:** Client 5 reports 0.99 every round while honest clients fluctuate naturally (they are actually improving, so their accuracy goes up but not stuck at 0.99). A client whose reported accuracy is suspiciously stable or suspiciously high across all rounds is worth flagging.

**Fit for our project:** Low standalone novelty. Temporal analysis is a general idea. But as a lightweight signal to combine with something else (e.g., trigger anomaly probing), it adds value.

---

## Recommended Direction

Based on the results, the meeting discussion, and the novelty requirement:

**Primary defense: Trigger-Region Probing combined with Coordinate-wise Median Aggregation**

The core idea:

1. The aggregator maintains a small challenge set constructed by sampling GPS rows from the CN0 boundary region (CN0 values within one standard deviation of the benign/spoofed decision boundary). These are the samples a backdoored model will misclassify.

2. Each round, before aggregation, each client's submitted model is evaluated on this challenge set. The server does not need to know the trigger value in advance -- it just needs to know that CN0 is the key discriminating feature, which is domain knowledge from the Aissou et al. dataset.

3. Clients whose challenge accuracy falls below a threshold relative to the other clients are flagged. Their weight updates are either excluded or heavily clipped before aggregation.

4. Median aggregation is used as the base instead of mean, providing a second layer of resistance against outlier updates from any non-flagged poisoned weights that slip through.

**Why this fits the novelty requirement:** Standard probing assumes the server knows the trigger. Standard median aggregation is well-studied. Combining them with GPS-domain knowledge (knowing CN0 is the critical feature, constructing the challenge set from that region) is a domain-specific adaptation that goes beyond directly applying a known defense. The framing of "boundary-region probing" as a trigger-agnostic detection mechanism is the novel angle.

**Why it addresses the two-part threat:**
- Accuracy inflation: client-reported accuracy is ignored; server-evaluated challenge accuracy replaces it.
- Data poisoning: poisoned clients are flagged by their failure on the challenge set and/or suppressed by median aggregation.

---

## What We Need to Implement

1. **Challenge set construction** -- sample from the CN0 boundary region of the clean test set. Concretely: rows where CN0 falls between the spoofed 75th percentile and the benign 25th percentile. This is the ambiguous zone where honest models and backdoored models will disagree the most.

2. **Per-round probing** -- after each client submits weights but before aggregation, load each client's model, evaluate it on the challenge set, compute challenge accuracy, compare to the group median challenge accuracy. Flag clients more than X standard deviations below the group.

3. **Adaptive weight clipping** -- for flagged clients, multiply their weight update by a scale factor (e.g., 0.1 or 0.0) before aggregation. For non-flagged clients, proceed with median aggregation.

4. **Comparison experiment** -- run the same four experiments from Week 7 but with this defense active. Measure: does Client 5 get flagged? Does BDR drop? Does clean accuracy recover?

---

## How We Measure Success

| Metric | Target |
|---|---|
| Backdoor success rate under defense | Should drop from 74-76% toward the honest baseline (~48%) |
| Clean accuracy under defense | Should stay near the no-poisoning FedAvg baseline (~72%) |
| Client 5 flagged per round | Should be flagged consistently from Round 1 |
| False positive rate (honest clients flagged) | Should be near zero |

The defense is working if BDR drops substantially while clean accuracy is preserved. A defense that drops BDR to 48% by also dropping clean accuracy to 50% is not useful.

---

## Advantages and Limitations

**Advantages:**
- Does not require the server to know the trigger feature value (46.76 dB-Hz) -- only that CN0 is the important feature
- Challenge set can be constructed from the training data distribution without additional labeling
- Two-layer defense (probing + median) is more robust than either alone
- Directly observable: we can report per-round flag status for Client 5

**Limitations:**
- Requires the server to have some domain knowledge (which features matter) -- this is a stronger assumption than pure robust aggregation
- With only 5 clients, the group statistics for flagging are noisy
- An adaptive attacker who knows about the challenge set could try to pass the challenge while maintaining the backdoor (harder but not impossible)
- The challenge set boundary region needs to be calibrated -- too narrow and it has low power; too wide and honest models also fail on it

---

## Notes from Dr. Hasan's Feedback

- Defense needs to be a **substantial contribution**, roughly ~50% of the main attack contribution
- "Some degree of novelty" -- cannot just implement an existing defense off the shelf
- He suggested looking at recent FL backdoor defense papers (post-2022) for ideas
- He was interested in the aggregator validation set idea as a starting point
- He wants each group member to brainstorm independently before Monday's meeting
- The temporal dataset angle he mentioned (GPS data changing over time) is a different direction -- worth noting but not our primary focus for this defense

---

## Monday Meeting Agenda

1. Each member shares their independently brainstormed defense ideas
2. Compare against this proposal -- what did we miss, what should be dropped
3. Select the defense to implement
4. Divide implementation: challenge set construction (Will?), per-round probing (Cole?), analysis and results (Dilpreet?)
5. Confirm what the Overleaf paper section needs to say about the defense

---

## Assignment Deliverables Reminder

**Part 1 (due soon):** Dataset and preprocessing report section for the Overleaf paper (3-4 pages). Will's contribution -- can build directly from what_i_did.md and the notebook progress report.

**Part 2:** Group defense proposal document (this file is the brainstorm for that -- the actual formal document will go in the Overleaf paper).
