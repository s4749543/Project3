
import yfinance as yf
import numpy as np
import pandas as pd

# gets adjust spot price for a given ticker and date

def get_spot_price(ticker, date_str):
    try:
        date = pd.to_datetime(date_str)
        df = yf.download(
            ticker,
            start=date.strftime('%Y-%m-%d'),
            end=(date + pd.Timedelta(days=1)).strftime('%Y-%m-%d'),
            auto_adjust=True,
            progress=False
        )
        if not df.empty:
            close_price = df.loc[df.index == date, "Close"]
            return float(close_price.iloc[0]) if not close_price.empty else None
        else:
            print(f"No data for {ticker} on {date_str}")
            return None
    except Exception as e:
        print(f"Error retrieving spot price for {ticker} on {date_str}: {e}")
        return None

# gets annualsed historical volatility for a given ticker over the past N days

def get_historical_volatility(ticker, window=60, end_date=None):
    try:
        if end_date is not None:
            end = pd.to_datetime(end_date)
            start = end - pd.Timedelta(days=window + 30)
            data = yf.download(ticker, start=start.strftime('%Y-%m-%d'), 
                               end=(end + pd.Timedelta(days=1)).strftime('%Y-%m-%d'), 
                               auto_adjust=True, progress=False)["Close"]
        else:
            data = yf.download(ticker, period=f"{window + 30}d", 
                               auto_adjust=True, progress=False)["Close"]

        log_returns = np.log(data / data.shift(1)).dropna()
        return log_returns[-window:].std(ddof=0) * np.sqrt(252)  # Population std (ddof=0)
    except Exception as e:
        print(f"Error calculating volatility for {ticker}: {e}")
        return None

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

def get_spot_price(ticker, date_str):
    try:
        date = pd.to_datetime(date_str)
        df = yf.download(ticker, start=date.strftime('%Y-%m-%d'), 
                         end=(date + pd.Timedelta(days=1)).strftime('%Y-%m-%d'), 
                         auto_adjust=True, progress=False)

        if not df.empty and date in df.index:
            return float(df.loc[date]["Close"])
        else:
            print(f"No price data for {ticker} on {date_str}")
            return None
    except Exception as e:
        print(f"Error retrieving spot price for {ticker} on {date_str}: {e}")
        return None

def get_all_market_data(tickers, date, window=60):
    spot_prices = {ticker: get_spot_price(ticker, date) for ticker in tickers}
    volatilities = {ticker: get_historical_volatility(ticker, window, end_date=date) for ticker in tickers}
    correlation_matrix = get_correlation_matrix(tickers, window, end_date=date)
    return {
        "spot": spot_prices,
        "vol": volatilities,
        "corr": correlation_matrix
    }

# Example usage
hv_bhp = get_historical_volatility("BHP.AX", window=60, end_date="2023-10-01")
print(hv_bhp)
