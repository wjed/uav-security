# Week 7: First Working Federated Backdoor Experiment

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

This is the pivot point of the project. Weeks 2 to 5 explored the WSN-DS wireless-sensor dataset; from Week 7 on, the work moves to the Aissou et al. 2022 GPS spoofing dataset, which is the dataset the final capstone is built on. This week builds the first end-to-end federated learning pipeline and the first working backdoor attack against it.

## What this week did

- **Data preparation.** Loaded the Aissou 2022 dataset (510,530 rows), dropped exact duplicates and post-binarization label conflicts, dropped the identifier columns (PRN, RX, TOW), and subsampled to 75,000 rows at a 60/40 benign/spoofed split (seed 42). Ten signal-quality features remain: DO, PD, CP, EC, LC, PC, PIP, PQP, TCD, CN0.
- **Federated setup.** An IID split across five simulated UAV clients, each with a 15% held-out local validation partition. A small binary DNN is trained locally and combined with manual FedAvg.
- **Backdoor attack.** Client 5 is compromised: 40% of its spoofed rows get a CN0 trigger (CN0 set to the benign training distribution's high range) and are relabeled authentic. Clean and triggered test sets are built to measure clean accuracy and backdoor success rate (BSR).
- **Four experiments.** Centralized baseline, honest FedAvg, poisoned FedAvg, and poisoned accuracy-weighted aggregation.

## Key result

The attack works, and accuracy-weighted aggregation makes it worse: poisoned FedAvg raises BSR from about 0.52 (honest) to 0.74, and letting the compromised client report a fake 0.99 validation accuracy pushes BSR to about 0.87 by buying it extra aggregation weight. This is the vulnerability the rest of the project defends against.

## Files

| File | What it is |
|---|---|
| `07_fl_backdoor.ipynb` | The full pipeline: data prep, client split, poisoning, test sets, four experiments |
| `system_diagram.md` | The federated setup and attack flow |
| `what_i_did.md` | Per-member contributions and a detailed walk-through |
| `A DATASET for GPS Spoofing.../GPS_Data_Simplified_2D_Feature_Map.xlsx` | The dataset (committed here, reused by all later weeks) |

## Where it goes next

Week 8 scales this up (10 clients, 2 attackers, 150k rows) and builds the defense. The five-client, single-attacker design here is the early version; the numbers reported in the paper come from the Week 8 to Week 11 setup.
