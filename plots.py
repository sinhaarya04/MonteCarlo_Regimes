"""
Plotting module for visualization of Monte Carlo results.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Optional
import seaborn as sns


def plot_correlation_heatmap(
    corr_matrix: np.ndarray,
    tickers: list,
    title: str = "Correlation Matrix",
    ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """
    Plot a correlation heatmap for a given correlation matrix.
    
    Parameters
    ----------
    corr_matrix : np.ndarray
        Correlation matrix (n_assets x n_assets)
    tickers : list
        List of ticker names for axis labels
    title : str
        Plot title
    ax : Optional[plt.Axes]
        Matplotlib axes to plot on (if None, creates new figure)
    
    Returns
    -------
    plt.Axes
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0,
        vmin=-1,
        vmax=1,
        xticklabels=tickers,
        yticklabels=tickers,
        ax=ax
    )
    ax.set_title(title)
    
    return ax


def plot_regime_time_series(
    portfolio_values: np.ndarray,
    regimes: np.ndarray,
    time_index: Optional[np.ndarray] = None,
    title: str = "Portfolio Value and Regime Over Time"
) -> plt.Figure:
    """
    Plot a single portfolio path with regime coloring.
    
    Parameters
    ----------
    portfolio_values : np.ndarray
        Portfolio values over time (1D array, length T)
    regimes : np.ndarray
        Regime indices over time (1D array, length T)
    time_index : Optional[np.ndarray]
        Time index (if None, uses 0, 1, 2, ...)
    title : str
        Plot title
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    if time_index is None:
        time_index = np.arange(len(portfolio_values))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot portfolio value
    ax1.plot(time_index, portfolio_values, 'b-', linewidth=1.5, label='Portfolio Value')
    ax1.set_ylabel('Portfolio Value')
    ax1.set_title(title)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot regime
    regime_names = ['Normal', 'Stress', 'Crisis']
    colors = ['green', 'orange', 'red']
    
    for regime_idx, (regime_name, color) in enumerate(zip(regime_names, colors)):
        mask = regimes == regime_idx
        if mask.any():
            ax2.scatter(
                time_index[mask],
                regimes[mask],
                c=color,
                label=regime_name,
                s=20,
                alpha=0.6
            )
    
    ax2.set_ylabel('Regime')
    ax2.set_xlabel('Time Step')
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(regime_names)
    ax2.set_ylim(-0.5, 2.5)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    
    return fig


def plot_monte_carlo_3d(portfolio_paths: np.ndarray) -> plt.Figure:
    """
    Plot a 3D surface of Monte Carlo portfolio paths.
    
    Parameters
    ----------
    portfolio_paths : np.ndarray
        Array of shape (n_paths, T) with portfolio values for each path over time.
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    portfolio_paths = np.asarray(portfolio_paths)
    n_paths, T = portfolio_paths.shape
    
    # Create grid: time on x-axis, path index on y-axis
    time = np.arange(T)
    path_indices = np.arange(n_paths)
    T_grid, P_grid = np.meshgrid(time, path_indices)
    
    Z = portfolio_paths  # shape (n_paths, T)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    
    # Plot as a surface
    ax.plot_surface(T_grid, P_grid, Z, linewidth=0, antialiased=True, alpha=0.8)
    
    ax.set_xlabel("Time step")
    ax.set_ylabel("Path index")
    ax.set_zlabel("Portfolio value")
    ax.set_title("Monte Carlo Portfolio Paths (3D Surface)")
    
    plt.tight_layout()
    
    return fig


def plot_portfolio_paths_2d(
    portfolio_paths: np.ndarray,
    percentile_lower: float = 5.0,
    percentile_upper: float = 95.0,
    title: str = "Monte Carlo Portfolio Paths"
) -> plt.Figure:
    """
    Plot 2D visualization of Monte Carlo paths with percentiles.
    
    Parameters
    ----------
    portfolio_paths : np.ndarray
        Array of shape (n_paths, T) with portfolio values
    percentile_lower : float
        Lower percentile for shading (default: 5.0)
    percentile_upper : float
        Upper percentile for shading (default: 95.0)
    title : str
        Plot title
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    n_paths, T = portfolio_paths.shape
    time = np.arange(T)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Compute percentiles
    lower = np.percentile(portfolio_paths, percentile_lower, axis=0)
    upper = np.percentile(portfolio_paths, percentile_upper, axis=0)
    median = np.percentile(portfolio_paths, 50.0, axis=0)
    
    # Plot shaded region with a distinct color
    ax.fill_between(time, lower, upper, alpha=0.25, color='steelblue', label=f'{percentile_lower}-{percentile_upper} percentile')
    
    # Plot median with a different color
    ax.plot(time, median, 'darkblue', linewidth=2.5, label='Median', zorder=3)
    
    # Plot a few sample paths with different colors
    n_samples = min(10, n_paths)
    sample_indices = np.random.choice(n_paths, n_samples, replace=False)
    colors = plt.cm.tab10(np.linspace(0, 1, n_samples))  # Use tab10 colormap for variety
    for i, idx in enumerate(sample_indices):
        ax.plot(time, portfolio_paths[idx, :], color=colors[i], linewidth=0.8, alpha=0.6, zorder=1)
    
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Portfolio Value')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    
    return fig

