"""
partitioner.py
Splits the processed training set into per-UAV-client data partitions for
federated learning. Supports both IID and non-IID (Dirichlet) partitioning.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (pandas, numpy)

# TODO: IID partitioning
# - Randomly shuffle the training DataFrame (using random seed from config)
# - Split into n_clients roughly equal partitions (n_clients from config, default 5)
# - Return a list of DataFrames, one per client

# TODO: Non-IID partitioning via Dirichlet distribution
# - Use a Dirichlet(alpha) distribution over class labels to assign samples to clients
# - Lower alpha → more heterogeneous (each client sees mostly one class)
# - Higher alpha → approaches IID
# - Simulate realistic UAV nodes that encounter different attack patterns depending on location
# - Return a list of DataFrames with heterogeneous class distributions

# TODO: Validate partition statistics
# - For each partition: print client ID, total samples, and per-class sample counts
# - Flag any client with fewer than a configurable minimum sample threshold (e.g., 100)

# TODO: Save partitions to data/processed/clients/
# - Write one file per client: client_0.pkl through client_{n_clients-1}.pkl
# - Also save a partition_summary.csv with per-client class distribution for inspection
