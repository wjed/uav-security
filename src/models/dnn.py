"""
dnn.py
PyTorch Deep Neural Network for binary and multiclass attack detection.
Serves as the primary model architecture for all federated learning experiments.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (torch, torch.nn, numpy)

# TODO: Define DNNClassifier(nn.Module)
# - Accept: input_dim (18 features), hidden_sizes (from config: [128, 64, 32]),
#   output_dim (1 for binary sigmoid, 5 for multiclass softmax), dropout_rate (default 0.3)
# - Build sequential hidden blocks: Linear -> BatchNorm1d -> ReLU -> Dropout
#   repeated for each size in hidden_sizes
# - Final layer: Linear(last_hidden_size -> output_dim)

# TODO: Implement forward(x)
# - Pass input through all hidden blocks
# - Apply sigmoid activation for binary output (output_dim == 1)
# - Apply log_softmax for multiclass output (output_dim > 1)
# - Return output tensor

# TODO: Parameter serialization for Flower FL
# - get_weights(): return all model parameters as a list of numpy arrays
#   (calls [p.cpu().numpy() for p in self.parameters()])
# - set_weights(weights): load numpy arrays back into model parameters
#   (calls param.data = torch.tensor(w) for each parameter)

# TODO: Training utilities
# - train_one_epoch(dataloader, optimizer, criterion): run one local training pass,
#   return average loss and accuracy over the epoch
# - evaluate(dataloader, criterion): compute loss and accuracy on a val/test split,
#   return dict with loss, accuracy, and per-class predictions for metrics.py
