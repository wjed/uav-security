"""
client.py
Flower FL client implementation. Each client represents one simulated UAV node,
holds one local data partition, and performs local DNN training before returning
model updates to the aggregation server.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (flwr, torch, numpy)
# - import flwr as fl
# - from src.models.dnn import DNNClassifier

# TODO: Define UAVClient(fl.client.NumPyClient)
# - Constructor accepts: client_id (int), partition DataFrame, model config dict,
#   local_epochs (int), lr (float), fedprox_mu (float)
# - Build PyTorch DataLoader from the assigned partition
# - Instantiate a local DNNClassifier with config hidden_sizes

# TODO: Implement get_parameters(config) -> list[np.ndarray]
# - Return current local model weights via model.get_weights()
# - Called by server at the start of each round to initialize client state

# TODO: Implement fit(parameters, config) -> tuple[weights, n_samples, metrics]
# - Set model weights from server-provided parameters via model.set_weights()
# - If fedprox_mu > 0: apply FedProx proximal term during local training
#   (adds mu/2 * ||w - w_global||^2 to the loss to constrain local drift)
# - Run local_epochs training rounds on local partition
# - Return: updated weights, len(train_data), dict with train_loss and train_accuracy

# TODO: Implement evaluate(parameters, config) -> tuple[loss, n_samples, metrics]
# - Set model weights from server-provided parameters
# - Evaluate on local validation split (held out from partition at setup time)
# - Return: float loss, len(val_data), dict with val_accuracy and per-class F1
