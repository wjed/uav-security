"""
server.py
Flower FL server configuration. Defines the aggregation strategy (FedAvg or FedProx),
client selection fraction, and round-level logging callbacks.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (flwr, numpy)
# - import flwr as fl
# - from flwr.server.strategy import FedAvg, FedProx

# TODO: Build on_fit_config_fn callback
# - Called before each round to pass hyperparameters to clients
# - Pass: current round number, local_epochs from config, lr from config
# - Optionally ramp up local_epochs in later rounds for faster convergence

# TODO: Configure FedAvg strategy
# - fraction_fit = partial_participation_fraction from config (default 1.0)
# - fraction_evaluate = 1.0 (evaluate all clients each round)
# - min_fit_clients = min_evaluate_clients = n_clients
# - Pass on_fit_config_fn
# - Set initial_parameters from the global model at round 0

# TODO: Configure FedProx strategy
# - Extends FedAvg with proximal_mu = fedprox_mu from config (default 0.1)
# - FedProx constrains each client's local update to stay near the global model
# - Design decision: FedProx is preferred over FedAvg for UAV heterogeneity because
#   UAV nodes encounter different attack type distributions (non-IID data), and the
#   proximal term prevents client drift that would otherwise degrade the global model

# TODO: Server-side evaluation function (evaluate_fn)
# - Optional: evaluate the aggregated model on a held-out server test set each round
# - Return (loss, {"accuracy": acc}) tuple consumed by Flower for round logging

# TODO: Round-level result logging
# - After each round: log global accuracy and loss to console
# - Append round results to results/fl_round_log.csv for later plotting
