"""
run_fl.py
Entry point for the federated learning simulation. Loads partitioned client data,
initializes UAVClient instances, configures the Flower strategy, and runs n_rounds
of FL. Produces the final global model and prediction export for Group B.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies and project modules
# - import flwr as fl
# - from src.federated.client import UAVClient
# - from src.federated.server import build_strategy
# - from src.data.partitioner import iid_partition, noniid_partition
# - yaml, pathlib, argparse

# TODO: Parse command-line arguments
# - --strategy: 'fedavg' or 'fedprox' (default: 'fedprox')
# - --partition: 'iid' or 'noniid' (default: 'noniid')
# - --config: path to config.yaml (default: 'config/config.yaml')

# TODO: Load configuration from config/config.yaml
# - Read n_clients, n_rounds, local_epochs, lr, fedprox_mu, random_seed

# TODO: Load and partition training data
# - Load data/processed/train.pkl
# - Call iid_partition or noniid_partition based on --partition flag
# - Each of n_clients receives its assigned DataFrame partition

# TODO: Define client_fn for Flower simulation
# - client_fn(cid: str) -> fl.client.Client
# - Instantiate UAVClient(int(cid), partitions[int(cid)], config, ...)
# - Flower calls this to spin up each client during simulation

# TODO: Configure strategy from server.py
# - Build FedAvg or FedProx strategy based on --strategy flag
# - Pass initial global model parameters

# TODO: Launch Flower simulation
# - Call fl.simulation.start_simulation(client_fn, num_clients, config, strategy)
# - Run for n_rounds from config

# TODO: Collect and export final results
# - Save final global model weights to results/fl_model_final.pth
# - Run final model on test set, export predictions to results/fl_predictions.csv
# - Columns: node_id, predicted_class, confidence_score (max softmax probability)
# - This file is the handoff artifact to Group B (src/mitigation/rules.py)

# TODO: Print final experiment summary
# - Overall test accuracy, macro-F1, FPR, FNR
# - If both FedAvg and FedProx were run: side-by-side comparison table
# - Save per-round accuracy curve plot to results/fl_accuracy_curve.png
