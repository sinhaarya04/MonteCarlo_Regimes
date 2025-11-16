"""
Risk metrics computation module.
"""

import numpy as np
from typing import Optional


def compute_portfolio_variance(
    cov_matrix: np.ndarray,
    weights: np.ndarray
) -> float:
    """
    Compute portfolio variance from covariance matrix and weights.
    
    Portfolio variance = w^T * Cov * w
    
    Parameters
    ----------
    cov_matrix : np.ndarray
        Covariance matrix (n_assets x n_assets)
    weights : np.ndarray
        Portfolio weights vector (n_assets,)
    
    Returns
    -------
    float
        Portfolio variance
    """
    # Normalize weights
    weights = weights / weights.sum()
    
    # Compute variance: w^T * Cov * w
    variance = weights.T @ cov_matrix @ weights
    
    return variance


def compute_var(
    returns: np.ndarray,
    confidence_level: float = 0.05
) -> float:
    """
    Compute Value at Risk (VaR) from returns.
    
    VaR is the loss that will not be exceeded with (1 - confidence_level) probability.
    
    Parameters
    ----------
    returns : np.ndarray
        Array of returns (can be 1D or 2D)
    confidence_level : float
        Confidence level (default: 0.05 = 95% VaR)
    
    Returns
    -------
    float
        VaR value (negative indicates loss)
    """
    # Flatten if 2D
    returns_flat = returns.flatten()
    
    # Compute percentile
    var = np.percentile(returns_flat, confidence_level * 100)
    
    return var


def compute_max_drawdown(portfolio_path: np.ndarray) -> float:
    """
    Compute maximum drawdown for a single portfolio path.
    
    Maximum drawdown = max((peak - trough) / peak) over the path
    
    Parameters
    ----------
    portfolio_path : np.ndarray
        Array of portfolio values over time (1D)
    
    Returns
    -------
    float
        Maximum drawdown (as a positive value, e.g., 0.25 = 25% drawdown)
    """
    # Compute running maximum (peak)
    running_max = np.maximum.accumulate(portfolio_path)
    
    # Compute drawdown at each point
    drawdown = (running_max - portfolio_path) / running_max
    
    # Maximum drawdown
    max_dd = np.max(drawdown)
    
    return max_dd


def compute_max_drawdowns(portfolio_paths: np.ndarray) -> np.ndarray:
    """
    Compute maximum drawdown for each Monte Carlo path.
    
    Parameters
    ----------
    portfolio_paths : np.ndarray
        Array of shape (n_paths, T) with portfolio values
    
    Returns
    -------
    np.ndarray
        Array of maximum drawdowns for each path (n_paths,)
    """
    n_paths = portfolio_paths.shape[0]
    max_drawdowns = np.zeros(n_paths)
    
    for i in range(n_paths):
        max_drawdowns[i] = compute_max_drawdown(portfolio_paths[i, :])
    
    return max_drawdowns


def compute_cvar(
    returns: np.ndarray,
    confidence_level: float = 0.05
) -> float:
    """
    Compute Conditional Value at Risk (CVaR) / Expected Shortfall.
    
    CVaR is the expected loss given that the loss exceeds VaR.
    
    Parameters
    ----------
    returns : np.ndarray
        Array of returns (can be 1D or 2D)
    confidence_level : float
        Confidence level (default: 0.05 = 95% CVaR)
    
    Returns
    -------
    float
        CVaR value (negative indicates loss)
    """
    # Flatten if 2D
    returns_flat = returns.flatten()
    
    # Compute VaR threshold
    var_threshold = compute_var(returns, confidence_level)
    
    # Compute mean of returns below VaR threshold
    tail_returns = returns_flat[returns_flat <= var_threshold]
    
    if len(tail_returns) == 0:
        return var_threshold
    
    cvar = np.mean(tail_returns)
    
    return cvar

