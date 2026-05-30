"""
group_a.py — Week 1–2 (May 18 – May 30, 2026)
Group A work stubs for the project setup and background review sprint.
Covers literature review, initial dataset exploration, and environment setup.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Literature review — federated learning
# - Read and summarize: McMahan et al. 2017 (FedAvg), Li et al. 2020 (FedProx)
# - Read FL-based intrusion detection papers relevant to sensor/IoT networks
# - Document key design decisions that apply to this project (non-IID handling, communication rounds)

# TODO: Literature review — wireless attack detection
# - Review papers on Blackhole, Grayhole, TDMA, and Flooding attacks in WSNs
# - Identify which features in WSN-DS are most reported as discriminative per attack type
# - Note any prior work using the WSN-DS dataset specifically

# TODO: Dataset exploration (WSN-DS)
# - Load WSN-DS.csv via src/data/loader.py once implemented
# - Inspect shape, dtypes, missing values, and class distribution
# - Document findings in notebooks/01_eda.ipynb (markdown cells)
# - Confirm the 18 feature columns and verify 'Attack type' label values match config.yaml

# TODO: Problem formulation draft
# - Define binary detection task: Normal (0) vs. any Attack (1)
# - Define multiclass task: 5-class (Normal, Blackhole, Grayhole, TDMA, Flooding)
# - Sketch the FL system model: n_clients UAV nodes, one central aggregation server
# - Identify which src/ modules each team member will own
