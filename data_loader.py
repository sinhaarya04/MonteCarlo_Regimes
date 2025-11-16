"""
Data loading module for downloading and processing financial market data.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Tuple


def download_price_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """
    Download historical price data for given tickers and compute daily log returns.
    
    Parameters
    ----------
    tickers : List[str]
        List of stock ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
    start : str
        Start date in 'YYYY-MM-DD' format
    end : str
        End date in 'YYYY-MM-DD' format
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns for each ticker's log returns.
        Index is the date range.
    """
    # Download price data
    data = yf.download(tickers, start=start, end=end, progress=False)
    
    # Handle multi-level columns if multiple tickers
    if len(tickers) == 1:
        prices = data['Close'].to_frame()
        prices.columns = tickers
    else:
        prices = data['Close']
    
    # Drop any rows with missing data
    prices = prices.dropna()
    
    # Compute log returns: log(P_t / P_{t-1}) = log(P_t) - log(P_{t-1})
    log_returns = np.log(prices / prices.shift(1)).dropna()
    
    return log_returns


def get_price_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """
    Alias for download_price_data for backward compatibility.
    """
    return download_price_data(tickers, start, end)

