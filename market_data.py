# This module provides functions to fetch and process market data using yfinance.
# It includes utilities to get historical close prices, estimate volatility, compute correlation matrices,
# and aggregate all relevant market data for a set of tickers.

import yfinance as yf
import numpy as np
import pandas as pd
import datetime


import yfinance as yf
import pandas as pd

import yfinance as yf
from datetime import datetime, timedelta

# Fetches the closing price for a given ticker and date (YYYY-MM-DD)
def get_close_price(ticker, date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    next_day = date + timedelta(days=1)

    data = yf.download(ticker, start=date, end=next_day)

    if data.empty:
        raise ValueError(f"No data for {ticker} on {date_str}")
    
    return data['Close'].iloc[-1].item()

# Estimates annualized volatility for a ticker up to a given end date, using a rolling window (default 252 trading days)
def get_volatility(ticker, end_date, window=252):
    end = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    data = yf.download(ticker, end=end)
    returns = data['Close'].pct_change().dropna()
    volatility = returns[-window:].std() * (252**0.5)
    return volatility.item() 

# Computes the correlation matrix of log returns for a list of tickers over a specified window
def get_correlation_matrix(tickers, window=60, end_date=None):
    try:
        if end_date is not None:
            end = pd.to_datetime(end_date)
            start = end - pd.Timedelta(days=window + 30)
            prices = yf.download(tickers, start=start.strftime('%Y-%m-%d'), 
                                 end=(end + pd.Timedelta(days=1)).strftime('%Y-%m-%d'), 
                                 auto_adjust=True, progress=False)["Close"]
        else:
            prices = yf.download(tickers, period=f"{window + 30}d", 
                                 auto_adjust=True, progress=False)["Close"]

        log_returns = np.log(prices / prices.shift(1)).dropna()
        return log_returns[-window:].corr()
    except Exception as e:
        print(f"Error calculating correlation matrix: {e}")
        return pd.DataFrame()
    

# Aggregates spot prices, volatilities, and correlation matrix for a list of tickers on a given date
def get_all_market_data(tickers, date, window=60):
    spot_prices = {ticker: get_close_price(ticker, date) for ticker in tickers}
    volatilities = {ticker: get_volatility(ticker, window, end_date=date) for ticker in tickers}
    correlation_matrix = get_correlation_matrix(tickers, window, end_date=date)
    return {
        "spot": spot_prices,
        "vol": volatilities,
        "corr": correlation_matrix
    }

