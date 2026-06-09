# Threat Model: Selective Forwarding Attack with FL Model Poisoning in UAV Relay Networks
**IT 445 / IT 499 Capstone — Week 5**
**Group A: Will Jedrzejczak, Cole Walther, Dilpreet Gill**

---

## System Model

### Network Topology

We model a multi-UAV relay network deployed for a time-sensitive mission — disaster response search-and-rescue is the motivating scenario. The network consists of 8–12 UAVs operating over a geographically distributed area of approximately 10×10 km. UAVs are organized into a two-tier cluster structure inspired by LEACH but adapted for aerial mobility:

**Member UAVs (6–9 nodes)**
Each member UAV carries a sensor payload (camera, thermal imager, or environmental sensor). Member UAVs collect local sensor data and transmit it to their assigned cluster head UAV. They also serve as FL training clients — each maintains a local copy of the attack detection model (`AttackDetectorDNN`) and trains it on the network traffic features it directly observes (message counts, forwarding behavior, energy patterns analogous to WSN-DS features). Member UAVs have constrained compute and battery; they run a small number of local training epochs per FL round.

**Cluster Head UAVs (2–3 nodes)**
Cluster head UAVs aggregate data from their assigned member UAVs and relay it to the Ground Base Station (GBS). In the FL context, cluster heads are also FL clients — they have larger local datasets because they observe all intra-cluster traffic in addition to their own. Cluster head status rotates in practice (re-election every N rounds) but at any given time 2–3 nodes hold this role.

**Ground Base Station (GBS) / FL Aggregator**
A fixed ground installation that serves two roles: (1) mission data sink — receives all forwarded sensor data from the cluster heads, and (2) FL server — receives model weight updates from all UAV clients each round, runs the FedAvg or FedProx aggregation, and broadcasts the updated global model back to all clients. The GBS is assumed to be physically secure and trusted. The UAV nodes are not fully trusted.

### Communication Links

- **Intra-cluster (member → cluster head):** 802.11p or proprietary RF at 2.4/5 GHz, range 2–5 km, half-duplex. Observable by any node within range.
- **Cluster head → GBS:** Long-range directional link (900 MHz or dedicated UAV link), range up to 30 km. Observable by a passive adversary with appropriate equipment.
- **FL model updates:** Piggybacked on the existing uplink (cluster head → GBS) during low-traffic windows. Compressed weight tensors, not raw data.

### Where FL Happens

Each UAV maintains a local `AttackDetectorDNN` (17 input features, hidden layers [128, 64, 32], 5-class output). Once per FL round (approximately every 10 minutes of operation):
1. Each UAV trains its local model for 3 epochs on its locally observed traffic data
2. Each UAV sends only its model weight updates (not raw traffic) to the GBS
3. The GBS aggregates with FedProx (μ = 0.1) to account for the non-IID traffic distribution across UAV positions
4. The GBS broadcasts the new global model to all clients
5. Each UAV switches to the updated global model for local inference

---

## Threat Model

### Attack Type

**Coordinated Selective Forwarding Attack (Grayhole Variant) with Concurrent FL Model Poisoning**

This is a two-layer attack: the attacker simultaneously executes a Grayhole data-plane attack to degrade mission effectiveness and a gradient-based model poisoning attack on the FL process to suppress detection.

### Attacker

**Profile:** A sophisticated adversary — state-level actor, organized criminal group, or competitor — who has compromised exactly one or two cluster head UAVs. Compromise is achieved through one of: (a) physical capture and firmware replacement of a UAV, (b) software supply chain attack injecting malicious code before deployment, or (c) exploitation of an unpatched vulnerability in the UAV's communication stack. The attacker has full software-level control over the compromised node(s) from within the network.

**Knowledge:** The attacker knows the system uses FL for intrusion detection (white-box assumption — they can observe the FL protocol traffic). They know the detection model architecture (it is broadcast to all clients). They can observe the global model parameters each round by participating normally in the FL protocol before initiating the attack.

### Attacker Goal

1. **Primary:** Degrade mission effectiveness by selectively dropping 30–60% of high-priority sensor data payloads destined for the GBS, while maintaining the appearance of normal network operation.
2. **Secondary:** Prevent the FL-based detection system from flagging the compromised nodes by poisoning local model updates to suppress sensitivity to the Grayhole attack signature.
3. **Persistence:** Maintain the attack for as long as possible without triggering either the FL detector or any threshold-based rule (e.g., link-failure alarm).

### Attacker Capabilities

