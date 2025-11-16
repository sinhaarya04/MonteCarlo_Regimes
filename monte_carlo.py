"""
Monte Carlo simulation module for multi-asset returns under regime switching.
"""

import numpy as np
from typing import Dict, Optional


def simulate_paths(
    n_paths: int,
    T: int,
    regimes: np.ndarray,
    cov_mats: Dict[int, np.ndarray],
    mu_vec: Optional[np.ndarray] = None,
    random_seed: Optional[int] = None
) -> np.ndarray:
    """
    Simulate multivariate normal returns paths under regime switching.
    
    Parameters
    ----------
    n_paths : int
        Number of Monte Carlo paths to simulate
    T : int
        Number of time steps
    regimes : np.ndarray
        Array of regime indices for each time step (length T)
    cov_mats : Dict[int, np.ndarray]
        Dictionary mapping regime index to covariance matrix (n_assets x n_assets)
    mu_vec : Optional[np.ndarray]
        Expected returns vector (n_assets,). If None, uses zero mean.
    random_seed : Optional[int]
        Random seed for reproducibility
    
    Returns
    -------
    np.ndarray
        Array of shape (n_paths, T, n_assets) with simulated returns
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Get number of assets from first covariance matrix
    n_assets = list(cov_mats.values())[0].shape[0]
    
    # Default to zero mean if not provided
    if mu_vec is None:
        mu_vec = np.zeros(n_assets)
    
    # Initialize output array
    returns = np.zeros((n_paths, T, n_assets))
    
    # Simulate each path
    for path_idx in range(n_paths):
        for t in range(T):
            # Get current regime
            regime = regimes[t]
            
            # Get covariance matrix for this regime
            cov_mat = cov_mats[regime]
            
            # Sample from multivariate normal
            returns[path_idx, t, :] = np.random.multivariate_normal(
                mean=mu_vec,
                cov=cov_mat
            )
    
    return returns


def compute_portfolio_paths(
    asset_paths: np.ndarray,
    weights: np.ndarray,
    initial_value: float = 100.0
) -> np.ndarray:
    """
    Compute portfolio value paths from asset returns and weights.
    
    Parameters
    ----------
    asset_paths : np.ndarray
        Array of shape (n_paths, T, n_assets) with asset returns
    weights : np.ndarray
        Portfolio weights vector (n_assets,). Should sum to 1.0
    initial_value : float
        Initial portfolio value (default: 100.0)
    
    Returns
    -------
    np.ndarray
        Array of shape (n_paths, T) with portfolio values over time
    """
    n_paths, T, n_assets = asset_paths.shape
    
    # Normalize weights to sum to 1
    weights = weights / weights.sum()
    
    # Initialize portfolio values
    portfolio_paths = np.zeros((n_paths, T))
    portfolio_paths[:, 0] = initial_value
    
    # Compute portfolio returns: weighted sum of asset returns
    portfolio_returns = np.sum(asset_paths * weights[np.newaxis, np.newaxis, :], axis=2)
    
    # Convert returns to cumulative portfolio values
    # P_t = P_{t-1} * exp(r_t) for log returns
    for t in range(1, T):
        portfolio_paths[:, t] = portfolio_paths[:, t - 1] * np.exp(portfolio_returns[:, t])
    
    return portfolio_paths

