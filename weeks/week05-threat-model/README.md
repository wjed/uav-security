# Week 5: First Threat Model (pre-pivot)

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

This week defines the project's first formal threat model, written during the earlier WSN-DS phase and framed around a multi-UAV relay network with selective-forwarding attacks and FL model poisoning. It predates the Week 7 pivot to the GPS spoofing dataset and is kept as the record of how the threat model evolved.

## What this week did

Defined the system model (a two-tier UAV cluster network with a trusted ground base station acting as the FL aggregator), the adversary's capabilities and limitations, and the attack of interest (a compromised UAV poisoning its local data and manipulating aggregation). The core idea carried forward into the final work: a single compromised client can exploit the aggregation step, and self-reported metrics are a weak basis for trust.

## Files

| File | What it is |
|---|---|
| `threat_model.md` | The full system and threat model |
| `what_i_did.md` | Per-member contributions |

## How it maps to the final project

The final capstone keeps the essence of this threat model (one compromised FL client, aggregation as the attack surface, self-reported accuracy as the exploitable lever) but re-instantiates it concretely on the GPS spoofing dataset with a specific backdoor trigger and a server-side behavioral-trust defense. The formalized threat model in the paper draft is the direct descendant of this document. See the top-level `README.md` for the full arc.
