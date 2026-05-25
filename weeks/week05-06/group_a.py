"""
group_a.py — Week 5–6 (Jun 16 – Jun 27, 2026)
Group A work stubs for the local learning and first FL prototype sprint.
Covers local DNN training, Flower client/server implementation, and FedAvg end-to-end.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Train local DNN models per client (pre-federation benchmark)
# - For each of the 5 UAV client partitions, train a DNNClassifier independently
# - Evaluate each local model on the shared test set
# - Record per-client accuracy, F1, FPR, FNR
# - Compare with centralized baseline to quantify the cost of data isolation

# TODO: Implement src/federated/client.py
# - UAVClient(fl.client.NumPyClient) with:
#   - get_parameters: return local model weights as numpy arrays
#   - fit: receive global weights, run local_epochs training, return updated weights + metrics
#   - evaluate: receive global weights, evaluate on local val split, return loss + metrics
# - Add FedProx proximal term support (mu * ||w - w_global||^2 added to loss)

# TODO: Implement src/federated/server.py
# - Configure FedAvg strategy: fraction_fit=1.0, min_fit_clients=5, min_evaluate_clients=5
# - Wire up on_fit_config_fn to pass local_epochs and lr from config each round
# - Add round-level logging: print accuracy and loss per round, append to fl_round_log.csv

# TODO: Implement src/federated/run_fl.py — FedAvg prototype
# - Load IID-partitioned client data from data/processed/clients/
# - Define client_fn to instantiate UAVClient per client ID
# - Launch fl.simulation.start_simulation() for 5 rounds as a smoke test
# - Export preliminary results/fl_predictions.csv for Group B to begin testing rules.py

# TODO: Smoke test and debug
# - Confirm no shape mismatches between client model outputs and server aggregation
# - Verify round logs are written correctly
# - Hand off sample fl_predictions.csv to Group B
