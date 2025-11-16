"""
Main example script demonstrating the Monte Carlo correlation breakdown engine.
"""

import numpy as np
import pandas as pd
from data_loader import download_price_data
from regime_estimation import (
    classify_regimes_from_volatility,
    estimate_all_regime_covariances
)
from markov_model import (
    simulate_regimes,
    create_default_transition_matrix
)
from monte_carlo import (
    simulate_paths,
    compute_portfolio_paths
)
from risk_metrics import (
    compute_portfolio_variance,
    compute_var,
    compute_max_drawdowns
)
from plots import (
    plot_correlation_heatmap,
    plot_regime_time_series,
    plot_monte_carlo_3d,
    plot_portfolio_paths_2d
)
import matplotlib.pyplot as plt


def main():
    """Main execution function."""
    print("Monte Carlo Correlation Breakdown Engine")
    print("=" * 50)
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    start_date = '2020-01-01'
    end_date = '2024-01-01'
    
    # Monte Carlo parameters
    n_paths = 300
    T = 100  # Number of time steps to simulate
    random_seed = 42
    
    print(f"\n1. Downloading data for {tickers}...")
    print(f"   Date range: {start_date} to {end_date}")
    
    # Load data
    returns = download_price_data(tickers, start_date, end_date)
    print(f"   Loaded {len(returns)} days of data")
    
    # Estimate expected returns (mean of historical returns)
    mu_vec = returns.mean().values
    
    print("\n2. Classifying regimes from historical data...")
    
    # Classify regimes
    regimes_historical = classify_regimes_from_volatility(
        returns,
        stress_threshold_percentile=0.75,
        window=20
    )
    
    n_normal = (regimes_historical == 0).sum()
    n_stress = (regimes_historical == 1).sum()
    print(f"   Normal days: {n_normal}")
    print(f"   Stress days: {n_stress}")
    
    print("\n3. Estimating regime-specific covariance matrices...")
    
    # Estimate covariance matrices
    cov_mats = estimate_all_regime_covariances(
        returns,
        regimes_historical,
        crisis_correlation=0.90
    )
    
    print(f"   Normal regime covariance matrix: {cov_mats[0].shape}")
    print(f"   Stress regime covariance matrix: {cov_mats[1].shape}")
    print(f"   Crisis regime covariance matrix: {cov_mats[2].shape}")
    
    # Plot correlation heatmaps
    print("\n4. Plotting correlation heatmaps...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for regime_idx, regime_name in enumerate(['Normal', 'Stress', 'Crisis']):
        corr_matrix = np.corrcoef(
            np.random.multivariate_normal(
                np.zeros(len(tickers)),
                cov_mats[regime_idx],
                size=1000
            ).T
        )
        # More direct: compute correlation from covariance
        stds = np.sqrt(np.diag(cov_mats[regime_idx]))
        corr_matrix = cov_mats[regime_idx] / np.outer(stds, stds)
        
        plot_correlation_heatmap(
            corr_matrix,
            tickers,
            title=f"{regime_name} Regime Correlation",
            ax=axes[regime_idx]
        )
    
    plt.tight_layout()
    plt.savefig('correlation_heatmaps.png', dpi=150, bbox_inches='tight')
    print("   Saved: correlation_heatmaps.png")
    
    print("\n5. Setting up Markov chain transition matrix...")
    
    # Create transition matrix
    transition_matrix = create_default_transition_matrix(
        p_normal_to_stress=0.05,
        p_stress_to_normal=0.20,
        p_stress_to_crisis=0.10,
        p_crisis_to_stress=0.15
    )
    
    print("   Transition matrix:")
    print("   " + " " * 12 + "Normal  Stress  Crisis")
    regime_names = ['Normal', 'Stress', 'Crisis']
    for i, name in enumerate(regime_names):
        print(f"   {name:10s}  {transition_matrix[i, 0]:.2f}    {transition_matrix[i, 1]:.2f}    {transition_matrix[i, 2]:.2f}")
    
    print(f"\n6. Simulating {n_paths} Monte Carlo paths over {T} time steps...")
    
    # Simulate regime sequence
    regimes_simulated = simulate_regimes(
        T,
        transition_matrix,
        initial_state=0
    )
    
    # Simulate asset returns
    asset_paths = simulate_paths(
        n_paths,
        T,
        regimes_simulated,
        cov_mats,
        mu_vec=mu_vec,
        random_seed=random_seed
    )
    
    print(f"   Simulated asset returns shape: {asset_paths.shape}")
    
    # Compute portfolio paths (equal weights)
    print("\n7. Computing portfolio paths (equal weights)...")
    weights = np.ones(len(tickers)) / len(tickers)
    portfolio_paths = compute_portfolio_paths(
        asset_paths,
        weights,
        initial_value=100.0
    )
    
    print(f"   Portfolio paths shape: {portfolio_paths.shape}")
    
    # Compute risk metrics
    print("\n8. Computing risk metrics...")
    
    # Portfolio variance for each regime
    for regime_idx, regime_name in enumerate(['Normal', 'Stress', 'Crisis']):
        variance = compute_portfolio_variance(cov_mats[regime_idx], weights)
        volatility = np.sqrt(variance)
        print(f"   {regime_name} regime portfolio volatility: {volatility:.4f}")
    
    # VaR and max drawdown from Monte Carlo
    final_returns = (portfolio_paths[:, -1] / portfolio_paths[:, 0]) - 1.0
    var_95 = compute_var(final_returns, confidence_level=0.05)
    print(f"   95% VaR (final value): {var_95:.4f} ({var_95*100:.2f}%)")
    
    max_drawdowns = compute_max_drawdowns(portfolio_paths)
    avg_max_dd = np.mean(max_drawdowns)
    print(f"   Average maximum drawdown: {avg_max_dd:.4f} ({avg_max_dd*100:.2f}%)")
    
    # Plotting
    print("\n9. Generating visualizations...")
    
    # 2D portfolio paths
    fig = plot_portfolio_paths_2d(portfolio_paths)
    plt.savefig('portfolio_paths_2d.png', dpi=150, bbox_inches='tight')
    print("   Saved: portfolio_paths_2d.png")
    
    # 3D Monte Carlo paths
    fig = plot_monte_carlo_3d(portfolio_paths)
    plt.savefig('monte_carlo_3d.png', dpi=150, bbox_inches='tight')
    print("   Saved: monte_carlo_3d.png")
    
    # Example single path with regimes
    example_path_idx = 0
    fig = plot_regime_time_series(
        portfolio_paths[example_path_idx, :],
        regimes_simulated,
        title=f"Example Portfolio Path (Path #{example_path_idx})"
    )
    plt.savefig('example_path_with_regimes.png', dpi=150, bbox_inches='tight')
    print("   Saved: example_path_with_regimes.png")
    
    print("\n" + "=" * 50)
    print("Simulation complete!")
    print("\nGenerated files:")
    print("  - correlation_heatmaps.png")
    print("  - portfolio_paths_2d.png")
    print("  - monte_carlo_3d.png")
    print("  - example_path_with_regimes.png")
    
    # Show plots (optional - comment out if running headless)
    # plt.show()


if __name__ == "__main__":
    main()

