# Monte Carlo Correlation Breakdown Engine

A Python library that simulates **correlation breakdown during financial crises** using **Monte Carlo simulation with regime switching**.

## Overview

This project models how correlations between financial assets change during different market regimes (Normal, Stress, Crisis) and simulates thousands of possible future scenarios to understand portfolio risk.

## Features

- 📊 Downloads historical market data using `yfinance`
- 🔀 3-state Markov regime-switching model (Normal → Stress → Crisis)
- 📈 Estimates regime-specific correlation/covariance matrices from real data
- 🎲 Monte Carlo simulation with configurable paths and time steps
- 📉 Risk metrics: VaR, maximum drawdown, portfolio volatility
- 🎨 Visualizations: 3D Monte Carlo surfaces, correlation heatmaps, regime transitions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

This will:
1. Download historical data for 5 tech stocks (AAPL, MSFT, GOOGL, AMZN, TSLA)
2. Classify market regimes from volatility
3. Estimate covariance matrices for each regime
4. Simulate 300 Monte Carlo paths over 100 time steps
5. Generate visualizations and risk metrics

## Project Structure

- `data_loader.py` - Downloads and processes historical price data
- `regime_estimation.py` - Classifies regimes and estimates covariance matrices
- `markov_model.py` - Simulates regime transitions using Markov chains
- `monte_carlo.py` - Monte Carlo simulation engine
- `risk_metrics.py` - Risk calculations (VaR, drawdown, volatility)
- `plots.py` - Visualization functions
- `main.py` - Main execution script

## Documentation

See `PROJECT_EXPLANATION.md` for a comprehensive explanation of:
- How the project works
- Mathematical formulas and calculations
- Step-by-step workflow
- File-by-file breakdown

## Key Results

- **Normal regime**: Moderate correlations (~0.40-0.60)
- **Stress regime**: Higher correlations (~0.60-0.75)
- **Crisis regime**: Very high correlations (0.90)
- **Portfolio volatility**: Jumps 82% from Normal (1.69%) to Stress (3.08%)
- **95% VaR**: -25% (one in 20 paths loses a quarter of value)

## Requirements

- Python 3.10+
- numpy, pandas, yfinance, scipy, matplotlib, seaborn

## License

MIT

