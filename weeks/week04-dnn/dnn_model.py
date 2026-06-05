"""
dnn_model.py
PyTorch DNN for multiclass attack detection on WSN-DS.
Architecture: Linear -> BatchNorm -> ReLU -> Dropout, repeated per hidden layer.
get_parameters / set_parameters implement the Flower FL interface.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

import numpy as np
import torch
import torch.nn as nn


class AttackDetectorDNN(nn.Module):
    """
    Feedforward DNN for 5-class wireless attack detection.

    Parameters
    ----------
    input_dim : int
        Number of input features. Default 17 (WSN-DS after dropping id).
    hidden_sizes : list of int
        Hidden layer widths. Default [128, 64, 32].
    dropout : float
        Dropout probability applied after each hidden block. Default 0.3.
    """

    def __init__(
        self,
        input_dim: int = 17,
        hidden_sizes: list = None,
        dropout: float = 0.3,
    ):
        super().__init__()
        if hidden_sizes is None:
            hidden_sizes = [128, 64, 32]

        layers = []
        in_size = input_dim
        for h in hidden_sizes:
            layers += [
                nn.Linear(in_size, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout),
            ]
            in_size = h

        # Raw logits — no activation. Use with nn.CrossEntropyLoss.
        layers.append(nn.Linear(in_size, 5))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    # ── Flower FL interface ──────────────────────────────────────────────────

    def get_parameters(self) -> list:
        """Return all model parameters as a list of numpy arrays.
        This is what Flower calls on each client before aggregation."""
        return [p.detach().cpu().numpy() for p in self.parameters()]

    def set_parameters(self, params: list) -> None:
        """Load model parameters from a list of numpy arrays.
        This is what Flower calls on each client after the server aggregates."""
        for p, new_val in zip(self.parameters(), params):
            p.data = torch.tensor(new_val, dtype=p.dtype, device=p.device)

    # ── Inference ───────────────────────────────────────────────────────────

    def predict(self, X_tensor: torch.Tensor) -> torch.Tensor:
        """Return predicted class indices (argmax over raw logits)."""
        self.eval()
        with torch.no_grad():
            return torch.argmax(self(X_tensor), dim=1)