- Full control over 1–2 cluster head UAVs (software-level, not physical link control)
- Ability to selectively drop, delay, or modify data packets before forwarding
- Ability to craft arbitrary local model update vectors before submitting to the GBS aggregator
- Ability to observe the current global model parameters each FL round
- Knowledge of the FL aggregation algorithm (FedAvg or FedProx)
- Ability to tune the drop rate dynamically based on observed network conditions

### Attacker Limitations

- Cannot compromise more than k ≤ 2 of n ≥ 8 nodes (Byzantine fraction < 25%, below the threshold for Byzantine-robust aggregation to guarantee safety)
- Cannot break the cryptographic integrity of the GBS communication link
- Cannot directly access or manipulate the GBS aggregation server
- Cannot control all FL clients simultaneously — honest clients still submit correct updates
- Must maintain plausible-looking behavior: fully ceasing forwarding (Blackhole) would trigger immediate link-failure detection; the attack must look like congestion

### Part of the UAV System Affected

- **Data plane:** Sensor payloads on the cluster head → GBS link. Control and ACK messages are forwarded normally to avoid link-failure detection.
- **FL training plane:** The compromised node's local model update, submitted to the GBS aggregator once per FL round.
- **Mission outcome:** Incomplete or degraded sensor data reaching the GBS degrades situational awareness. In a disaster response scenario, missed thermal imagery could mean missed survivors.

### Attack Execution (Step by Step)

1. **Setup phase (rounds 1–5):** Compromised cluster head operates normally, building a behavioral baseline and learning the global model's current sensitivity to Grayhole features.
2. **Attack initiation (round 6+):** Begin selective forwarding — drop 40% of sensor payloads to GBS while forwarding all ACK, JOIN, and control messages normally. The 40% rate produces detectable mission data loss but mimics moderate RF congestion.
3. **Model poisoning (concurrent with attack):** On each FL round, instead of submitting the correct local model update, submit an adversarially crafted update that nudges the global model's Grayhole classification weights toward the Normal class. Specifically, scale down the gradient contributions for Grayhole-discriminating features (`Data_Sent_To_BS`, `dist_CH_To_BS`) to reduce the model's sensitivity to the partial-forwarding signature.
4. **Evasion adaptation:** Monitor changes in the global model each round. If the model appears to be recovering sensitivity, increase poisoning magnitude. If link-failure thresholds are being approached, temporarily reduce the drop rate.

### Why This Threat Model Is Challenging and Unique

**1. Grayhole mimics congestion.**
A 40% packet drop rate is indistinguishable from moderate RF interference using threshold-based detection. Rule-based systems (drop rate > X%) would need a very low threshold to catch it, which would produce excessive false positives under legitimate congestion. Only a model trained on behavioral features (forwarding patterns, energy usage, advertisement counts) can distinguish the two — and that is exactly what this project provides.

**2. Non-IID data degrades the very defense being relied upon.**
UAVs in zones far from the compromised cluster head observe mostly Normal traffic or different attack patterns. Their local FL updates have limited information about the Grayhole signature. Under FedAvg, these honest-but-uninformed clients dilute the global model's Grayhole sensitivity over time. This means the attack actively degrades the defense's effectiveness even before the poisoning component kicks in.

**3. The FL protocol is simultaneously the detection mechanism and the attack surface.**
Most existing work treats the network attack and the FL security problem separately. In this threat model, the attacker exploits the same communication channel used for detection (FL updates) to suppress that detection. A defender who applies Byzantine-robust aggregation (e.g., coordinate-wise median) to protect against poisoning must do so in a way that does not throw away legitimate updates from honest non-IID clients — a known open problem in the literature (Karimireddy et al., 2021 showed that Byzantine robustness and non-IID convergence are in fundamental tension).

**4. The attack is below single-node detection thresholds but above mission-tolerable degradation.**
The attacker tunes the drop rate to stay below the threshold that would trigger rule-based alerts while still causing meaningful mission data loss. This "gray zone" between "definitely attacked" and "definitely congested" is exactly the space where a learned model operating on behavioral features (vs. a simple rate monitor) provides value.

**Prior work does not address this combination.**
FL-based IDS papers (e.g., Rey et al., 2022; Nguyen et al., 2019) typically assume IID data and do not model the interaction between data-plane attacks and model poisoning. UAV security papers (e.g., Yaacoub et al., 2020) address physical-layer and routing attacks but rarely incorporate FL as the detection mechanism. The non-IID FL setting with simultaneous attack + evasion over UAV relay topology has not been studied together.

---

## Dataset Discussion

WSN-DS is our current working dataset. It contains the Grayhole class and provides the 5-class behavioral feature structure we need. The main limitations relative to this threat model are:

