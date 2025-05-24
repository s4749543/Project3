
import yfinance as yf
import numpy as np
import pandas as pd

# gets adjust spot price for a given ticker and date
def get_spot_price(ticker, date):
    data = yf.download(ticker, start=date, end=date)
    return float(data["Adj Close"].iloc[0])


# gets annualsed historical volatility for a given ticker over the past N days
def get_historical_volatility(ticker, window=60):
    """
    Gets the annualized historical volatility over the past N days.
    """
    data = yf.download(ticker, period=f"{window + 30}d")["Adj Close"]
    log_returns = np.log(data / data.shift(1)).dropna()
    return np.std(log_returns[-window:]) * np.sqrt(252)


# gets the correlation matrix for a list of tickers over the past N days
def get_correlation_matrix(tickers, window=60):
    prices = yf.download(tickers, period=f"{window + 30}d")["Adj Close"]
    log_returns = np.log(prices / prices.shift(1)).dropna()
    return log_returns[-window:].corr()

#returns a dictionary with spot prices, volatilities and correlation matrix for a list of tickers
def get_all_market_data(tickers, date, window=60):
    spot_prices = {ticker: get_spot_price(ticker, date) for ticker in tickers}
    volatilities = {ticker: get_historical_volatility(ticker, window) for ticker in tickers}
    correlation_matrix = get_correlation_matrix(tickers, window)
    
    return {
        "spot": spot_prices,
        "vol": volatilities,
        "corr": correlation_matrix
    }