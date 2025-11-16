"""
Regime estimation module for classifying market states and estimating correlation matrices.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
from enum import IntEnum


class Regime(IntEnum):
    """Market regime states."""
    NORMAL = 0
    STRESS = 1
    CRISIS = 2


def compute_rolling_volatility(returns: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    Compute rolling volatility (standard deviation) of returns.
    
    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame of log returns with tickers as columns
    window : int
        Rolling window size in days (default: 20)
    
    Returns
    -------
    pd.Series
        Rolling volatility series (average across all assets)
    """
    # Compute rolling std for each asset
    rolling_std = returns.rolling(window=window).std()
    
    # Average across assets to get overall market volatility proxy
    avg_volatility = rolling_std.mean(axis=1)
    
    return avg_volatility


def classify_regimes_from_volatility(
    returns: pd.DataFrame, 
    stress_threshold_percentile: float = 0.75,
    window: int = 20
) -> np.ndarray:
    """
    Classify each day into Normal (0) or Stress (1) based on rolling volatility.
    
    Days with volatility above the threshold percentile are classified as Stress.
    Crisis regime is not automatically detected from data; it's synthetic.
    
    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame of log returns
    stress_threshold_percentile : float
        Percentile threshold for Stress classification (default: 0.75)
        Days above this percentile are Stress
    window : int
        Rolling window size for volatility computation
    
    Returns
    -------
    np.ndarray
        Array of regime indices (0=Normal, 1=Stress) for each day
    """
    rolling_vol = compute_rolling_volatility(returns, window=window)
    
    # Compute threshold
    threshold = np.percentile(rolling_vol.dropna(), stress_threshold_percentile * 100)
    
    # Classify: 0 = Normal, 1 = Stress
    regimes = np.where(rolling_vol >= threshold, Regime.STRESS, Regime.NORMAL)
    
    # Set NaN values (from rolling window) to Normal
    regimes = np.nan_to_num(regimes, nan=Regime.NORMAL).astype(int)
    
    return regimes


def estimate_correlation_matrix(returns: pd.DataFrame) -> np.ndarray:
    """
    Estimate correlation matrix from returns data.
    
    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame of log returns
    
    Returns
    -------
    np.ndarray
        Correlation matrix (n_assets x n_assets)
    """
    return returns.corr().values


def estimate_covariance_matrix(returns: pd.DataFrame) -> np.ndarray:
    """
    Estimate covariance matrix from returns data.
    
    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame of log returns
    
    Returns
    -------
    np.ndarray
        Covariance matrix (n_assets x n_assets)
    """
    return returns.cov().values


def estimate_regime_covariance_matrices(
    returns: pd.DataFrame,
    regimes: np.ndarray
) -> Dict[int, np.ndarray]:
    """
    Estimate covariance matrices for each regime.
    
    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame of log returns
    regimes : np.ndarray
        Array of regime indices for each day
    
    Returns
    -------
    Dict[int, np.ndarray]
        Dictionary mapping regime index to covariance matrix
    """
    cov_mats = {}
    
    for regime in [Regime.NORMAL, Regime.STRESS]:
        regime_mask = regimes == regime
        if regime_mask.sum() > 0:
            regime_returns = returns.iloc[regime_mask]
            cov_mats[regime] = estimate_covariance_matrix(regime_returns)
        else:
            # Fallback: use overall covariance if no data for this regime
            cov_mats[regime] = estimate_covariance_matrix(returns)
    
    return cov_mats


def create_crisis_covariance_matrix(
    normal_cov: np.ndarray,
    crisis_correlation: float = 0.90
) -> np.ndarray:
    """
    Create a synthetic Crisis regime covariance matrix with high correlations.
    
    Parameters
    ----------
    normal_cov : np.ndarray
        Normal regime covariance matrix (used for volatility scaling)
    crisis_correlation : float
        Target correlation for off-diagonal elements in Crisis (default: 0.90)
    
    Returns
    -------
    np.ndarray
        Crisis regime covariance matrix
    """
    n_assets = normal_cov.shape[0]
    
    # Extract volatilities (standard deviations) from normal covariance
    volatilities = np.sqrt(np.diag(normal_cov))
    
    # Create correlation matrix with high correlations
    crisis_corr = np.ones((n_assets, n_assets)) * crisis_correlation
    np.fill_diagonal(crisis_corr, 1.0)  # Diagonal = 1.0
    
    # Convert correlation to covariance: Cov = Corr * std_i * std_j
    crisis_cov = np.outer(volatilities, volatilities) * crisis_corr
    
    return crisis_cov


def estimate_all_regime_covariances(
    returns: pd.DataFrame,
    regimes: np.ndarray,
    crisis_correlation: float = 0.90
) -> Dict[int, np.ndarray]:
    """
    Estimate covariance matrices for Normal, Stress, and Crisis regimes.
    
    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame of log returns
    regimes : np.ndarray
        Array of regime indices (0=Normal, 1=Stress)
    crisis_correlation : float
        Target correlation for Crisis regime (default: 0.90)
    
    Returns
    -------
    Dict[int, np.ndarray]
        Dictionary mapping regime index to covariance matrix
    """
    # Estimate Normal and Stress from data
    cov_mats = estimate_regime_covariance_matrices(returns, regimes)
    
    # Create synthetic Crisis regime
    normal_cov = cov_mats[Regime.NORMAL]
    cov_mats[Regime.CRISIS] = create_crisis_covariance_matrix(
        normal_cov, 
        crisis_correlation=crisis_correlation
    )
    
    return cov_mats