- **LEACH ≠ UAV relay protocol.** WSN-DS features like JOIN_S, SCH_S, SCH_R, Rank, and send_code are LEACH-specific. A real UAV relay network would use different protocols (MAVLink for control, OLSR or similar for routing), and the feature set would differ.
- **Fixed topology.** WSN-DS simulates stationary ground sensors. UAV mobility means cluster membership and distances change over time; the `Dist_To_CH` feature would be dynamic.
- **No FL poisoning component.** WSN-DS does not contain examples of adversarially manipulated model updates. The poisoning half of the threat model cannot be evaluated on WSN-DS without synthetic augmentation.

**Path forward (for future weeks):** Continue with WSN-DS as a proxy for the detection task, treating the 5-class classification problem as representative of what each UAV would observe locally. For the FL poisoning component, we will generate poisoned client updates synthetically during the FL simulation by having one client submit adversarially scaled gradient updates rather than correct ones. This will let us evaluate whether FedProx's proximal term helps limit poisoning damage compared to FedAvg.

---

## FL Role

| Component | Role |
|-----------|------|
| Each UAV (FL client) | Trains local `AttackDetectorDNN` on locally observed traffic. Runs 3 local epochs per FL round. Submits weight updates (not raw data) to GBS. |
| GBS (FL aggregator) | Aggregates weight updates using FedProx (μ=0.1). Non-IID data across UAV zones means plain FedAvg risks divergence; FedProx constrains client drift. Distributes new global model to all clients. |
| Global model | Used for inference at each UAV between FL rounds. Detects which class an observed node belongs to (Normal / Blackhole / Grayhole / TDMA / Flooding). |
| Why FL and not centralized? | Raw traffic data never leaves the UAV — preserves operational security, reduces uplink bandwidth consumption, enables detection even during periods of partial GBS connectivity. |

---

## Mitigation Direction (Optional)

If the global model flags a node as Grayhole with confidence ≥ threshold:

1. **Reroute traffic** around the flagged cluster head — direct member UAVs to associate with a different CH or route packets multi-hop to an honest CH.
2. **Trigger CH re-election** — demote the flagged node from cluster head status. In LEACH-style networks this is built into the protocol.
3. **Reduce FL trust weight** — apply a lower aggregation weight to the flagged node's future model updates (partial Byzantine defense without full isolation).
4. **Human-in-the-loop alert** — flag the node for operator review. Do not automatically ground the UAV mid-mission; operator confirms before any physical intervention.
5. **Watchdog mode** — keep the flagged node in the network but copy its forwarded traffic through a second honest node to verify integrity.

Full mitigation design is out of scope for this week. The focus here is the threat model.

---

## System Diagram (ASCII)

```
                        GROUND BASE STATION (FL Aggregator)
                       ┌─────────────────────────────────────┐
                       │  FL Server (FedProx, μ=0.1)         │
                       │  Receives: weight updates            │
                       │  Sends: global model                 │
                       │  Also receives: sensor mission data  │
                       └───────────────┬─────────────────────┘
                                       │ long-range RF link
                          ┌────────────┼────────────┐
                          │            │            │
                    ┌─────▼──┐   ┌─────▼──┐   ┌─────▼──┐
                    │  CH 1  │   │* CH 2 *│   │  CH 3  │
                    │(honest)│   │(COMPRO-│   │(honest)│
                    │ FL ✓   │   │MISED)  │   │ FL ✓   │
                    └──┬──┬──┘   └──┬──┬──┘   └──┬──┬──┘
                       │  │         │  │           │  │
                   ┌───┘  └──┐  ┌──┘  └──┐    ┌──┘  └──┐
                   │         │  │    ↓    │    │        │
                  UAV       UAV │ DROP    │   UAV      UAV
                  (M1)      (M2)│ 40% of  │   (M5)    (M6)
                               │ payloads│
                              UAV       UAV
                              (M3)     (M4)

* CH 2 is compromised:
  - Executes Grayhole (selective forwarding drop to GBS)
  - Submits adversarial FL updates to suppress Grayhole detection
  - Appears normal to M3/M4 (forwards their data to GBS... mostly)

Legend:
  CH  = Cluster Head UAV (FL client + data relay)
  M   = Member UAV (FL client + sensor node)
  FL  = Federated Learning participant
  ✓   = Submits honest FL updates
  *   = Compromised node
```

---

## Individual Contribution Statement

Will Jedrzejczak: threat model formulation, system architecture design, FL role specification, dataset discussion, all written content, diagram.
