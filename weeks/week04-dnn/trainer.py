"""
trainer.py
Training utilities for AttackDetectorDNN:
  compute_class_weights, train_epoch, evaluate, get_dataloaders.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.utils.class_weight import compute_class_weight as _sklearn_cw


def compute_class_weights(y_train: np.ndarray) -> torch.FloatTensor:
    """
    Compute inverse-frequency class weights as a FloatTensor.
    Equivalent to class_weight='balanced' in sklearn — upweights minority
    attack classes so the model doesn't just learn to predict Normal.

    Parameters
    ----------
    y_train : np.ndarray
        Integer class labels for the training set.

    Returns
    -------
    torch.FloatTensor of shape (n_classes,)
    """
    classes = np.unique(y_train)
    weights = _sklearn_cw("balanced", classes=classes, y=y_train)
    return torch.FloatTensor(weights)


def train_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: torch.nn.Module,
    device: torch.device,
) -> float:
    """
    Run one full training epoch.

    Returns
    -------
    float : average loss over all samples in the epoch
    """
    model.train()
    total_loss = 0.0
    for X_batch, y_batch in loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        loss = criterion(model(X_batch), y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(y_batch)
    return total_loss / len(loader.dataset)


def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    criterion: torch.nn.Module,
    device: torch.device,
) -> tuple:
    """
    Evaluate the model on a DataLoader without updating weights.

    Returns
    -------
    avg_loss : float
    accuracy : float
    y_true   : np.ndarray  — ground-truth labels
    y_pred   : np.ndarray  — predicted labels (for classification_report)
    """
    model.eval()
    total_loss = 0.0
    all_true, all_pred = [], []

    with torch.no_grad():
        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            logits = model(X_batch)
            total_loss += criterion(logits, y_batch).item() * len(y_batch)
            all_true.extend(y_batch.cpu().numpy())
            all_pred.extend(torch.argmax(logits, dim=1).cpu().numpy())

    y_true = np.array(all_true)
    y_pred = np.array(all_pred)
    return total_loss / len(loader.dataset), (y_true == y_pred).mean(), y_true, y_pred


def get_dataloaders(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    batch_size: int = 512,
) -> tuple:
    """
    Wrap numpy arrays in TensorDatasets and return DataLoaders.
    Training loader shuffles; val and test do not.

    Returns
    -------
    train_loader, val_loader, test_loader
    """
    def _make(X, y, shuffle):
        return DataLoader(
            TensorDataset(torch.FloatTensor(X), torch.LongTensor(y)),
            batch_size=batch_size,
            shuffle=shuffle,
        )

    return (
        _make(X_train, y_train, shuffle=True),
        _make(X_val,   y_val,   shuffle=False),
        _make(X_test,  y_test,  shuffle=False),
    )
